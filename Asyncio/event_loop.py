# using selectors
# ref: PyCon 2015 - David Beazley

import asyncio
import socket
import selectors
from collections import deque


@asyncio.coroutine
def read_wait(s):
    yield 'read_wait', s


@asyncio.coroutine
def write_wait(s):
    yield 'write_wait', s


class Loop:
    """Simple loop prototype"""

    def __init__(self):
        self.ready = deque()
        self.selector = selectors.DefaultSelector()

    async def sock_accept(self, s):
        await read_wait(s)
        return s.accept()

    async def sock_recv(self, c, mb):
        await read_wait(c)
        return c.recv(mb)

    async def sock_sendall(self, c, m):
        while m:
            await write_wait(c)
            nsent = c.send(m)
            m = m[nsent:]

    def create_task(self, coro):
        self.ready.append(coro)

    def run_forever(self):
        while True:
            self._run_once()

    def _run_once(self):
        while not self.ready:
            events = self.selector.select()
            for k, _ in events:
                self.ready.append(k.data)
                self.selector.unregister(k.fileobj)

        while self.ready:
            self.cur_t = self.ready.popleft()
            try:
                op, *a = self.cur_t.send(None)
                getattr(self, op)(*a)
            except StopIteration:
                pass

    def read_wait(self, s):
        self.selector.register(s, selectors.EVENT_READ, self.cur_t)

    def write_wait(self, s):
        self.selector.register(s, selectors.EVENT_WRITE, self.cur_t)


loop = Loop()
host = 'localhost'
port = 5566
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setblocking(False)
s.bind((host, port))
s.listen(10)


async def handler(c):
    while True:
        msg = await loop.sock_recv(c, 1024)
        if not msg:
            break
        await loop.sock_sendall(c, msg)
    c.close()


async def server():
    while True:
        c, addr = await loop.sock_accept(s)
        loop.create_task(handler(c))


loop.create_task(server())
loop.run_forever()

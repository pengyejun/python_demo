import select
import threading
import time
from threading import local
from collections import deque
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET


_RUNNING_LOOP = local()


def get_event_loop() -> "EventLoop":
    if getattr(_RUNNING_LOOP, "__loop", None) is None:
        _RUNNING_LOOP.__loop = EventLoop()
    print(id(_RUNNING_LOOP.__loop))
    return _RUNNING_LOOP.__loop


class Future:
    def __init__(self, loop: "EventLoop" = None):
        if loop is None:
            loop = get_event_loop()
        self.loop = loop
        self.done = False
        self.result = None
        self.co = None

    def set_result(self, result):
        self.done = True
        self.result = result

        if self.co:
            self.loop.add_coroutine(self.co)

    def set_coroutine(self, co):
        self.co = co

    def __await__(self):
        if not self.done:
            yield self
        return self.result


class EventLoop:

    def __init__(self):
        self.epoll = select.epoll()

        self.runnables = deque()
        self.handlers = dict()

    def create_future(self):
        return Future(loop=self)

    def create_listen_socket(self, bind_addr, bind_port, backlogs: int = 2):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((bind_addr, bind_port))
        sock.listen(backlogs)
        return AsyncSocket(sock, self)

    def register_for_polling(self, fd: int, events, handler):
        print(f"register fd={fd} for events {events}")
        self.handlers[fd] = handler
        self.epoll.register(fd, events)

    def unregister_from_polling(self, fd: int):
        print(f"unregister fd={fd}")
        self.epoll.unregister(fd)
        self.handlers.pop(fd)

    def add_coroutine(self, co):
        self.runnables.append(co)

    def run_coroutine(self, co):
        try:
            future = co.send(None)
            future.set_coroutine(co)
        except StopIteration as e:
            print(f"coroutine {co.__name__} stopped")

    def schedule_runnable_coroutines(self):
        while self.runnables:
            self.run_coroutine(co=self.runnables.popleft())

    def run_forever(self):
        while True:
            self.schedule_runnable_coroutines()

            events = self.epoll.poll(1)
            for fd, event in events:
                handler = self.handlers.get(fd)
                if handler:
                    handler(fd, events)


class AsyncSocket:
    def __init__(self, sock: socket, loop: EventLoop):
        sock.setblocking(False)
        self.sock: socket = sock
        self.loop = loop

    def fd(self):
        return self.sock.fileno()

    def create_future_for_events(self, events):
        future = self.loop.create_future()

        def handler(fd, active_events):
            self.loop.unregister_from_polling(fd)
            future.set_result(active_events)

        self.loop.register_for_polling(self.fd(), events, handler)
        return future

    async def accept(self):
        while True:
            try:
                sock, addr = self.sock.accept()
                return AsyncSocket(sock=sock, loop=self.loop), addr
            except BlockingIOError:
                future = self.create_future_for_events(select.EPOLLIN)
                await future

    async def recv(self, bufsize):
        while True:
            try:
                return self.sock.recv(bufsize)
            except BlockingIOError:
                future = self.create_future_for_events(select.EPOLLIN)
                await future

    async def send(self, data):
        while True:
            try:
                return self.sock.send(data)
            except BlockingIOError:
                future = self.create_future_for_events(select.EPOLLOUT)
                await future


class TcpServer:

    def __init__(self, loop=None, bind_addr="0.0.0.0", bind_port=55555):
        if loop is None:
            loop = get_event_loop()
        self.loop = loop
        self.listen_sock = self.loop.create_listen_socket(bind_addr=bind_addr, bind_port=bind_port)
        self.loop.add_coroutine(self.serve_forever())

    async def serve_client(self, sock: AsyncSocket):
        while True:
            data = await sock.recv(1024)
            if not data:
                print("client disconnected")
                break

            await sock.send(data.upper())

    async def serve_forever(self):
        while True:
            sock, (addr, port) = await self.listen_sock.accept()
            print(f"client connected addr={addr} port={port}")

            self.loop.add_coroutine(self.serve_client(sock))


if __name__ == "__main__":
    _loop = get_event_loop()
    server = TcpServer()
    server1 = TcpServer(bind_port=55556)
    _loop.run_forever()

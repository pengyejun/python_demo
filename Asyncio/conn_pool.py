import asyncio
import socket
import uuid


class Transport:

    def __init__(self, loop, host, port):
        self.used = False

        self._loop = loop
        self._host = host
        self._port = port
        self._sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._uuid = uuid.uuid1()

    async def connect(self):
        loop, sock = self._loop, self._sock
        host, port = self._host, self._port
        return await loop.sock_connect(sock, (host, port))

    async def sendall(self, msg):
        loop, sock = self._loop, self._sock
        return await loop.sock_sendall(sock, msg)

    async def recv(self, buf_size):
        loop, sock = self._loop, self._sock
        return await loop.sock_recv(sock, buf_size)

    def close(self):
        if self._sock:
            self._sock.close()

    @property
    def alive(self):
        ret = True if self._sock else False
        return ret

    @property
    def uuid(self):
        return self._uuid


class ConnectionPool:

    def __init__(self, loop, host, port, max_conn=3):
        self._host = host
        self._port = port
        self._max_conn = max_conn
        self._loop = loop

        conns = [Transport(loop, host, port) for _ in range(max_conn)]
        self._conns = conns

    def __await__(self):
        for _c in self._conns:
            yield from _c.connect().__await__()
        return self

    def getconn(self, fut=None):
        if fut is None:
            fut = self._loop.create_future()

        for _c in self._conns:
            if _c.alive and not _c.used:
                _c.used = True
                fut.set_result(_c)
                break
        else:
            loop.call_soon(self.getconn, fut)

        return fut

    def release(self, conn):
        if not conn.used:
            return
        for _c in self._conns:
            if _c.uuid != conn.uuid:
                continue
            _c.used = False
            break

    def close(self):
        for _c in self._conns:
            _c.close()


async def handler(pool, msg):
    conn = await pool.getconn()
    byte = await conn.sendall(msg)
    mesg = await conn.recv(1024)
    pool.release(conn)
    return 'echo: {}'.format(mesg)


async def main(loop, host, port):
    # creat connection pool
    pool = await ConnectionPool(loop, host, port)
    try:

        # generate messages
        msgs = ('coro_{}'.format(_).encode('utf-8') for _ in range(5))

        # create tasks
        fs = [loop.create_task(handler(pool, _m)) for _m in msgs]

        # wait all tasks done
        done, pending = await asyncio.wait(fs)
        for _ in done:
            print(_.result())
    finally:
        pool.close()


loop = asyncio.get_event_loop()
host = '127.0.0.1'
port = 5566

try:
    loop.run_until_complete(main(loop, host, port))
except KeyboardInterrupt:
    pass
finally:
    loop.close()

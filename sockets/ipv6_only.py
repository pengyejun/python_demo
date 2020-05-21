import contextlib
import socket

host = "::"
port = 5566


@contextlib.contextmanager
def server(_host: str, _port: int):
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        s.bind((_host, _port))
        s.listen(10)
        yield s
    finally:
        s.close()


with server(host, port) as s:
    try:
        while True:
            conn, addr = s.accept()
            remote = conn.getpeername()
            print(remote)
            msg = conn.recv(1024)

            if msg:
                conn.send(msg)
            conn.close()
    except KeyboardInterrupt:
        pass

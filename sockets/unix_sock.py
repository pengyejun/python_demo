import socket
import contextlib
import os


@contextlib.contextmanager
def domain_server(addr):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        if os.path.exists(addr):
            os.unlink(addr)
        sock.bind(addr)
        sock.listen(10)
        yield sock

    finally:
        sock.close()


addr = "./domain.sock"

with domain_server(addr) as s:
    while True:
        conn, _ = s.accept()
        msg = conn.recv(1024)
        print(msg)
        conn.send(msg)
        conn.close()

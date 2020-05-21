import socket


class Server(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def __enter__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._host, self._port))
        sock.listen(10)
        self._sock = sock
        return self._sock

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            import traceback
            traceback.print_exception(exc_type, exc_val, exc_tb)
        self._sock.close()


if __name__ == "__main__":
    host = "localhost"
    port = 5566
    with Server(host, port) as s:
        while True:
            conn, addr = s.accept()
            msg = conn.recv(1024)
            conn.send(msg)
            conn.close()

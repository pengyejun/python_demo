import socket


class UDPServer(object):
    def __init__(self, _host, _port):
        self._host = _host
        self._port = _port

    def __enter__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self._host, self._port))
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
    with UDPServer(host, port) as s:
        while True:
            msg, addr = s.recvfrom(1024)
            print(msg, addr)
            s.sendto(msg, addr)

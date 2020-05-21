import socket
from threading import Thread


def work(conn):
    while True:
        msg = conn.recv(1024)
        conn.send(msg)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("localhost", 5566))
sock.listen(5)

while True:
    conn, addr = sock.accept()
    t = Thread(target=work, args=(conn, ))
    t.daemon = True
    t.start()

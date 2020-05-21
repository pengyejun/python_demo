import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = ("localhost", 5566)

while True:
    sock.sendto(b"Hello\n", host)
    time.sleep(5)
import socket
import os
import time

c_s, p_s = socket.socketpair()
try:
    pid = os.fork()
except OSError:
    print("Fork Error")
    raise

if pid:
    # parent process
    c_s.close()
    while True:
        p_s.sendall(b"Hi! Child!")
        msg = p_s.recv(1024)
        print(msg)
        time.sleep(3)
    os.wait()
else:
    # child process
    p_s.close()
    while True:
        msg = c_s.recv(1024)
        print(msg)
        c_s.sendall(b"Hi! Parent!")
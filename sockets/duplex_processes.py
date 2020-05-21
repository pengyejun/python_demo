import os
import socket

child, parent = socket.socketpair()
pid = os.fork()

try:
    if pid == 0:
        print(f"child pid: {os.getpid()}")
        child.send(b"Hello 1")
        msg = child.recv(1024)
        print(f"p:{os.getppid()}, c:{os.getpid()}, {msg}")
    else:
        print(f"parent pid: {os.getpid()}")
        msg = parent.recv(1024)
        print(f"c:{pid} ---> p:{os.getpid()}, {msg}")
        parent.send(msg)
except KeyboardInterrupt:
    pass
finally:
    child.close()
    parent.close()

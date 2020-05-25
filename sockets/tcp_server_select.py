import socket
from select import select

host = ("localhost", 5566)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(host)
sock.listen(5)
rl = [sock]
wl = []
ml = {}
try:
    while True:
        _rl, _wl, _ = select(rl, wl, [])
        for r in _rl:
            if r == sock:
                conn, addr = sock.accept()
                rl.append(conn)
            else:
                msg = r.recv(1024)
                ml[r.fileno()] = msg
                wl.append(r)
        for w in _wl:
            msg = ml[w.fileno()]
            w.send(msg)
            wl.remove(w)
            del ml[w.fileno()]
except:
    sock.close()

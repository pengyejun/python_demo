from __future__ import print_function, unicode_literals

import socket
import select
import contextlib

if not hasattr(select, 'kqueue'):
    print("Not support kqueue")
    exit(1)


host = 'localhost'
port = 5566

con = {}
req = {}
resp = {}

@contextlib.contextmanager
def Server(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind((host, port))
        s.listen(10)
        yield s
    except socket.error:
        print("Get socket error")
        raise
    finally:
        if s: s.close()


@contextlib.contextmanager
def Kqueue():
    try:
        kq = select.kqueue()
        yield kq
    finally:
        kq.close()
        for fd, c in con.items(): c.close()


def accept(server, kq):
    conn, addr = server.accept()
    conn.setblocking(False)
    fd = conn.fileno()
    ke = select.kevent(conn.fileno(),
                       select.KQ_FILTER_READ,
                       select.KQ_EV_ADD)
    kq.control([ke], 0)
    req[fd] = conn
    con[fd] = conn


def recv(fd, kq):
    if fd not in req:
        return

    conn = req[fd]
    msg = conn.recv(1024)
    if msg:
        resp[fd] = msg
        # remove read event
        ke = select.kevent(fd,
                           select.KQ_FILTER_READ,
                           select.KQ_EV_DELETE)
        kq.control([ke], 0)
        # add write event
        ke = select.kevent(fd,
                           select.KQ_FILTER_WRITE,
                           select.KQ_EV_ADD)
        kq.control([ke], 0)
        req[fd] = conn
        con[fd] = conn
    else:
        conn.close()
        del con[fd]

    del req[fd]


def send(fd, kq):
    if fd not in resp:
        return

    conn = con[fd]
    msg = resp[fd]
    b = 0
    total = len(msg)
    while total > b:
        l = conn.send(msg)
        msg = msg[l:]
        b += l

    del resp[fd]
    req[fd] = conn
    # remove write event
    ke = select.kevent(fd,
                       select.KQ_FILTER_WRITE,
                       select.KQ_EV_DELETE)
    kq.control([ke], 0)
    # add read event
    ke = select.kevent(fd,
                       select.KQ_FILTER_READ,
                       select.KQ_EV_ADD)
    kq.control([ke], 0)


try:
    with Server(host, port) as server, Kqueue() as kq:

        max_events = 1024
        timeout = 1

        ke = select.kevent(server.fileno(),
                           select.KQ_FILTER_READ,
                           select.KQ_EV_ADD)

        kq.control([ke], 0)
        while True:
            events = kq.control(None, max_events, timeout)
            for e in events:
                fd = e.ident
                if fd == server.fileno():
                    accept(server, kq)
                elif e.filter == select.KQ_FILTER_READ:
                    recv(fd, kq)
                elif e.filter == select.KQ_FILTER_WRITE:
                    send(fd, kq)
except KeyboardInterrupt:
    pass
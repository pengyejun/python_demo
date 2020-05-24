import socket
import hashlib
import contextlib


@contextlib.contextmanager
def create_alg(typ, name):
    s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
    try:
        s.bind((typ, name))
        yield s

    finally:
        s.close()


msg = b"Python is awesome"

with create_alg('hash', 'sha256') as algo:
    op, _ = algo.accept()
    with op:
        op.sendall(msg)
        data = op.recv(512)
        print(data.hex())

        h = hashlib.sha256(msg).digest()
        if h != data:
            raise Exception(f"sha256({h}) != af_alg({data})")

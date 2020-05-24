# need python 3.6 or above & Linux >=4.3
import contextlib
import socket
import os

BS = 16  # Bytes


def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode('utf-8')


def upad(s): return s[0:-s[-1]]


@contextlib.contextmanager
def create_alg(typ, name):
    s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
    try:
        s.bind((typ, name))
        yield s
    finally:
        s.close()


def encrypt(plaintext, key, iv):
    with create_alg('skcipher', 'cbc(aes)') as algo:
        algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, key)
        op, _ = algo.accept()
        with op:
            plaintext = pad(plaintext)
            op.sendmsg_afalg([plaintext],
                             op=socket.ALG_OP_ENCRYPT,
                             iv=iv)
            ciphertext = op.recv(len(plaintext))

    return ciphertext


def decrypt(ciphertext, key, iv):
    with create_alg('skcipher', 'cbc(aes)') as algo:
        algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, key)
        op, _ = algo.accept()
        with op:
            op.sendmsg_afalg([ciphertext],
                             op=socket.ALG_OP_DECRYPT,
                             iv=iv)
            plaintext = op.recv(len(ciphertext))

    return upad(plaintext)


key = os.urandom(32)
iv = os.urandom(16)

plaintext = b"Demo AF_ALG"
ciphertext = encrypt(plaintext, key, iv)
plaintext = decrypt(ciphertext, key, iv)

print(ciphertext.hex())
print(plaintext)

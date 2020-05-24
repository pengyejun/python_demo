# need python 3.6 or above & Linux >=4.9
import contextlib
import socket
import sys
import os


@contextlib.contextmanager
def create_alg(typ, name):
    s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
    try:
        s.bind((typ, name))
        yield s
    finally:
        s.close()


def encrypt(key, iv, assoc, taglen, pfile):
    assoclen = len(assoc)

    pfd = pfile.fileno()
    offset = 0
    st = os.fstat(pfd)
    totalbytes = st.st_size

    with create_alg('aead', 'gcm(aes)') as algo:
        algo.setsockopt(socket.SOL_ALG,
                        socket.ALG_SET_KEY, key)
        algo.setsockopt(socket.SOL_ALG,
                        socket.ALG_SET_AEAD_AUTHSIZE,
                        None,
                        assoclen)

        op, _ = algo.accept()
        with op:
            op.sendmsg_afalg(op=socket.ALG_OP_ENCRYPT,
                             iv=iv,
                             assoclen=assoclen,
                             flags=socket.MSG_MORE)

            op.sendall(assoc, socket.MSG_MORE)

            # using sendfile to encrypt file data
            os.sendfile(op.fileno(), pfd, offset, totalbytes)

            res = op.recv(assoclen + totalbytes + taglen)
            ciphertext = res[assoclen:-taglen]
            tag = res[-taglen:]

    return ciphertext, tag


def decrypt(key, iv, assoc, tag, ciphertext):
    assoclen = len(assoc)

    with create_alg('aead', 'gcm(aes)') as algo:
        algo.setsockopt(socket.SOL_ALG,
                        socket.ALG_SET_KEY, key)
        algo.setsockopt(socket.SOL_ALG,
                        socket.ALG_SET_AEAD_AUTHSIZE,
                        None,
                        assoclen)
        op, _ = algo.accept()
        with op:
            msg = assoc + ciphertext + tag
            op.sendmsg_afalg([msg],
                             op=socket.ALG_OP_DECRYPT, iv=iv,
                             assoclen=assoclen)

            taglen = len(tag)
            res = op.recv(len(msg) - taglen)
            plaintext = res[assoclen:]

    return plaintext


key = os.urandom(16)
iv = os.urandom(12)
assoc = os.urandom(16)

if len(sys.argv) != 2:
    print("usage: cmd plain")
    exit(1)

plain = sys.argv[1]

with open(plain, 'r') as pf:
    ciphertext, tag = encrypt(key, iv, assoc, 16, pf)
    plaintext = decrypt(key, iv, assoc, tag, ciphertext)

    print(ciphertext.hex())
    print(plaintext)

import asyncio
import ssl


def make_header():
    head = b"HTTP/1.1 200 OK\r\n"
    head += b"Content-Type: text/html\r\n"
    head += b"\r\n"
    return head


def make_body():
    resp = b"<html>"
    resp += b"<h1>Hello SSL</h1>"
    resp += b"</html>"
    return resp


sslctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
sslctx.load_cert_chain(
    certfile="cert/root-ca.crt", keyfile="cert/root-ca.key"
)


class Service(asyncio.Protocol):
    def connection_made(self, tr):
        self.tr = tr
        self.total = 0

    def data_received(self, data):
        if data:
            resp = make_header()
            resp += make_body()
            self.tr.write(resp)
        self.tr.close()


async def start():
    server = await loop.create_server(
        Service, "localhost", 5566, ssl=sslctx
    )
    await server.wait_closed()


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
finally:
    loop.close()
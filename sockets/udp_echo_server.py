import socketserver


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        m, s = self.request
        s.sendto(m, self.client_address)
        print(self.client_address)


host = ("localhost", 5566)
s = socketserver.UDPServer(host, Handler)
s.serve_forever()

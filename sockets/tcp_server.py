import socketserver
import time


class Hanlder(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        time.sleep(10)
        print(self.client_address)
        self.request.sendall(data)


host = ("localhost", 5566)
s = socketserver.TCPServer(host, Hanlder)
s.serve_forever()

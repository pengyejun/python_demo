import socket
import struct

# ref: IP protocol numbers
PROTO_MAP = {
    1: "ICMP",
    2: "IGMP",
    6: "TCP",
    17: "UDP",
    27: "RDP"}

import ctypes

class ifreq(ctypes.Structure):
    _fields_ = [("ifr_ifrn", ctypes.c_char * 16),
                ("ifr_flags", ctypes.c_short)]

IFF_PROMISC = 0x100
SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
ifr = ifreq()
ifr.ifr_ifrn = b"wlp0s20f3"

f = open("./ip_log.txt", "w")


class log:

    def __call__(self, *args, **kwargs):
        for arg in args:
            f.write(arg + "\n")
        f.flush()


print = log()


class IP(object):
    ''' IP header Structure

    strcut ip {
        u_char         ip_v:4;  /* version */         4bit
        u_char         ip_hl:4; /* header_len */      1 byte
        u_char         ip_tos;  /* type of service */ 2 byte
        short          ip_len;  /* total len */       4 byte
        u_short        ip_id;   /* identification */  6 byte
        short          ip_off;  /* offset field */    8 byte
        u_char         ip_ttl;  /* time to live */    9 byte
        u_char         ip_p;    /* protocol */        10 byte
        u_short        ip_sum;  /* checksum */        12 byte
        struct in_addr ip_src;  /* source */          16 byte
        struct in_addr ip_dst;  /* destination */     20 byte
    };
    https://blog.csdn.net/audience_fzn/article/details/81269581
    '''

    def __init__(self, buf=None):
        line1 = struct.unpack(">BBH", buf[:4])
        line2 = struct.unpack(">HH", buf[4:8])
        line3 = struct.unpack(">BBH", buf[8:12])
        line4 = struct.unpack(">4s", buf[12:16])
        line5 = struct.unpack(">4s", buf[16:20])
        self.ip_v = line1[0] >> 4
        self.ip_hl = line1[0] & 15
        self.ip_tos = line1[1]
        self.ip_len = line1[2]
        self.ip_id = line2[0]
        self.ip_offtag = line2[1] >> 13
        self.ip_offset = line2[1] & pow(2, 14) - 1
        self.ip_ttl = line3[0]
        self.ip_proto = PROTO_MAP[line3[1]]
        self.ip_sum = line3[2]
        self.ip_src = socket.inet_ntoa(line4[0])
        self.ip_dst = socket.inet_ntoa(line5[0])


host = '0.0.0.0'
s = socket.socket(socket.AF_INET,
                  socket.SOCK_RAW,
                  socket.IPPROTO_TCP)
import fcntl

fcntl.ioctl(s.fileno(), SIOCGIFFLAGS, ifr) # G for Get

ifr.ifr_flags |= IFF_PROMISC
fcntl.ioctl(s.fileno(), SIOCSIFFLAGS, ifr) # S for Set
s.bind((host, 8888))

print("hello")
print("Sniffer start...")
try:
    while True:
        buf, addr = s.recvfrom(65535)
        ip_header = IP(buf[:20])
        for k, v in vars(ip_header).items():
            if k.startswith("ip"):
                print(f"{k}:  {v}")
except KeyboardInterrupt:
    s.close()

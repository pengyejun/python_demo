from __future__ import print_function, unicode_literals

import os
import sys

if len(sys.argv) != 3:
    print("Usage: cmd src dst")
    exit(1)

src = sys.argv[1]
dst = sys.argv[2]

with open(src, 'r') as s, open(dst, 'w') as d:
    st = os.fstat(s.fileno())

    offset = 0
    count = 4096
    s_len = st.st_size

    sfd = s.fileno()
    dfd = d.fileno()

    while s_len > 0:
        ret = os.sendfile(dfd, sfd, offset, count)
        offset += ret
        s_len -= ret






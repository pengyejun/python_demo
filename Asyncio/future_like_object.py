import sys
import asyncio

PY_35 = sys.version_info >= (3, 5)

loop = asyncio.get_event_loop()


class SlowObj(object):
    def __init__(self, n):
        self.n = n

    if PY_35:
        def __await__(self):
            print(f"__await__ sleep {self.n}")
            yield from asyncio.sleep(self.n).__await__()
            print("sleep ok")
            return self


async def main():
    obj = await SlowObj(2)

loop.run_until_complete(main())

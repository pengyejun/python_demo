import asyncio
import sys
PY_35 = sys.version_info >= (3, 5)
loop = asyncio.get_event_loop()


async def slow_task(n):
    print("task sleep")
    await asyncio.sleep(n)


class SlowObj(object):
    def __init__(self, n):
        self.n = n

    if PY_35:
        def __await__(self):
            print(f"__await__ sleep {self.n}")
            yield from asyncio.sleep(self.n).__await__()
            yield from slow_task(self.n).__await__()
            print("sleep ok")
            return self


async def main(n):
    ret = await SlowObj(n)

loop.run_until_complete(main(1))

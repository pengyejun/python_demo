import asyncio
from contextlib import asynccontextmanager


class AsyncCtxMgr:

    async def __aenter__(self):
        await asyncio.sleep(1)
        print("__aenter__")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(1)

        print("__aexit__")


async def hello():
    async with AsyncCtxMgr() as m:
        print("hello")


async def world():
    print("world")


asyncio.get_event_loop().run_until_complete(asyncio.gather(hello(), world()))

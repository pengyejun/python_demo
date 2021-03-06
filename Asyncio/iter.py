import asyncio


class AsyncIter:
    def __init__(self, it):
        self.it = iter(it)

    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(1)

        try:
            val = next(self.it)
        except StopIteration:
            raise StopAsyncIteration

        return val


async def foo():
    it = [1, 2, 3]
    async for _ in AsyncIter(it):
        print(_)


asyncio.run(foo())

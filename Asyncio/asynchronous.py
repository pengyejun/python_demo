import asyncio


class AsyncIter:
    def __init__(self, it):
        self.it = it.__iter__()

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
    _ = [1, 2, 3]
    it = AsyncIter(_)
    running = True

    while running:
        try:
            res = await it.__anext__()
            print(res)
        except StopAsyncIteration:
            running = False

asyncio.run(foo())
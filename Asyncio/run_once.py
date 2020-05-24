import asyncio


def _run_once(self):
    num_task = len(self._scheduled)
    print(f"num tasks in queue: {num_task}")
    super(asyncio.SelectorEventLoop, self)._run_once()


EventLoop = asyncio.SelectorEventLoop
EventLoop._run_once = _run_once
loop = EventLoop()
asyncio.set_event_loop(loop)


async def task(n):
    await asyncio.sleep(n)
    print(f"sleep in {n}")


async def hello():
    while True:
        print(123)
        await asyncio.sleep(2)

asyncio.ensure_future(hello())
coro = loop.create_task(task(30))
loop.run_until_complete(coro)

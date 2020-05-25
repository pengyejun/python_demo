import asyncio


@asyncio.coroutine
def hello():
    yield 1


async def main():
    await asyncio.sleep(2)

    print(await hello())
    print("exit")


asyncio.run(main())

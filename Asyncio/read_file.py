import asyncio
from concurrent.futures import ThreadPoolExecutor

e = ThreadPoolExecutor()
loop = asyncio.get_event_loop()


async def read_file(_file):
    with open(_file, "r") as f:
        return await loop.run_in_executor(e, f.read)


coro = loop.create_task(read_file("/etc/passwd"))
ret = loop.run_until_complete(coro)
print(ret)

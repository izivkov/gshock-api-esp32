import uasyncio as asyncio

async def tick():
    while True:
        print("tick")
        await asyncio.sleep(1)  # sleep 1 second non-blocking

async def main():
    asyncio.create_task(tick())
    while True:
        print("tock")
        await asyncio.sleep(2)

asyncio.run(main())

import uasyncio as asyncio
from machine import Pin
import config_server
import gshock_server
from lib.config.config_manager import config_manager
import gc

server_task = None
boot_button = Pin(9, Pin.IN, Pin.PULL_UP)  # BOOT: usually HIGH

async def watch_boot_button(callback):
    while True:
        if boot_button.value() == 0:  # Button pressed (active low)
            print("Boot button pressed...")
            await asyncio.sleep_ms(20)  # Debounce
            if boot_button.value() == 0:
                await callback()
                while boot_button.value() == 0:  # Wait until button released
                    await asyncio.sleep_ms(20)
        await asyncio.sleep_ms(50)

async def start_config_mode():
    global server_task
    print("Switching to config mode!")
    if server_task:
        server_task.cancel()
        try:
            await server_task
        except:  # Ignore cancellation exception
            pass
    server_task = asyncio.create_task(config_server.main())


async def main():
    global server_task

    config_manager.load()
    
    if not config_manager.get("ssid") or not config_manager.get("password"):
        print("Missing config: starting config server")
        await asyncio.sleep(3)
        server_task = asyncio.create_task(config_server.main())
    else:
        print("Config found: starting gshock server")
        server_task = asyncio.create_task(gshock_server.main())

    watcher_task = asyncio.create_task(watch_boot_button(start_config_mode))

    # Run all concurrently
    await asyncio.gather(server_task, watcher_task)

asyncio.run(main())


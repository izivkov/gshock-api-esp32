import uasyncio as asyncio
from machine import Pin
import config_server
import gshock_server
from lib.config.config_manager import config_manager
import gc

from di import display
from lib.display.touch import touch
from lib.display.dim_display import DimDisplay
import utime as time
from lib.utils.periodic_task_runner import PeriodicTaskRunner
import lib.utils.utils as utils
from gshock_api.logger import logger

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

        await init()
        server_task = asyncio.create_task(gshock_server.main())

    watcher_task = asyncio.create_task(watch_boot_button(start_config_mode))

    # Run all concurrently
    await asyncio.gather(server_task, watcher_task)

# Starting support processes...
async def init():

    set_colors()
    display.show_message("Starting...")

    await start_time_setter()
    await start_dimmer()

async def start_time_setter():
    time_task = PeriodicTaskRunner(set_server_time, interval_sec=6*60*60, run_immediately=True)
    await time_task.start(block_until_first_run=True)

    display.show_message(f"Time on Server: {utils.format_time(time.localtime())}")
    gc.collect()
    time.sleep(2)

def set_server_time():
    try:
        ssid = config_manager.get("ssid")
        password = config_manager.get("password")
        timezone = config_manager.get("timezone", "UTC")

        from lib.config.network_time_setter import network_time_setter
        time_set = network_time_setter.set_time(ssid, password, timezone)
        if not time_set:
            display.show_message (f"""Failed to set time using WiFi "{ssid}". Please check config and connection.""")
            logger.error(f"gshock_server: Failed to set time using WiFi \"{ssid}\". Please check config and connection.")
            return False
        else:
            return True

    except Exception as e:
        return False
    
    finally:
        network_time_setter.cleanup()

async def start_dimmer():
    dim_display = DimDisplay(display, touch)
    dim_display.start()
    gc.collect()

def set_colors():
    display_fg_color = config_manager.get("foreground_color", "15130857")
    display_bg_color = config_manager.get("background_color", "1315352")

    fg = display.decimal_to_rgb(int(display_fg_color))
    bg = display.decimal_to_rgb(int(display_bg_color))
    display.set_colors(fg, bg)
    gc.collect()

asyncio.run(main())


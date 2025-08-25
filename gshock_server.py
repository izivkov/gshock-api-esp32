import gc

import uasyncio as asyncio
import utime as time
from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from gshock_api.exceptions import GShockConnectionError, GShockIgnorableException
from lib.config import network_time_setter
from lib.config.config_manager import config_manager
from lib.display.led import led, LEDController
import lib.utils.strings as strings

from lib.display.display import display

from lib.utils.run_once import run_once_key
from lib.utils.persistent_store import store

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"

async def main():        
    config_manager.load()
    
    if not config_manager.get("ssid") or not config_manager.get("password"):
        display.show_message (f"""Configuration file "config.json" missing. Please create and copy to device""")
        logger.error(f" {config_manager.get_instructions()}")
        led.red_on()
        asyncio.sleep(10)
        return

    print(f"Local time: {strings.format_time(time.localtime())}")
    display.show_message(strings.format_time(time.localtime()))
    
    await gshock_server()

def prompt():
    logger.info("==============================================================================================")
    logger.info("Short-press lower-right button on your watch to set time...")
    logger.info("")
    logger.info("If Auto-time set on watch, the watch will connect and run automatically up to 4 times per day.")
    logger.info("==============================================================================================")
    logger.info("")

async def gshock_server():
    excluded_watches = [
        "DW-H5600", "OCW-S400", "OCW-S400SG", "OCW-T200SB",
        "ECB-30", "ECB-20", "ECB-10", "ECB-50", "ECB-60", "ECB-70"
    ]

    prompt()
    display.show_message (f"""Started...""")

    while True:
        try:
            run_once_key(
                "show_welcome_screen",
                display.show_welcome_screen,
                "Waiting for connection...",
                watch_name=store.get("watch_name", None),
                last_sync=store.get("last_connected", None),
            )

            logger.info("Waiting for connection...")
            connection = Connection()

            led.set_mode(LEDController.MODE_BLINK_GREEN)
            connected = await connection.connect(excluded_watches)
            led.set_mode(LEDController.MODE_SMOOTH)

            if not connected:
                logger.info("Connect attempt failed; retrying...")
                await asyncio.sleep(1)
                continue

            gc.collect()
            print("Free memory:", gc.mem_free())

            # Update store
            t = time.localtime()  # returns (year, month, mday, hour, minute, second, weekday, yearday)
            formatted_time = "{:02d}/{:02d} {:02d}:{:02d}".format(t[1], t[2], t[3], t[4])

            store.add("last_connected", formatted_time)
            store.add("watch_name", watch_info.name)

            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()

            # Apply fine adjustment to the time
            # fine_adjustment_secs = args.get().fine_adjustment_secs
            fine_adjustment_secs = 0

            await api.set_time(offset=fine_adjustment_secs)

            now_tuple = time.localtime()
            now_str = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                now_tuple[0], now_tuple[1], now_tuple[2], now_tuple[3], now_tuple[4], now_tuple[5]
            )
            logger.info("Time set at {} on {}".format(now_str, watch_info.name))

            if pressed_button == WatchButton.LOWER_LEFT:
                await show_display(api)
            else:
                display.show_welcome_screen("Waiting for connection...",
                                            watch_name=watch_info.name,
                                            last_sync=formatted_time)

            if watch_info.alwaysConnected == False:
                await connection.disconnect()
                connection = None
                gc.collect()

        except (GShockConnectionError, GShockIgnorableException) as e:
            led.set_mode(LEDController.MODE_BLINK_RED)
            logger.error("Got error: {}".format(e))
            continue

        except Exception as e: # Just in case
            led.set_mode(LEDController.MODE_BLINK_RED)
            logger.error("Unknown error: {}".format(e))
            continue

        finally:
                # Release memory
                gc.collect()

def get_next_alarm_time(alarms):
    now = time.localtime()  # (year, month, mday, hour, minute, second, weekday, yearday)
    now_sec = time.mktime(now)

    times_today = []
    times_tomorrow = []

    for alarm in alarms:
        if not alarm.get("enabled", True):
            continue
        hour = alarm.get("hour")
        minute = alarm.get("minute")
        if not (isinstance(hour, int) and isinstance(minute, int)):
            continue

        # Today’s alarm time
        alarm_today = (now[0], now[1], now[2], hour, minute, 0, 0, 0)
        alarm_today_sec = time.mktime(alarm_today)

        if alarm_today_sec > now_sec:
            times_today.append(alarm_today_sec)
        else:
            # Tomorrow’s alarm time
            alarm_tomorrow = (now[0], now[1], now[2] + 1, hour, minute, 0, 0, 0)
            alarm_tomorrow_sec = time.mktime(alarm_tomorrow)
            times_tomorrow.append(alarm_tomorrow_sec)

    next_alarm_sec = None
    if times_today:
        next_alarm_sec = min(times_today)
    elif times_tomorrow:
        next_alarm_sec = min(times_tomorrow)
    else:
        return None, None

    next_alarm = time.localtime(next_alarm_sec)
    return next_alarm[3], next_alarm[4]  # (hour, minute)

async def show_display(api: GshockAPI):
    try:
        alarms = await api.get_alarms()
        hour, minute = get_next_alarm_time(alarms)
        if hour is not None and minute is not None:
            alarm_str = "{:02}:{:02}".format(hour, minute)
        else:
            alarm_str = "Invalid time"

        condition = await api.get_watch_condition()
        battery = condition.get("battery_level_percent")
        temperature = condition.get("temperature")

        name = watch_info.name
        short_name = ' '.join(name.strip().split()[1:])

        t = time.localtime()
        last_sync = "{:02}/{:02} {:02}:{:02}".format(t[1], t[2], t[3], t[4])

        auto_sync="On" if await api.get_time_adjustment() else "Off"
        print(f"Auto Sync: {auto_sync}")

        reminders = await api.get_reminders()
        reminder_title = reminders[0].get("title") if reminders else "None"

        data = [
        ("", short_name),
        ("Last Sync", last_sync),
        ("TimeZone:", config_manager.get("timezone")),
        ("Next Alarm:", alarm_str),
        ("Rem:", reminder_title),
        ("Auto Sync:", auto_sync)
        ]

        display.display_data(data)
        display.draw_battery_icon(percent=battery)
        display.draw_temperature(temperature=temperature)

    except Exception as e:
        logger.error("Got error: {}".format(e))

    except Exception as e:
        logger.error("Got error: {}".format(e))

if __name__ == "__main__":
    asyncio.run(main())

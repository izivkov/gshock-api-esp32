import gc

import uasyncio as asyncio
import utime as time
from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from gshock_api.exceptions import GShockConnectionError, GShockIgnorableException
from lib.config.config_manager import config_manager
from lib.display.led_mock import led, LEDController
import lib.utils.utils as utils
from lib.utils.periodic_task_runner import PeriodicTaskRunner

from di import display
from lib.display.touch import touch
from lib.display.dim_display import DimDisplay

from lib.utils.run_once import run_once_key
from lib.utils.persistent_store import store

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"

async def main():     
    try:
        gc.collect()

        config_manager.load()
        set_colors()

        display.show_message("Starting...")

        await start_time_setter()
        await start_dimmer()

        await gshock_server()

    except asyncio.CancelledError:
        print("Task was cancelled, cleaning up!")
        # perform any cleanup if needed
        # raise  # always re-raise unless you are sure you want to swallow it
    
async def start_time_setter():
    time_task = PeriodicTaskRunner(set_server_time, interval_sec=86400, run_immediately=True)
    await time_task.start(block_until_first_run=True)

    display.show_message(f"Time on Server: {utils.format_time(time.localtime())}")
    gc.collect()
    time.sleep(2)

async def start_dimmer():
    dim_display = DimDisplay(display, touch)
    dim_display.start()
    gc.collect()

def set_colors():
    display_fg_color = config_manager.get("foreground_color", "15130857")
    display_bg_color = config_manager.get("background_color", "1315352")

    print(f"display_fg_color: {display_fg_color}, display_bg_color: {display_bg_color}")

    fg = display.decimal_to_rgb(int(display_fg_color))
    bg = display.decimal_to_rgb(int(display_bg_color))
    display.set_colors(fg, bg)
    gc.collect()

def prompt():
    logger.info("==============================================================================================")
    logger.info("Short-press lower-right button on your watch to set time...")
    logger.info("")
    logger.info("If Auto-time set on watch, the watch will connect and run automatically up to 4 times per day.")
    logger.info("==============================================================================================")
    logger.info("")

async def gshock_server():

    always_connected_watches = [
        "DW-H5600", "OCW-S400", "OCW-S400SG", "OCW-T200SB",
        "ECB-30", "ECB-20", "ECB-10", "ECB-50", "ECB-60", "ECB-70"
    ]
    
    prompt()

    while True:
        try:
            run_once_key(
                "show_welcome_screen",
                display.show_welcome_screen,
                "Waiting for connection...",
                watch_name=store.get("watch_name", None),
                last_sync=store.get("last_connected", "Unknown"),
            )

            logger.info("Waiting for connection...")
            connection = Connection()

            led.set_mode(LEDController.MODE_BLINK_GREEN)
            connected = await connection.connect(excluded_watches=always_connected_watches)
            led.set_mode(LEDController.MODE_SOLID_GREEN)

            if not connected:
                logger.info("Connect attempt failed; retrying...")
                await asyncio.sleep(1)
                continue

            # Update store
            t = time.localtime()  # (year, month, mday, hour, minute, second, weekday, yearday)
            date_fmt = config_manager.get("dateformat", "MM/DD")
            time_fmt = config_manager.get("timeformat", "24H")
            formatted_time = f'{utils.format_month_day(t, order=date_fmt)} {utils.format_time(t, timeformat=time_fmt)}'

            store.add("last_connected", formatted_time)
            store.add("watch_name", watch_info.name)

            gc.collect()
            api = GshockAPI(connection)

            pressed_button = await api.get_pressed_button()

            # Apply fine adjustment to the time
            fine_adjustment_secs = 0

            await api.set_time(offset=fine_adjustment_secs)

            logger.info(f"Time set at {utils.format_month_day(t, order=date_fmt)} {utils.format_time(t, timeformat=time_fmt)}")

            if pressed_button == WatchButton.LOWER_LEFT:
                await show_display(api)
                pass
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

        except Exception as e:
            led.set_mode(LEDController.MODE_BLINK_RED)
            logger.error("Unknown error: {}".format(e))
            continue

        finally:
            gc.collect()

def set_server_time():
    try:
        ssid = config_manager.get("ssid")
        password = config_manager.get("password")
        timezone = config_manager.get("timezone", "UTC")

        from lib.config.network_time_setter import NetworkTimeSetter
        network_time_setter = NetworkTimeSetter()
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
        timeformat = config_manager.get("timeformat", "24H")
        dateformat = config_manager.get("dateformat", "MM/DD")
        last_sync = f"{utils.format_month_day(t, dateformat)} {utils.format_time(t, timeformat)}"

        auto_sync="On" if await api.get_time_adjustment() else "Off"

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
        display.draw_temperature(temperature=temperature, temperature_unit=config_manager.get("temperature_unit", "C"))

    except Exception as e:
        logger.error("Got error: {}".format(e))

    except Exception as e:
        logger.error("Got error: {}".format(e))

    finally:
        gc.collect()

if __name__ == "__main__":
    asyncio.run(main())

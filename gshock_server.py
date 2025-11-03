import gc

import uasyncio as asyncio
import utime as time
from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from gshock_api.exceptions import GShockConnectionError, GShockIgnorableException, GShockRateRestrictedWatchException
from lib.config.config_manager import config_manager
import lib.utils.utils as utils
from di import display
from lib.utils.run_once import run_once_key
from lib.utils.persistent_store import store
from gshock_api.always_connected_watch_filter import always_connected_watch_filter as watch_filter
from di import led, LEDController
from lib.config.network_time_setter import network_time_setter
from lib.config.log_sender import log_sender
from lib.config.activity_log import activity_log

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"

async def main():     
    try:
        await gshock_server()

    except asyncio.CancelledError:
        print("Task was cancelled, cleaning up!")
        # perform any cleanup if needed
        # raise  # always re-raise unless you are sure you want to swallow it
    
def prompt():
    logger.info("==============================================================================================")
    logger.info("Short-press lower-right button on your watch to set time...")
    logger.info("")
    logger.info("If Auto-time set on watch, the watch will connect and run automatically up to 4 times per day.")
    logger.info("==============================================================================================")
    logger.info("")

async def gshock_server():
    
    prompt()

    while True:
        watch_name = "Unknown"

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

            led.set_mode(LEDController.MODE_PULSATE_GREEN)
            connected, name = await connection.connect(watch_filter.connection_filter)
            print(f"Connection result: {connected}, name: {name}")

            if connected and name == "TimeServerConfigurator":
                # activity_log.get_logs()
                await log_sender.send_logs(connection, activity_log)
                continue

            led.set_mode(LEDController.MODE_SMOOTH)

            if not network_time_setter.is_NTP_set():
                logger.info("Network time not set on device - cannot sync...")
                display.show_message("NTP not set - cannot sync")
                activity_log.add_log(activity_name="Setting Time", status_code="NTP_NOT_SET", message="Network time not set on device - cannot sync")
                await connection.disconnect()
                connection = None
                continue

            if not connected:
                logger.info("Connect attempt failed; retrying...")
                activity_log.add_log(activity_name="Setting Time", status_code="CONNECT_FAILED", message="Failed to connect to watch")                
                await asyncio.sleep(1)
                continue

            # Update store
            t = time.localtime()  # (year, month, mday, hour, minute, second, weekday, yearday)
            date_fmt = config_manager.get("dateformat", "MM/DD")
            time_fmt = config_manager.get("timeformat", "24H")
            formatted_time = f'{utils.format_month_day(t, order=date_fmt)} {utils.format_time(t, timeformat=time_fmt)}'

            watch_name = watch_info.shortName.strip('\u0000 \t\n\r')
            store.add("last_connected", formatted_time)
            store.add("watch_name", watch_name)

            gc.collect()
            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()

            # Apply fine adjustment to the time
            fine_adjustment_secs = 0
            await api.set_time(offset=fine_adjustment_secs)
            logger.info(f"Time set at {utils.format_month_day(t, order=date_fmt)} {utils.format_time(t, timeformat=time_fmt)}")
            set_mode = "AUTO" if pressed_button is WatchButton.NO_BUTTON else "MANUAL" if pressed_button == WatchButton.LOWER_RIGHT else "MANUAL WITH DISPLAY"
            activity_log.add_log(activity_name="Setting Time", status_code="TIME_SET", message=f"Time set on {watch_name}, mode: {set_mode}")

            if pressed_button == WatchButton.LOWER_LEFT:
                await show_display(api)
                pass
            else:
                display.show_welcome_screen("Waiting for connection...",
                                            watch_name=watch_name,
                                            last_sync=formatted_time)

            await connection.disconnect()
            connection = None
            gc.collect()

        except (GShockConnectionError, GShockIgnorableException, GShockRateRestrictedWatchException) as e:
            logger.error("Got Ignorable error: {}".format(e))
            led.set_mode(LEDController.MODE_BLINK_RED)
            # Ignorable, do not set logs
            continue

        except Exception as e:
            logger.error("Unknown error: {}".format(e))
            activity_log.add_log(activity_name="Setting Time", status_code="ERROR", message=f"Failed to set time for {watch_name}: {str(e)}")
            led.set_mode(LEDController.MODE_BLINK_RED)
            continue

        finally:
            gc.collect()
            led.set_mode(LEDController.MODE_BLINK_RED)
            print(f"Activity Log: {activity_log.to_json()}")

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

        short_name = watch_info.shortName
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

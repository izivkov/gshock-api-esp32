import uasyncio as asyncio
import sys
import json
import time

# Import or define minimal stub versions of these for MicroPython
from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.event import Event, create_event_date, RepeatPeriod
from gshock_api.logger import logger  # Replace with print-based logger if unavailable
from gshock_api.app_notification import AppNotification, NotificationType
from gshock_api.exceptions import GShockConnectionError

def prompt():
    print("=" * 70)
    print("Press and hold lower-left button on your watch for 3 seconds to start...")
    print("=" * 70)
    print()

async def run_api_tests(argv):
    excluded_watches = [
        "DW-H5600", "OCW-S400", "OCW-S400SG", "OCW-T200SB",
        "ECB-30", "ECB-20", "ECB-10", "ECB-50", "ECB-60", "ECB-70"
    ]
    prompt()

    try:
        print("Waiting for connection...")
        connection = Connection()
        await connection.connect(excluded_watches)
        print("Connected...")

        api = GshockAPI(connection)

        app_info = await api.get_app_info()
        print("app info:", app_info)

        pressed_button = await api.get_pressed_button()
        print("pressed button:", pressed_button)

        watch_name = await api.get_watch_name()
        print("got watch name:", watch_name)

        await api.set_time(time.time() + 10 * 60)

        alarms = await api.get_alarms()
        print("alarms:", alarms)

        # Modify alarm as example
        if len(alarms) > 3:
            alarms[3]["enabled"] = True
            alarms[3]["hour"] = 7
            alarms[3]["minute"] = 25
            alarms[3]["enabled"] = False
            await api.set_alarms(alarms)

        seconds = await api.get_timer()
        print("timer:", seconds, "seconds")

        await api.set_timer(seconds + 10)
        time_adjustment = await api.get_time_adjustment()
        print("time adjustment:", time_adjustment)

        await api.set_time_adjustment(time_adjustement=True, minutes_after_hour=10)

        condition = await api.get_watch_condition()
        print("condition:", condition)

        settings_local = await api.get_basic_settings()
        print("settings:", settings_local)

        settings_local["button_tone"] = True
        settings_local["language"] = "Russian"
        settings_local["time_format"] = "24h"

        await api.set_settings(settings_local)
        settings_local = await api.get_basic_settings()
        await app_notifications(api)

        # Create a single event (simplified time handling)
        utc_timestamp = time.time()
        event_date = create_event_date(utc_timestamp, None)  # Pass None or minimal tz support
        event_date_str = json.dumps(event_date.__dict__)
        event_json_str = (
            '{"title":"Test Event", "time":{"selected":false, "enabled":true, "repeat_period":'+
            str(RepeatPeriod.WEEKLY) +
            ', "days_of_week":"MONDAY", "start_date":' + event_date_str + ', "end_date":' + event_date_str + '}}'
        )
        Event().create_event(json.loads(event_json_str))
        print("Created event:", event_json_str)

        reminders = await api.get_reminders()
        for reminder in reminders:
            print("reminder:", str(reminder))

        if len(reminders) > 3:
            reminders[3]["title"] = "Test Event"
            await api.set_reminders(reminders)

    except GShockConnectionError as e:
        print("Connection problem:", e) 

    print("Disconnecting...")
    await connection.disconnect()
    print("--- END OF TESTS ---")

async def app_notifications(api):
    calendar_notification = AppNotification(
        type=NotificationType.CALENDAR,
        timestamp="20231001T121000",
        app="Calendar",
        title="This is a very long Meeting with Team",
        text="9:20 - 10:15 AM"
    )
    await api.send_app_notification(calendar_notification)
    # Add other notifications similarly if needed

def convert_time_string_to_epoch(time_string):
    try:
        # MicroPython might lack datetime.strptime, so parse manually or omit
        h, m, s = map(int, time_string.split(':'))
        return h * 3600 + m * 60 + s
    except Exception:
        print("Invalid time format. Please use the format HH:MM:SS.")
        return None

async def main(argv):
    await run_api_tests(argv)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(sys.argv[1:] if len(sys.argv) > 1 else []))
    except KeyboardInterrupt:
        print("Interrupted and exiting")

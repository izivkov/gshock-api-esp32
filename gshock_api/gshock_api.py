import uasyncio as asyncio
import json
import time

# You must port or recreate these for MicroPython environment:
# from gshock_api.iolib.dst_watch_state_io import DtsState
# from gshock_api.iolib.button_pressed_io import WatchButton
# from gshock_api.iolib.app_notification_io import AppNotificationIO
from gshock_api import message_dispatcher
# from gshock_api.utils import to_hex_string, to_compact_string
# from gshock_api.alarms import alarms_inst
# from gshock_api.event import Event
# from gshock_api.watch_info import watch_info

class GshockAPI:
    def __init__(self, connection):
        self.connection = connection

    async def get_watch_name(self):
        result = await message_dispatcher.WatchNameIO.request(self.connection)
        return await result

    async def get_pressed_button(self):
        result = await message_dispatcher.ButtonPressedIO.request(self.connection)
        return await result

    async def get_world_cities(self, city_number):
        city = await message_dispatcher.WorldCitiesIO.request(self.connection, city_number)
        return await city

    async def get_dst_for_world_cities(self, city_number):
        result = await message_dispatcher.DstForWorldCitiesIO.request(self.connection, city_number)
        return await result

    async def get_dst_watch_state(self, state):
        result = await message_dispatcher.DstWatchStateIO.request(self.connection, state)
        return await result

    async def initialize_for_setting_time(self):
        await self.read_write_dst_watch_states()
        await self.read_write_dst_for_world_cities()
        await self.read_write_world_cities()

    async def read_and_write(self, function, param):
        ret = await function(param)
        short_str = to_compact_string(to_hex_string(ret))
        await self.connection.write(0xE, short_str)

    async def read_write_dst_watch_states(self):
        array_of_dst_watch_state = [
            {"function": self.get_dst_watch_state, "state": DtsState.ZERO},
            {"function": self.get_dst_watch_state, "state": DtsState.TWO},
            {"function": self.get_dst_watch_state, "state": DtsState.FOUR},
        ]

        for item in array_of_dst_watch_state[: watch_info.dstCount]:
            await self.read_and_write(item["function"], item["state"])

    async def send_app_notification(self, hex_str):
        await self.connection.write(0xD, hex_str)

    async def read_write_dst_for_world_cities(self):
        array_of_get_dst_for_world_cities = [
            {"function": self.get_dst_for_world_cities, "city_number": i} for i in range(6)
        ]

        for item in array_of_get_dst_for_world_cities[: watch_info.worldCitiesCount]:
            await self.read_and_write(item["function"], item["city_number"])

    async def read_write_world_cities(self):
        array_of_world_cities = [
            {"function": self.get_world_cities, "city_number": i} for i in range(6)
        ]

        for item in array_of_world_cities[: watch_info.worldCitiesCount]:
            await self.read_and_write(item["function"], item["city_number"])

    async def set_time(self, current_time=None, offset=0):
        await self.initialize_for_setting_time()
        await self._set_time(current_time, offset)
        current_time = None

    async def _set_time(self, current_time, offset=0):
        await message_dispatcher.TimeIO.request(self.connection, current_time, offset)

    async def get_alarms(self):
        alarms_inst.clear()
        await self._get_alarms()
        return alarms_inst.alarms

    async def _get_alarms(self):
        result = await message_dispatcher.AlarmsIO.request(self.connection)
        return result

    async def set_alarms(self, alarms):
        if not alarms:
            print("Alarm model not initialised! Cannot set alarm")
            return

        alarms_str = json.dumps(alarms)
        set_action_cmd = '{{"action":"SET_ALARMS", "value":{} }}'.format(alarms_str)
        await self.connection.sendMessage(set_action_cmd)

    async def get_timer(self):
        return await message_dispatcher.TimerIO.request(self.connection)

    async def set_timer(self, timer_value):
        await self.connection.sendMessage(
            """{"action": "SET_TIMER", "value": """ + str(timer_value) + """ }"""
        )

    async def get_watch_condition(self):
        result = await message_dispatcher.WatchConditionIO.request(self.connection)
        return await result

    async def get_time_adjustment(self):
        result = await message_dispatcher.TimeAdjustmentIO.request(self.connection)
        return await result

    async def set_time_adjustment(self, time_adjustement, minutes_after_hour):
        message = f"""{{"action": "SET_TIME_ADJUSTMENT", "timeAdjustment": "{time_adjustement}", "minutesAfterHour": "{minutes_after_hour}" }}"""
        await self.connection.sendMessage(message)

    async def get_basic_settings(self):
        result = await message_dispatcher.SettingsIO.request(self.connection)
        return await result

    async def set_settings(self, settings):
        setting_json = json.dumps(settings)
        await self.connection.sendMessage(
            """{"action": "SET_SETTINGS", "value": """ + setting_json + """ }"""
        )

    async def get_reminders(self):
        reminders = []
        for i in range(1, 6):
            reminders.append(await self.get_event_from_watch(i))
        return reminders

    async def get_event_from_watch(self, event_number):
        result = await message_dispatcher.EventsIO.request(self.connection, event_number)
        return await result

    async def set_reminders(self, events):
        if not events:
            return

        def get_enabled_events(events):
            return [event for event in events if event["time"]["enabled"]]

        enabled = get_enabled_events(events)

        await self.connection.sendMessage(
            """{{\"action\": \"SET_REMINDERS\", \"value\": {}}}""".format(json.dumps(enabled))
        )

    async def get_app_info(self):
        result = await message_dispatcher.AppInfoIO.request(self.connection)
        return await result

    async def send_app_notification(self, notification):
        encoded_buffer = AppNotificationIO.encode_notification_packet(notification)
        encrypted_buffer = AppNotificationIO.xor_encode_buffer(encoded_buffer)
        await self.connection.write(0xD, encrypted_buffer)

# Note: replace all logging calls with 'print' or minimal logger.
# Ensure your async calls and message_dispatcher methods are ported or stubbed for MicroPython.


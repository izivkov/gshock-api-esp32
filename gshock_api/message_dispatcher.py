import uasyncio as asyncio
import json

from gshock_api.logger import logger
from gshock_api.casio_constants import CasioConstants
from gshock_api.iolib.app_info_io import AppInfoIO
from gshock_api.iolib.dst_watch_state_io import DstWatchStateIO
from gshock_api.iolib.world_cities_io import WorldCitiesIO
from gshock_api.iolib.dst_for_world_cities_io import DstForWorldCitiesIO
from gshock_api.iolib.time_io import TimeIO
from gshock_api.iolib.timer_io import TimerIO
from gshock_api.iolib.watch_name_io import WatchNameIO
from gshock_api.iolib.alarms_io import AlarmsIO
from gshock_api.iolib.events_io import EventsIO
from gshock_api.iolib.settings_io import SettingsIO
from gshock_api.iolib.time_adjustement_io import TimeAdjustmentIO
from gshock_api.iolib.watch_condition_io import WatchConditionIO
from gshock_api.iolib.error_io import ErrorIO
from gshock_api.iolib.unknown_io import UnknownIO
from gshock_api.iolib.button_pressed_io import ButtonPressedIO

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class MessageDispatcher:
    watch_senders = {
        "GET_ALARMS": AlarmsIO.send_to_watch,
        "SET_ALARMS": AlarmsIO.send_to_watch_set,
        "SET_REMINDERS": EventsIO.send_to_watch_set,
        "GET_SETTINGS": SettingsIO.send_to_watch,
        "SET_SETTINGS": SettingsIO.send_to_watch_set,
        "GET_TIME_ADJUSTMENT": TimeAdjustmentIO.send_to_watch,
        "SET_TIME_ADJUSTMENT": TimeAdjustmentIO.send_to_watch_set,
        "GET_TIMER": TimerIO.send_to_watch,
        "SET_TIMER": TimerIO.send_to_watch_set,
        "SET_TIME": TimeIO.send_to_watch_set,
    }

    data_received_messages = {
        CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]: AlarmsIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]: AlarmsIO.on_received,
        CHARACTERISTICS["CASIO_TIMER"]: TimerIO.on_received,
        CHARACTERISTICS["CASIO_WATCH_NAME"]: WatchNameIO.on_received,
        CHARACTERISTICS["CASIO_DST_SETTING"]: DstForWorldCitiesIO.on_received,
        CHARACTERISTICS["CASIO_REMINDER_TIME"]: EventsIO.on_received,
        CHARACTERISTICS["CASIO_REMINDER_TITLE"]: EventsIO.on_received_title,
        CHARACTERISTICS["CASIO_WORLD_CITIES"]: WorldCitiesIO.on_received,
        CHARACTERISTICS["CASIO_DST_WATCH_STATE"]: DstWatchStateIO.on_received,
        CHARACTERISTICS["CASIO_WATCH_CONDITION"]: WatchConditionIO.on_received,
        CHARACTERISTICS["CASIO_APP_INFORMATION"]: AppInfoIO.on_received,
        CHARACTERISTICS["CASIO_BLE_FEATURES"]: ButtonPressedIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]: SettingsIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_BLE"]: TimeAdjustmentIO.on_received,
        CHARACTERISTICS["ERROR"]: ErrorIO.on_received,
        CHARACTERISTICS["UNKNOWN"]: UnknownIO.on_received,
        CHARACTERISTICS["CMD_SET_TIMEMODE"]: UnknownIO.on_received,
        CHARACTERISTICS["FIND_PHONE"]: UnknownIO.on_received,
    }

    @staticmethod
    async def send_to_watch(message):
        try:
            if isinstance(message, str):
                json_message = json.loads(message)
            else:
                json_message = message

            action = json_message.get("action")
            if action in MessageDispatcher.watch_senders:
                handler = MessageDispatcher.watch_senders[action]
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            else:
                logger.info("Unknown action: {}".format(action))
        except Exception as e:
            logger.info("send_to_watch error: {}".format(e))

    @staticmethod
    def on_received(data):
        key = data[0:1]  # first byte
        handler = MessageDispatcher.data_received_messages.get(key)
        if handler:
            handler(data)
        else:
            logger.info("Unknown key: {}".format(key))


# Optional usage example (requires an asyncio loop)
# This is just for illustration; you can remove or adapt it:
async def main():
    message = '{"action": "GET_SETTINGS"}'
    await MessageDispatcher.send_to_watch(message)

# Uncomment to run test:
# asyncio.run(main())

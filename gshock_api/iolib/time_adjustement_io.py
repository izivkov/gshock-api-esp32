import uasyncio as asyncio
import ujson as json
from gshock_api.cancelable_result import CancelableResult
from gshock_api.settings import settings
from gshock_api.utils import to_compact_string, to_hex_string, to_int_array
from gshock_api.casio_constants import CasioConstants
from gshock_api.iolib.error_io import ErrorIO
from gshock_api.logger import logger

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimeAdjustmentIO:
    result = None
    connection = None
    original_value = None

    @staticmethod
    async def request(connection):
        TimeAdjustmentIO.connection = connection
        await connection.request("11")

        TimeAdjustmentIO.result = CancelableResult()
        return TimeAdjustmentIO.result.get_result()

    @staticmethod
    def send_to_watch(message):
        # write assumed synchronous in MicroPython BLE
        TimeAdjustmentIO.connection.write(
            0x000C, bytearray([CHARACTERISTICS["TIME_ADJUSTMENT"]])
        )

    @staticmethod
    async def send_to_watch_set(message):
        if TimeAdjustmentIO.original_value is None:
            await ErrorIO.request("Error: Must call get before set")
            return

        # Parse JSON once
        data = json.loads(message)
        time_adjustment = data.get("timeAdjustment") == "True"
        minutes_after_hour = int(data.get("minutesAfterHour", 0))

        def encode_time_adjustment(time_adjustment, minutes_after_hour):
            int_array = to_int_array(TimeAdjustmentIO.original_value)
            int_array[12] = 0x00 if time_adjustment else 0x80
            int_array[13] = minutes_after_hour
            return bytes(int_array)

        encoded = encode_time_adjustment(time_adjustment, minutes_after_hour)
        write_cmd = to_compact_string(to_hex_string(encoded))

        await TimeAdjustmentIO.connection.write(0x000E, write_cmd)

    @staticmethod
    def on_received(message):
        TimeAdjustmentIO.original_value = to_hex_string(message)

        def is_time_adjustment_set(data):
            return data[12] == 0x00

        def get_minutes_after_hour(data):
            return data[13]

        time_adjusted = is_time_adjustment_set(message)
        minutes_after_hour = get_minutes_after_hour(message)

        result_dict = {
            "timeAdjustment": str(time_adjusted),
            "minutesAfterHour": str(minutes_after_hour)
        }

        TimeAdjustmentIO.result.set_result(result_dict)

    @staticmethod
    async def on_received_set(message):
        logger.info("TimeAdjustmentIO onReceivedSet: {}".format(message))

import ujson as json
from gshock_api.cancelable_result import CancelableResult
from gshock_api.utils import to_hex_string
from gshock_api.casio_constants import CasioConstants
from gshock_api.logger import logger

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class TimeAdjustmentIO:
    result: CancelableResult = None
    connection = None
    original_value = None

    @staticmethod
    def send_to_watch(message):
        # write assumed synchronous in MicroPython BLE
        TimeAdjustmentIO.connection.write(
            0x000C, bytearray([CHARACTERISTICS["TIME_ADJUSTMENT"]])
        )

    @staticmethod
    async def request(connection):
        TimeAdjustmentIO.connection = connection
        await connection.request("11")

        TimeAdjustmentIO.result = CancelableResult()
        return TimeAdjustmentIO.result.get_result()

    @staticmethod
    def on_received(message):
        TimeAdjustmentIO.original_value = to_hex_string(
            message
        )  # save original message

        def is_time_adjustment_set(data) -> bool:
            # syncing off: 110f0f0f0600500004000100->80<-10d2
            # syncing on:  110f0f0f0600500004000100->00<-10d2

            # CasioIsAutoTimeOriginalValue.value = data  # save original data for future use
            return int(data[12]) == 0x00

        def get_minutes_after_hour(data) -> int:
            # syncing off: 110f0f0f060050000400010080->10<-d2

            # CasioIsAutoTimeOriginalValue.value = data  # save original data for future use
            return int(data[13])

        timeAdjusted = is_time_adjustment_set(message)
        munutesAfterHour = get_minutes_after_hour(message)
        valueToSetStr = f"""{{"timeAdjusment": "{timeAdjusted}",
            "minutesAfterHour": "{munutesAfterHour}" }}"""

        value = json.loads(valueToSetStr)
        TimeAdjustmentIO.result.set_result(value)

    @staticmethod
    async def on_received_set(message):
        logger.info(f"TimeAdjustmentIO onReceivedSet: {message}")

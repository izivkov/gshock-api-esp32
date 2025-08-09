import ujson as json
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger
from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimerIO:
    result = None
    connection = None

    @staticmethod
    async def request(connection):
        TimerIO.connection = connection
        await connection.request("18")

        TimerIO.result = CancelableResult()
        return await TimerIO.result.get_result()

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_TIMER"]]))

    @staticmethod
    async def send_to_watch_set(data):
        def encode(seconds_str):
            in_seconds = int(seconds_str)
            hours = in_seconds // 3600
            minutes = (in_seconds % 3600) // 60
            seconds = in_seconds % 60

            arr = bytearray(7)
            arr[0] = 0x18
            arr[1] = hours
            arr[2] = minutes
            arr[3] = seconds
            return arr

        data_obj = json.loads(data)
        seconds_as_byte_arr = encode(data_obj.get("value"))
        seconds_as_compact_str = to_compact_string(to_hex_string(seconds_as_byte_arr))
        await TimerIO.connection.write(0x000E, seconds_as_compact_str)

    @staticmethod
    def on_received(data):
        def decode_value(data_bytes):
            # Assumes `data` is already a bytearray or int array.
            hours = data_bytes[1]
            minutes = data_bytes[2]
            seconds = data_bytes[3]
            return hours * 3600 + minutes * 60 + seconds

        decoded = decode_value(data)
        TimerIO.result.set_result(decoded)

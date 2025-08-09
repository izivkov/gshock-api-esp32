import ujson as json
import utime
from gshock_api.logger import logger
from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants
from gshock_api.exceptions import GShockIgnorableException

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class TimeIO:
    connection = None

    @staticmethod
    async def request(connection, current_time, offset):
        TimeIO.connection = connection

        message = {
            "action": "SET_TIME",
            "value": {
                "time": None if current_time is None else int(current_time),
                "offset": offset
            }
        }
        await connection.sendMessage(json.dumps(message))

    @staticmethod
    async def send_to_watch_set(message):
        data = json.loads(message)
        value = data.get("value", {})

        timestamp = value.get("time")
        offset = value.get("offset", 0)

        if timestamp is None:
            timestamp = utime.time()

        date_time = utime.localtime(int(timestamp + offset))
        time_data = TimeEncoder.prepare_current_time(date_time)

        time_command = to_hex_string(
            bytearray([CHARACTERISTICS["CASIO_CURRENT_TIME"]]) + time_data
        )

        try:
            await TimeIO.connection.write(0xE, to_compact_string(time_command))
        except GShockIgnorableException as e:
            logger.info("Ignoring exception: {}".format(e))


class TimeEncoder:
    @staticmethod
    def prepare_current_time(date_tuple):
        # date_tuple: (year, month, mday, hour, minute, second, weekday, yearday)
        arr = bytearray(10)
        year = date_tuple[0]
        arr[0] = year & 0xFF
        arr[1] = (year >> 8) & 0xFF
        arr[2] = date_tuple[1]
        arr[3] = date_tuple[2]
        arr[4] = date_tuple[3]
        arr[5] = date_tuple[4]
        arr[6] = date_tuple[5]
        arr[7] = date_tuple[6]
        arr[8] = 0
        arr[9] = 1
        return arr

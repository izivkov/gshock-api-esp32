import ujson as json
import utime as time
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
                "time": None if current_time is None else round(current_time),
                "offset": offset  # must always be an integer
            }
        }
        await connection.sendMessage(json.dumps(message))

    @staticmethod
    async def send_to_watch_set(message):
        data = json.loads(message)
        value = data.get("value", {})

        # Extract time or fallback to now
        timestamp = value.get("time")
        offset = value.get("offset", 0)

        if timestamp is None:
            timestamp = time.time()  # seconds since epoch

        date_time_sec = int(timestamp + offset)

        # Convert to struct_time
        tm = time.localtime(date_time_sec)

        # Prepare time data
        time_data = TimeEncoder.prepare_current_time(tm)

        time_command = to_hex_string(
            bytearray([CHARACTERISTICS["CASIO_CURRENT_TIME"]]) + time_data
        )

        try:
            await TimeIO.connection.write(0xE, to_compact_string(time_command))
        except GShockIgnorableException as e:
            logger.info("Ignoring {}".format(e))

class TimeEncoder:
    @staticmethod
    def prepare_current_time(tm):
        arr = bytearray(10)
        year = tm[0]
        arr[0] = year & 0xFF
        arr[1] = (year >> 8) & 0xFF
        arr[2] = tm[1]  # month
        arr[3] = tm[2]  # day
        arr[4] = tm[3]  # hour
        arr[5] = tm[4]  # minute
        arr[6] = tm[5]  # second
        arr[7] = tm[6]  # weekday (0=Mon in utime)
        arr[8] = 0
        arr[9] = 1
        return arr
import uasyncio as asyncio
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger
from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class AppInfoIO:
    result = None
    connection = None

    @staticmethod
    async def request(connection):
        AppInfoIO.connection = connection
        await connection.request("22")
        AppInfoIO.result = CancelableResult()
        return AppInfoIO.result.get_result()

    @staticmethod
    async def send_to_watch(connection):
        await connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_APP_INFORMATION"]]))

    @staticmethod
    def on_received(data):
        def set_app_info(data_str):
            # App info packet to restore D button functionality after reset.
            compact = to_compact_string(data_str)
            if compact == "22FFFFFFFFFFFFFFFFFFFF00":
                AppInfoIO.connection.write(0xE, "223488F4E5D5AFC829E06D02")

        set_app_info(to_hex_string(data))
        if AppInfoIO.result:
            AppInfoIO.result.set_result("OK")

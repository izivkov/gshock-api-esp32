import uasyncio as asyncio
import aioble
import bluetooth
from bluetooth import UUID
from gshock_api.casio_constants import CasioConstants
from gshock_api.exceptions import GShockIgnorableException, GShockConnectionError
from gshock_api.logger import logger
from gshock_api.utils import to_casio_cmd, to_hex_string
from gshock_api.watch_info import watch_info
from gshock_api.data_listener import data_listener
from gshock_api import message_dispatcher

class Connection:
    def __init__(self, address=None):
        self.address = address
        self.device = None
        self.client = None
        self.handles_map = self.init_handles_map()
        self.characteristics_map = {}
        self._discovery_lock = asyncio.Lock()
        self._discovered = False

    async def connect(self, excluded_watches=[]) -> bool:
        def _format_addr(addr_bytes):
            """Convert BLE address bytes to string format."""
            return ':'.join(f"{b:02X}" for b in addr_bytes)

        def _is_target_device(adv, excluded_watches):
            """Return True if advertisement matches CASIO and is not excluded."""
            name = (adv.name() or "").upper()
            if not name.startswith("CASIO"):
                return False

            if adv.device:
                addr_str = _format_addr(adv.device.addr)
                if addr_str in excluded_watches:
                    return False

            return True

        try:
            found = None
            while not found:
                async with aioble.scan(5000) as scanner:
                    async for adv in scanner:
                        if _is_target_device(adv, excluded_watches):
                            logger.info("Found CASIO device:", adv.name(),
                                "at", _format_addr(adv.device.addr))
                            
                            watch_info.set_name_and_model(adv.name()) 
                            
                            found = adv.device
                            break

                if not found:
                    await asyncio.sleep(1)  # Delay between scans

            self.device = found
            self.client = await found.connect()

            service = await self.client.service(bluetooth.UUID(CasioConstants.CASIO_MAIN_SERVICE_UUID))

            # Subscribe only to the known notifiable characteristics
            for char_uuid in CasioConstants.CASIO_NOTIFY_CHARACTERISTICS:
                char = await service.characteristic(bluetooth.UUID(char_uuid))
                await data_listener.subscribe(char)

            await self.init_characteristics_map()
            return True

        except Exception as e:
            logger.error(f"Failed to connect to CASIO device: {e}")
            return False

    async def discover_services(self, conn):
        char_map = {}
        try:
            target_uuid = bluetooth.UUID(CasioConstants.CASIO_MAIN_SERVICE_UUID)
            target_service = None

            async for service in conn.services():
                if service.uuid == target_uuid:
                    target_service = service
                    # Can't break — discovery must complete

            if target_service:
                async for char in target_service.characteristics():
                    char_map[char.uuid] = char
        except Exception as e:
            logger.error(f"Error during service discovery: {e}")
        return char_map

    async def init_characteristics_map(self):
        self.characteristics_map = await self.discover_services(self.client)

    async def write(self, handle, data):
        try:
            uuid = self.handles_map.get(handle)

            if UUID(uuid) not in self.characteristics_map:
                logger.info(f"write failed: handle {handle} not in characteristics map")
                if handle == 13:
                    logger.info("Your watch does not support notifications...")
                return

            char = self.characteristics_map[UUID(uuid)]

            payload = to_casio_cmd(data)
            responseType = True if handle == 0x0E else False

            await asyncio.sleep(0.1)

            await char.write(payload, response=responseType, timeout_ms=6000)
            await data_listener.smart_subscribe(char, responseType)

        except OSError as err:
            logger.error(f"OSError sending data to watch: {err}")
            raise GShockIgnorableException(err)
        except Exception as e:
            logger.error(f"Exception: {e!r}")
            
            # Get exception type
            logger.error(f"Type: {type(e).__name__}")

            # Get full traceback (MicroPython-compatible)
            import sys
            sys.print_exception(e)            
            # raise GShockConnectionError(f"Unable to send data to watch: {e}")            

    async def disconnect(self):
        if self.client is None:
            return
        try:
            # Some ports don’t expose is_connected(); disconnect if available
            if hasattr(self.client, "is_connected") and not self.client.is_connected():
                self.client = None
                return
            if hasattr(self.client, "disconnect"):
                await self.client.disconnect()
        finally:
            self.client = None

    async def request(self, request):
        await self.write(0xC, request)

    def init_handles_map(self):
        handles_map = {}

        handles_map[0x04] = CasioConstants.CASIO_GET_DEVICE_NAME
        handles_map[0x06] = CasioConstants.CASIO_APPEARANCE
        handles_map[0x09] = CasioConstants.TX_POWER_LEVEL_CHARACTERISTIC_UUID
        handles_map[
            0x0C
        ] = CasioConstants.CASIO_READ_REQUEST_FOR_ALL_FEATURES_CHARACTERISTIC_UUID
        handles_map[0x0E] = CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID
        handles_map[0x0D] = CasioConstants.CASIO_NOTIFICATION_CHARACTERISTIC_UUID
        handles_map[0x11] = CasioConstants.CASIO_DATA_REQUEST_SP_CHARACTERISTIC_UUID
        handles_map[0x14] = CasioConstants.CASIO_CONVOY_CHARACTERISTIC_UUID
        handles_map[0xFF] = CasioConstants.SERIAL_NUMBER_STRING

        return handles_map

    async def sendMessage(self, message):
        await message_dispatcher.MessageDispatcher.send_to_watch(message)

import uasyncio as asyncio
import aioble
from aioble import DeviceDisconnectedError, GattError  # Micropython aioble exception
import bluetooth
from bluetooth import UUID
from gshock_api.casio_constants import CasioConstants
from gshock_api.exceptions import GShockIgnorableException, GShockConnectionError
from gshock_api.logger import logger
from gshock_api.utils import to_casio_cmd, to_hex_string
from gshock_api.watch_info import watch_info
from gshock_api.data_listener import data_listener
from gshock_api import message_dispatcher
import gc

class Connection:
    def __init__(self, address=None):
        self.address = address
        self.device = None
        self.client = None
        self.handles_map = self.init_handles_map()
        self.characteristics_map = {}
        self._discovery_lock = asyncio.Lock()
        self._discovered = False

    async def connect(self, watch_filter=None) -> bool:
        # Remove non-printable ASCII characters
        def remove_non_printable(s):
            return ''.join(c for c in s if 32 <= ord(c) <= 126)

        # Format BLE address as string
        def _format_addr(addr_bytes):
            return ':'.join('%02X' % b for b in addr_bytes)

        # Check if advertisement matches the desired device and passes filter
        def _is_target_device(adv):
            name = adv.name()
            if not name:
                return False
            name = remove_non_printable(name).upper()
            if not name.startswith('CASIO'):
                return False
            if watch_filter and not watch_filter(name):
                return False
            return True

        try:
            found = None
            while not found:
                async with aioble.scan(5000) as scanner:
                    async for adv in scanner:
                        if not adv:
                            continue
                        if _is_target_device(adv):
                            logger.info(
                                "Found CASIO device:", adv.name(),
                                "at", _format_addr(adv.device.addr)
                            )
                            watch_info.set_name_and_model(adv.name())
                            found = adv.device
                            break
                if not found:
                    await asyncio.sleep(1)

            self.device = found
            self.client = await found.connect()

            service = await self.client.service(bluetooth.UUID(CasioConstants.CASIO_MAIN_SERVICE_UUID))
            if service == None:
                logger.error (f"Could not find service for {CasioConstants.CASIO_MAIN_SERVICE_UUID}")
                return False

            # Subscribe to known notifiable characteristics
            for char_uuid in CasioConstants.CASIO_NOTIFY_CHARACTERISTICS:
                char = await service.characteristic(bluetooth.UUID(char_uuid))
                if char is None:
                    continue
                await data_listener.subscribe(char)

            await self.init_characteristics_map()
            return True

        except Exception as e:
            logger.error("Failed to connect to CASIO device: %s" % e)
            return False

    async def discover_services(self, conn):
        char_map = {}
        services = []

        try:
            # First pass — collect all services
            async for service in conn.services():
                services.append(service)

            # Second pass — get characteristics for each service
            for service in services:
                try:
                    async for char in service.characteristics():
                        char_map[char.uuid] = char

                except Exception as ce:
                    logger.error(f"Error reading characteristics from {service.uuid}: {ce}")
                    continue

        except Exception as e:
            logger.error(f"Error during service discovery: {e}")

        return char_map

    async def init_characteristics_map(self):
        self.characteristics_map = await self.discover_services(self.client)

    async def write(self, handle, data):
        gc.collect()

        uuid = self.handles_map.get(handle)

        if UUID(uuid) not in self.characteristics_map:
            logger.info(f"write failed: handle {handle} not in characteristics map")
            if handle == 13:
                logger.info("Your watch does not support notifications...")
            return

        char = self.characteristics_map[UUID(uuid)]
        payload = to_casio_cmd(data)
        responseType = (handle == 0x0E)

        try:
            await asyncio.sleep(0.1)
            await char.write(payload, response=responseType, timeout_ms=6000)
            await data_listener.smart_subscribe(char, responseType)
    
        except (OSError, GattError, DeviceDisconnectedError) as err:
            logger.error(f"Connection error sending data to watch: {err}")
            raise GShockIgnorableException(err)

        except asyncio.TimeoutError as err:
            logger.error(f"Timeout sending data to watch: {err}")
            raise GShockIgnorableException(err)
        
        except ValueError as err:
            logger.error(f"Value error sending data to watch: {err}")
            raise GShockIgnorableException(err)
        
        finally:
            gc.collect()

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

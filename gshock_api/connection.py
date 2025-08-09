import uasyncio as asyncio
import aioble
from gshock_api.casio_constants import CasioConstants
from gshock_api import message_dispatcher
from gshock_api.utils import to_casio_cmd
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from gshock_api.exceptions import GShockIgnorableException, GShockConnectionError
from gshock_api.scanner import scanner

class Connection:
    def __init__(self, address=None):
        self.handles_map = self.init_handles_map()
        self.address = address  # string like "AA:BB:CC:DD:EE:FF"
        self.client = None      # aioble.DeviceClient instance after connect
        self.characteristics_map = {}  # UUID string -> characteristic object
        self.scanner = scanner  # Your Scanner instance, if any

    def notification_handler(self, data: bytes):
        # called from aioble notification callback with bytes data
        message_dispatcher.MessageDispatcher.on_received(data)

    async def init_characteristics_map(self):
        self.characteristics_map.clear()

        # Get list of services
        services = await self.client.services()  # returns a list
        print(f"[GShock] Discovered {len(services)} services")
        
        for service in services:
            characteristics = await service.characteristics()  # also returns a list
            for char in characteristics:
                self.characteristics_map[str(char.uuid)] = char

        logger.info(f"[GShock] Discovered {len(self.characteristics_map)} characteristics")

    async def connect(self, excluded_watches=None) -> bool:
        try:
            # Use scanner to find device if no address known
            if self.address is None:
                if self.scanner is None:
                    logger.info("No scanner provided to find device")
                    return False
                device = await self.scanner.scan(
                    device_address=None, excluded_watches=excluded_watches
                )
                if device is None:
                    logger.info("No G-Shock device found or name matches excluded watches.")
                    return False

                print(f"[INFO] Found G-Shock device: {device})")

                self.address = ':'.join(f"{b:02X}" for b in device.addr)
                self.client = device
            else:
                # Convert address string to bytes
                addr_bytes = bytes(int(b, 16) for b in self.address.split(":"))
                self.client = aioble.DeviceClient(addr_bytes)

            logger.info(f"[GShock] Connecting to {self.address}")
            self.client = await asyncio.wait_for(self.client.connect(), timeout=10)
            if not self.client.is_connected():
                logger.info(f"Failed to connect to {self.address}")
                return False

            await self.init_characteristics_map()

            # Start notifications: set callback wrapping notification handler
            notify_uuid = CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID
            char = self.characteristics_map.get(notify_uuid)
            if char:
                await char.start_notify(lambda data: self.notification_handler(data))
                logger.info("[GShock] Started notifications")
            else:
                logger.info("[GShock] Notification characteristic not found")

            return True

        except Exception as e:
            logger.info(f"[GShock Connect] Connection failed: {e}")
            return False

    async def disconnect(self):
        if self.client is not None and self.client.is_connected():
            await self.client.disconnect()
            logger.info("[GShock] Disconnected")
            self.client = None

    def is_service_supported(self, handle):
        uuid = self.handles_map.get(handle)
        # Return True if uuid is in characteristics map
        return uuid in self.characteristics_map

    async def write(self, handle, data):
        try:
            uuid = self.handles_map.get(handle)

            if uuid not in self.characteristics_map:
                logger.info(f"write failed: handle {handle} not in characteristics map")
                if handle == 13:
                    logger.info("Your watch does not support notifications...")
                return

            char = self.characteristics_map[uuid]
            if self.client is None or not self.client.is_connected():
                logger.info("Not connected")
                return

            if isinstance(data, str):
                data = data.encode()

            await char.write(to_casio_cmd(data), response=True)
            logger.info(f"Successfully wrote to characteristic {uuid}")

        except Exception as e:
            # Emulate exception handling as in your original code
            e.args = (type(e).__name__,)
            # You may check specific exceptions if needed here
            raise GShockIgnorableException(e) if isinstance(e, OSError) else GShockConnectionError(f"Unable to send data to watch: {e}")

    async def request(self, request):
        await self.write(0x0C, request)

    def init_handles_map(self):
        handles_map = {}

        handles_map[0x04] = CasioConstants.CASIO_GET_DEVICE_NAME
        handles_map[0x06] = CasioConstants.CASIO_APPEARANCE
        handles_map[0x09] = CasioConstants.TX_POWER_LEVEL_CHARACTERISTIC_UUID
        handles_map[0x0C] = CasioConstants.CASIO_READ_REQUEST_FOR_ALL_FEATURES_CHARACTERISTIC_UUID
        handles_map[0x0E] = CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID
        handles_map[0x0D] = CasioConstants.CASIO_NOTIFICATION_CHARACTERISTIC_UUID
        handles_map[0x11] = CasioConstants.CASIO_DATA_REQUEST_SP_CHARACTERISTIC_UUID
        handles_map[0x14] = CasioConstants.CASIO_CONVOY_CHARACTERISTIC_UUID
        handles_map[0xFF] = CasioConstants.SERIAL_NUMBER_STRING

        return handles_map

    async def sendMessage(self, message):
        await message_dispatcher.MessageDispatcher.send_to_watch(message)

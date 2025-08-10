import uasyncio as asyncio
import aioble
import bluetooth
from bluetooth import UUID
from gshock_api.casio_constants import CasioConstants
from gshock_api import message_dispatcher
from gshock_api.exceptions import GShockIgnorableException, GShockConnectionError
from gshock_api.logger import logger
from gshock_api.utils import to_casio_cmd

class Connection:
    def __init__(self, address=None):
        self.address = address
        self.device = None
        self.client = None
        self.handles_map = self.init_handles_map()
        self.characteristics_map = {}
        # Serialize discovery to avoid 'Discovery in progress' races
        self._discovery_lock = asyncio.Lock()
        self._discovered = False


    async def connect(self, excluded_watches=[]) -> bool:
        
        try:
            found = None
            async with aioble.scan(5000) as scanner:
                async for adv in scanner:
                    name = adv.name() or ""
                    print(f"---> adv: {adv}, name: {name}")
                    if name.upper().startswith("CASIO"):
                        found = adv.device
                        break

            if not found:
                print(f"---> not found")
                return False

            self.device = found
            # self.address = ':'.join(f"{b:02X}" for b in found.addr)
            self.client = await found.connect()

            await self.init_characteristics_map()

            return True
        except Exception:
            return False

    async def discover_services(self, conn):
        print(f"---> discover_services called")
        char_map = {}

        try:
            # target_service_uuid = "26eb000d-b012-49a8-b1f8-394fb2032b0f"
            target_service_uuid = bluetooth.UUID("26eb000d-b012-49a8-b1f8-394fb2032b0f")
            target_service = None

            # First pass – discover all services and store them
            async for service in conn.services():
                print(f"Service: {str(service.uuid)}, {target_service_uuid}")  
                if service.uuid == target_service_uuid:
                    print(f"Found target service: {service.uuid}")
                    target_service = service
                    # Do not break, we need to complete the service discovery,
                    # Otherwise we get "Discovery in progress" error.
                    # break

            if target_service:
                print(f"Service {target_service.uuid} characteristics:")
                async for char in target_service.characteristics():
                    char_map[char.uuid] = char

        except Exception as e:
            print(f"Error during service discovery: {e}")

        print(f"---> discover_services returning char_map: {char_map}")
        return char_map

    async def init_characteristics_map(self):
        print(f"---> init_characteristics_map called")
        self.characteristics_map = await self.discover_services(self.client)
        print(f"---> init_characteristics_map END")

    async def smart_write(self, char, data):
        WRITE = 0x08
        WRITE_NO_RESPONSE = 0x04

        if (char.properties & WRITE) != 0:
            response = True
        elif (char.properties & WRITE_NO_RESPONSE) != 0:
            response = False
        else:
            raise RuntimeError("Characteristic does not support write")

        await char.write(data, response=response)

    async def write(self, handle, data):
        try:
            uuid = self.handles_map.get(handle)
            print(f"---> write called with handle: {handle}, data: {data}, uuid: {uuid}")

            if UUID(uuid) not in self.characteristics_map:
                logger.info("write failed: handle {} not in characteristics map".format(handle))
                if handle == 13:
                    logger.info("Your watch does not support notifications...")
                return

            print(f"---> write: found uuid {uuid} in characteristics map")
            entry = self.characteristics_map[UUID(uuid)]
            print(f"---> write: entry: {entry}")
            if isinstance(entry, str):
                print(f"---> write: entry is a string, resolving characteristic for uuid: {uuid}")

                char = await self._resolve_char(uuid)
                if not char:
                    logger.info("Characteristic not found for UUID {}".format(uuid))
                    return
            else:
                char = entry

            if self.client is None or (hasattr(self.client, "is_connected") and not self.client.is_connected()):
                logger.info("Not connected")
                return

            payload = to_casio_cmd(data) if isinstance(data, str) else data
            print(f"---> Writing to characteristic {char.uuid}: {payload}, data: {data}")
            await self.smart_write(char, payload)
            print(f"Write completed.")

        except OSError as err:
            raise GShockIgnorableException(err)
        except Exception as e:
            raise GShockConnectionError("Unable to send data to watch: {}".format(e))

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

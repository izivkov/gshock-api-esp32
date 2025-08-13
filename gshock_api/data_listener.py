import uasyncio as asyncio
import bluetooth

from gshock_api.casio_constants import CasioConstants
from gshock_api import message_dispatcher
from gshock_api.logger import logger

class DataListener:
    def __init__(self):
        self.listener_tasks = {}
        self.old_responseType = None

    async def listen_for_notifications(self, characteristic):
        try:
            while True:
                data = await characteristic.notified()
                message_dispatcher.MessageDispatcher.on_received(data)
        except asyncio.CancelledError:
            pass  # Task cancelled normally
        except OSError as e:
            logger.info(f"Device disconnected or notification error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in notification listener: {e}")

    async def subscribe(self, char):
        await self.unsubscribe(char)  # Cancel old listener if exists
        await char.subscribe()
        self.listener_tasks[char.uuid] = asyncio.create_task(
            self.listen_for_notifications(char)
        )

    async def smart_subscribe(self, char, responseType):
        if responseType:
            await self.subscribe(char)
            # logger.info(f"Subscribed to {char.uuid} with responseType {responseType}")  

        self.old_responseType = responseType

    async def unsubscribe(self, char):
        task = self.listener_tasks.pop(char.uuid, None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Listener for {char.uuid} cancelled")
    
data_listener = DataListener()

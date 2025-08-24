import uasyncio as asyncio
import config_server
import gshock_server

from lib.config.config_manager import config_manager
from gshock_api.logger import logger


# Combine them in a single main coroutine
config_manager.load()

if not config_manager.get("ssid") or not config_manager.get("password"):
    print(f" {config_manager.get_instructions()}")
    print(f"Starting configuration server")
    asyncio.run(config_server.main())

else:
    asyncio.run(gshock_server.main())
    pass


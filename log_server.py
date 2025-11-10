import uasyncio as asyncio
import aioble
import bluetooth
import gc
from lib.logs.log_sender import LogSender
from lib.logs.activity_log import activity_log

"""
This module connects to an Android App and sends activity logs.
"""

SERVICE_UUID = bluetooth.UUID(0x1001)
LOG_CHAR_UUID = bluetooth.UUID(0x1002)

# --- GATT Service Setup ---
service = aioble.Service(SERVICE_UUID)
aioble.register_services(service)

log_char = aioble.Characteristic(
    service,
    LOG_CHAR_UUID,
    read=True,
    write=True,
    notify=True,
    capture=True
)

aioble.register_services(service)
log_sender = None

async def on_new_log(log_message):
    if log_sender:
        print("on_new_log: New log added, sending via BLE...")
        await log_sender.send_log(log_message.to_dict())
    else:
        print("Log sender not initialized yet.")    

# There is only one instance of activity_log, and is being updated from gshock_server
activity_log.set_on_add (on_new_log)

async def ble_logger():
    global log_sender

    while True:
        print("Advertising logs service...")
        adv = aioble.advertise(
            100_000,
            name="ESP32_Logger",
            services=[SERVICE_UUID]
        )

        connection = await adv
        print("🔵 Device connected.")

        log_sender = LogSender(activity_log, connection, log_char)

        try:
            # Wait for Android to send "START" command and send logs
            while connection.is_connected():
                print("Waiting for START command...")
                connection, data = await log_char.written()
                cmd = data.decode().strip()
                if cmd == "START":
                    await log_sender.send_logs(activity_log.get_logs())
                    break

            # After sending logs, *keep* waiting until device disconnects
            while connection.is_connected():
                await asyncio.sleep(1)  # or small delay to avoid busy loop

        except Exception as e:
            print("Error:", e)

        finally:
            print("finally called...exiting connection scope")
            gc.collect()

        print("Device disconnected, resuming advertising loop")

# --- Main entry ---
async def main():
    await ble_logger()

if __name__ == "__main__":
    asyncio.run(main())
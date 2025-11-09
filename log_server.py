import uasyncio as asyncio
import aioble
import bluetooth
import json
from gshock_server import activity_log

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

async def on_new_log(log_message):
    send_log(None, log_message.to_dict())

activity_log.set_on_add (on_new_log)

async def send_notify_safe(connection, data):
    """Send notification safely, handling potential exceptions."""
    try:
        await log_char.notify(connection, data)
    except TypeError:
        # Ignore occasional NoneType issues from BLE library quirks
        pass

async def send_log(connection, log):
    """Send a single log entry as JSON, chunked without header."""
    if not connection.is_connected():
        print("Connection lost before sending.")
        return

    # Convert dict to JSON bytes
    log_data = json.dumps(log).encode('utf-8')
    chunk_size = 17

    try:
        for i in range(0, len(log_data), chunk_size):
            if not connection.is_connected():
                print("Connection lost during notify.")
                return

            chunk = log_data[i:i + chunk_size]
            await send_notify_safe(connection, chunk)

        print("✅ Finished sending one log.")

    except Exception as e:
        print("Notify failed:", e)
        print("Exception type:", type(e).__name__)


async def send_logs(connection):
    """Send all logs one by one."""
    if not connection.is_connected():
        print("Connection lost before sending.")
        return

    logs = activity_log.get_logs()
    print(f"type of logs: {type(logs).__name__}")

    for log in logs:
        # Convert LogMessage to dict, then send
        await send_log(connection, log.to_dict())

    print("✅ Finished sending all logs.")


# --- BLE Server / Peripheral Logic ---
async def ble_logger():
    while True:
        print("Advertising logs service...")
        adv = aioble.advertise(
            100_000,
            name="ESP32_Logger",
            services=[SERVICE_UUID]
        )

        connection = await adv
        print("🔵 Device connected.")

        try:
            # Wait for Android to send "START"
            while connection.is_connected():
                print("Waiting for START command...")
                connection, data = await log_char.written()
                cmd = data.decode().strip()
                if cmd == "START":
                    await send_logs(connection)
                    break

            await connection.disconnect()

        except Exception as e:
            print("Error:", e)
        finally:
            print("Disconnected.")
            await asyncio.sleep(2)


# --- Main entry ---
async def main():
    await ble_logger()

asyncio.run(main())

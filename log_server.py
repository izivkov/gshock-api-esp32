import uasyncio as asyncio
import aioble
import bluetooth
import json

SERVICE_UUID = bluetooth.UUID(0x1001)
LOG_CHAR_UUID = bluetooth.UUID(0x1002)

# --- GATT Service Setup ---
service = aioble.Service(SERVICE_UUID)

log_char = aioble.Characteristic(
    service,
    LOG_CHAR_UUID,
    read=True,
    write=True,  # This allows the Android app to write the "START" command
    notify=True,  # This allows the ESP32 to send notifications
    capture=True
)

aioble.register_services(service)

# Example log storage
logs = [
    {"event": "watch_connected", "time": "12:00"},
    {"event": "time_synced", "time": "12:01"}
]

async def send_logs(connection):
    if not connection.is_connected():
        print("Connection lost before sending.")
        return

    data = json.dumps(logs).encode('utf-8')
    chunk_size = 17

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        try:
            if not connection.is_connected():
                print("Connection lost during notify.")
                break
            
            await log_char.notify(connection, chunk)

        except TypeError:
            # For some reason getting: ['NoneType' object isn't iterable] message
            # Ignore and continue
            ...

        except Exception as e:
            print("Notify failed:", e)
            print("Exception type:", type(e))
            break

    print("Finished sending logs.")

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

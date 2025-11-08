import uasyncio as asyncio
import aioble
import bluetooth
import json
import gc
# --- CONFIG ---

# --- CONFIG ---
# Use your actual UUIDs
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
LOG_CHAR_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

# --- GATT Service Setup ---
service = aioble.Service(SERVICE_UUID)

# ========================= THE FIX IS HERE =========================
# The characteristic MUST be declared with write=True and notify=True
# to match what the Android app is checking for.
log_char = aioble.Characteristic(
    service,
    LOG_CHAR_UUID,
    read=True,
    write=True,  # This allows the Android app to write the "START" command
    notify=True  # This allows the ESP32 to send notifications
)
# =================================================================

aioble.register_services(service)

# Example log storage
logs = [
    {"event": "watch_connected", "time": "12:00"},
    {"event": "time_synced", "time": "12:01"}
]


# --- Helper to send logs as JSON ---
async def send_logs(connection):
    print(">>> Preparing to send logs...")
    log_json = json.dumps(logs)
    print(f">>> Log JSON {log_json}, log_char: {log_char}")
    
    print(type(log_char))
    print(type(b"Hi"))
    print(f"write: {log_char.write}")
    
    if connection.is_connected():
        await log_char.write(b"Hi", True)
    else:
        print("Connection lost before sending logs.")
        return

    print("Sent logs:", log_json)

async def send_logs_notify(connection):
    print(">>> Preparing to send logs...")
    log_json = json.dumps(logs)
    print(f">>> Log JSON {log_json}, log_char: {log_char}")

    if not connection.is_connected():
        print("Connection lost before sending logs.")
        return

    try:
        # Convert to bytes
        data = log_json.encode("utf-8")

        # Send data in chunks (BLE limit ~20 bytes)
        chunk_size = 20
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            await log_char.notify(connection, chunk)
            await asyncio.sleep_ms(50)  # small delay for reliability

        print("Sent logs:", log_json)

    except Exception as e:
        print("Error during send_logs:", e)


# --- BLE Server / Peripheral Logic ---
async def ble_logger():
    while True:
        # Start advertising
        print("Advertising logs service...")
        adv = aioble.advertise(
            100_000,  # advertise duration in ms
            name="ESP32_Logger",
            services=[SERVICE_UUID]
        )

        # Wait for a central (Android app) to connect
        connection = await adv
        print("Connected to:", connection.device)

        # Once connected, send logs
        try:
            await send_logs_notify(connection)
            await asyncio.sleep(1)
        except Exception as e:
            print("Error sending logs:", e)
        finally:
            await connection.disconnect()
            print("Disconnected.")

        await asyncio.sleep(2)


# --- Main entry ---
async def main():
    await ble_logger()

asyncio.run(main())

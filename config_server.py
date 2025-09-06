import uasyncio as asyncio
import bluetooth
import aioble
import struct
import ujson as json
import machine
from lib.display.display import display
from lib.display.dim_display import DimDisplay

SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_UUID = bluetooth.UUID("abcdefab-1234-5678-1234-56789abcdef0")

def save_config(obj, filename="config.json"):
    try:
        with open(filename, "w") as f:
            f.write(json.dumps(obj))
            f.write("\n")
        print("Config saved")
        display.show_message("Config saved...")
    except Exception as e:
        print("Failed to save config:", e)

def process_full_message(json_bytes):
    try:
        obj = json.loads(json_bytes)
        print("Valid JSON received:", obj)
        save_config(obj)
        machine.reset()
    except ValueError as e:
        print("Invalid JSON received:", e)
        display.show_message("Invalid JSON received")

async def init_ble():
    while True:
        try:
            ble = bluetooth.BLE()
            ble.active(False)
            ble.active(True)
            ble.config(gap_name="TimeServer")

            service = aioble.Service(SERVICE_UUID)
            char = aioble.Characteristic(service, CHAR_UUID, write_no_response=True, capture=True)
            aioble.register_services(service)

            await asyncio.sleep_ms(200)  # Ensure GATT table ready
            print("BLE config successful")
            return char  # return characteristic for use
        except OSError as e:
            if e.args[0] == 110:  # ETIMEOUT
                print("Connection timeout, retrying BLE config...")
            else:
                print(f"BLE error: {e}, retrying...")
            await asyncio.sleep_ms(500)
        except Exception as e:
            print(f"Unexpected error: {e}, retrying...")
            await asyncio.sleep_ms(500)

async def handle_connection(char, conn):
    print("Central connected:", conn.device)
    display.show_message(f"Connected to app: {conn.device}")

    buffer = bytearray()
    expected_len = None

    display.show_message(f"Waiting for data...")
    
    while conn.is_connected():
        try:
            _, data = await char.written()

            if not data:
                continue

            buffer.extend(data)

            if expected_len is None and len(buffer) >= 4:
                # Extract 4-byte length prefix
                expected_len = struct.unpack(">I", buffer[:4])[0]
                print(f"Expecting {expected_len} bytes of JSON data...")
                buffer = buffer[4:]  # Keep rest of JSON payload

            if expected_len is not None and len(buffer) >= expected_len:
                message_bytes = buffer[:expected_len]
                try:
                    process_full_message(message_bytes)
                except Exception as e:
                    print(f"Error processing full message: {e}")

                buffer = buffer[expected_len:]
                expected_len = None
        except asyncio.CancelledError:
            break
        except Exception as e:
            print("Error or disconnected:", e)
            display.show_message(f"Disconnected: {e}")
            break

    print("Central disconnected")
    display.show_message(f"Configuration completed.")

async def advertise_and_handle_connections(char):
    while True:
        try:
            print("Advertising...")
            conn = await aioble.advertise(
                250_000,
                name="TimeServer",
                services=[SERVICE_UUID]
            )
            await handle_connection(char, conn)
        except Exception as e:
            print("Error during advertising:", e)


async def config_server():
    char = await init_ble()
    await advertise_and_handle_connections(char)

async def main():
    display.show_message("Configuration mode. Start the Android app to configure")
    await config_server()

if __name__ == "__main__":
    import time
    try:
        display.show_message("Starting...")
        time.sleep(2)  # Startup delay
        asyncio.run(main())
    except Exception as e:
        print("Fatal error in main loop:", e)

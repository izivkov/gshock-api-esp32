import uasyncio as asyncio
import bluetooth
import aioble
import struct
import ujson as json
import machine
import sys
import time
from lib.display.display import display

# Define constants outside of functions
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_UUID = bluetooth.UUID("abcdefab-1234-5678-1234-56789abcdef0")

def save_config(obj, filename="config.json"):
    try:
        with open(filename, "w") as f:
            # Dump with indentation for pretty format
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

async def config_server():
    # Initialize BLE stack and services within this coroutine
    # This prevents race conditions with other tasks
    try:
        ble = bluetooth.BLE()
        ble.active(False) # Ensure BLE stack is reset
        ble.active(True)
        ble.config(gap_name="TimeServer")

        service = aioble.Service(SERVICE_UUID)
        char = aioble.Characteristic(service, CHAR_UUID, write_no_response=True, capture=True)
        aioble.register_services(service)
        
        # Add a short delay after registering services to ensure the GATT table is ready
        await asyncio.sleep_ms(200)

    except Exception as e:
        display.show_message(f"BLE Error: {e}")
        # Use a print to output a stack trace to the console
        sys.print_exception(e) # this will still fail
        print("BLE Setup failed. Exiting config_server.")
        return

    while True:
        print("Advertising...")
        try:
            conn = await aioble.advertise(
                250_000,
                name="TimeServer",
                services=[SERVICE_UUID]
            )
        except Exception as e:
            # Handle potential advertising errors
            print("Error during advertising:", e)
            continue

        print("Central connected:", conn.device)
        display.show_message(f"Connected to app: {conn.device}")

        buffer = bytearray()
        expected_len = None

        while conn.is_connected():
            try:
                display.show_message(f"Waiting for data...")
                _, data = await char.written()

                if not data:
                    continue

                # Always accumulate incoming data into buffer
                buffer.extend(data)

                # If we don't know expected message length yet and buffer has at least 4 bytes,
                # extract the length prefix from the first 4 bytes
                if expected_len is None and len(buffer) >= 4:
                    expected_len = struct.unpack(">I", buffer[:4])[0]
                    print(f"Expecting {expected_len} bytes of JSON data...")
                    # Remove the 4-byte length prefix, keep the rest (start of JSON payload)
                    buffer = buffer[4:]

                # If we know message length and buffer has enough bytes, process complete message
                if expected_len is not None and len(buffer) >= expected_len:
                    # Extract entire JSON message bytes
                    message_bytes = buffer[:expected_len]

                    # Process full message (decode JSON, etc.)
                    try:
                        process_full_message(message_bytes)
                    except Exception as e:
                        print(f"Error processing full message: {e}")

                    # Remove processed bytes from buffer
                    buffer = buffer[expected_len:]

                    # Reset expected length to wait for next message
                    expected_len = None

            except asyncio.CancelledError:
                # This could happen if the main loop tries to cancel this task
                break
            except Exception as e:
                # Handle connection loss or other errors gracefully
                print("Error or disconnected:", e)
                display.show_message(f"Disconnected: {e}")
                break

        print("Central disconnected")
        display.show_message(f"Configuration completed.")

async def main():
    print(f"Config Server started...") 
    display.show_message(f"Configuration mode. Start the Android app to configure")
    await config_server()

if __name__ == "__main__":
    try:
        # Add a startup delay here to ensure the system is ready
        time.sleep(5) # A safe bet
        asyncio.run(main())
    except Exception as e:
        # Catch any errors from the main entry point
        print("Fatal error in main loop:", e)


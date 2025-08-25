import uasyncio as asyncio
import bluetooth
import aioble
import struct
import ujson as json
import machine

SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_UUID = bluetooth.UUID("abcdefab-1234-5678-1234-56789abcdef0")

async def main():       
    print(f"Config Server started...") 
    await config_server()

def process_full_message(json_bytes):
    try:
        obj = json.loads(json_bytes)
        print("Valid JSON received:", obj)

        save_config(obj)
        machine.reset()

    except ValueError as e:
        print("Invalid JSON received:", e)

def save_config(obj, filename="config.json"):
    try:
        with open(filename, "w") as f:
            # Dump with indentation for pretty format
            f.write(json.dumps(obj))
            f.write("\n")
        print("Config saved")
    except Exception as e:
        print("Failed to save config:", e)

async def config_server():
    ble = bluetooth.BLE()
    ble.active(True)
    ble.config(gap_name="TimeServer")

    service = aioble.Service(SERVICE_UUID)
    char = aioble.Characteristic(service, CHAR_UUID, write_no_response=True, capture=True)

    aioble.register_services(service)

    while True:
        print("Advertising...")
        conn = await aioble.advertise(
            250_000,
            name="TimeServer",
            services=[SERVICE_UUID]
        )

        try:
            mtu = await conn.exchange_mtu(256)
            print("Negotiated MTU:", mtu)
        except Exception as e:
            print("MTU exchange failed:", e)

        print("Central connected:", conn.device)

        buffer = bytearray()
        expected_len = None

        while True:
            try:
                _, data = await char.written()
                print(f"data: {data}")
                if not data:
                    continue

                # Always accumulate incoming data into buffer
                buffer.extend(data)
                print(f"Buffer length: {len(buffer)}")

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

            except Exception as e:
                print("Error or disconnected:", e)
                break

        print("Central disconnected")

if __name__ == "__main__":
    asyncio.run(main())
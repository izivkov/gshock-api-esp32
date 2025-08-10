import uasyncio as asyncio
import aioble
import bluetooth
import time

def props_to_string(props: int) -> str:
    out = []
    if props & bluetooth.FLAG_READ:
        out.append("READ")
    if props & bluetooth.FLAG_WRITE:
        out.append("WRITE")
    if props & bluetooth.FLAG_WRITE_NO_RESPONSE:
        out.append("WRITE_NO_RESPONSE")
    if props & bluetooth.FLAG_NOTIFY:
        out.append("NOTIFY")
    if props & bluetooth.FLAG_INDICATE:
        out.append("INDICATE")
    # MicroPython doesn’t define BROADCAST / SIGNED_WRITE flags explicitly in aioble,
    # but they’re in the Bluetooth spec if needed.
    return " | ".join(out) if out else "NONE"

async def discover_services(conn):
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

    return char_map

async def main():
    print("Scanning for CASIO device...")

    device = None
    while device is None:
        async with aioble.scan(duration_ms=5000) as scanner:
            async for result in scanner:
                name = result.name() or "Unknown"
                print(f"Found: {result.device.addr_hex()}  Name: {name}")
                if name.upper().startswith("CASIO"):
                    device = result.device
                    break
        if device is None:
            print("No CASIO device found, scanning again...")

    print(f"Connecting to device: {device.addr_hex()}")

    conn = await device.connect()
    try:
        print("Connected. Discovering services...")
        services = await discover_services(conn)
        print(f"Discovered {len(services)} services")
    finally:
        await conn.disconnect()
        print("Disconnected.")

asyncio.run(main())

import uasyncio as asyncio
import aioble

class Scanner:
    def __init__(self):
        self._found_device = None

    async def scan(self, device_address=None, excluded_watches=None, max_retries=60):
        excluded_watches = excluded_watches or []
        excluded_watches_ci = [w.lower() for w in excluded_watches]
        retries = 0

        print("[DEBUG] Starting BLE scan...")

        while retries < max_retries:
            try:
                async with aioble.scan(5000) as scanner:
                    print("[DEBUG] Scanning for devices...")
                    async for adv in scanner:
                        name = adv.name() or ""
                        parts = name.split(" ", 1)

                        if not parts or parts[0].lower() != "casio":
                            continue

                        if len(parts) > 1 and parts[1].lower() in excluded_watches_ci:
                            print(f"[INFO] {name} excluded!")
                            continue

                        print(f"[DEBUG] ✅ Matched device: {name}")

                        addr_str = ':'.join(f"{b:02X}" for b in adv.device.addr)
                        if device_address and addr_str.lower() != device_address.lower():
                            continue

                        print(f"[INFO] ✅ Found: {name} ({addr_str})")
                        # Set your watch_info etc here
                        self._found_device = adv.device
                        return adv.device

                retries += 1
                print(f"[DEBUG] ⚠️ No matching device found, retry {retries}...")
                await asyncio.sleep(1)

            except Exception as e:
                print(f"[WARN] ⚠️ BLE scan error: {e}")
                retries += 1
                await asyncio.sleep(1)

        print("[ERROR] ⚠️ Max retries reached. No device found.")
        return None

scanner = Scanner()

# Example usage:
# scanner = Scanner()
# device = await scanner.scan()

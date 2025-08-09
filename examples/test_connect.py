import uasyncio as asyncio
from bluetooth import BLE

_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6
_IRQ_PERIPHERAL_CONNECT = 7

class SimpleCentral:
    def __init__(self):
        self.ble = BLE()
        self.ble.active(True)
        def irq_handler(event, data):
            self.bt_irq(event, data)
        self.ble.irq(irq_handler)

        self.scan_event = asyncio.Event()

        self.connect_event = asyncio.Event()
        self.connect_addr_type = None
        self.connect_addr = None
        print("BLE initialized and IRQ handler set.")

    def _decode_name(self, adv_data):
        if isinstance(adv_data, memoryview):
            adv_data = bytes(adv_data)  # Convert to bytes

        i = 0
        while i + 1 < len(adv_data):
            length = adv_data[i]
            if length == 0:
                break
            ad_type = adv_data[i + 1]
            if ad_type == 0x09:  # Complete Local Name
                print("Found Complete Local Name in adv_data:", adv_data)
                try:
                    name_bytes = adv_data[i + 2 : i + 1 + length]
                    return name_bytes.decode('utf-8')  # Specify utf-8 explicitly
                except Exception as e:
                    print("Exception decoding name:", e)
                    return None
            i += 1 + length

        return None

    def bt_irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data

            name = self._decode_name(adv_data)
            print(f"Scanned device: {addr_type} {addr} {adv_type} {rssi} {name}")

            if name and name.upper().startswith("CASIO"):                
                print("Found CASIO device, attempting to connect...")

                # Stop scanning before connecting
                self.ble.gap_scan(None)

                try:
                    self.ble.gap_connect(addr_type, bytes(addr))
                    print("Connection initiated")
                except Exception as e:
                    print("Connection failed:", e)

    async def forever_scan_and_connect(self):
        try:
            while True:
                self.connect_addr = None
                self.connect_addr_type = None
                self.scan_event.clear()

                # Scan for 5 seconds
                self.ble.gap_scan(5000, 30000, 30000)

                await self.scan_event.wait()
                self.ble.gap_scan(None)  # Stop scanning (defensive: stop scan after match)

                if self.connect_addr:
                    print("Attempting to connect...")
                    self.ble.gap_connect(self.connect_addr_type, self.connect_addr)
                    # Wait a bit for connect; in real use, track disconnect event as well.
                    await asyncio.sleep(10)
                    print("Disconnecting and restarting scan.")
                    # Add BLE disconnect code here if you want to formally disconnect each time.
                    await asyncio.sleep(1)
                else:
                    print("No matching device found, will retry.")
                    await asyncio.sleep(1)

        except Exception as e:
            print("Exception in forever_scan_and_connect:", e)
            raise

async def main():
    central = SimpleCentral()
    asyncio.create_task(central.forever_scan_and_connect())  # start the scan task
    await asyncio.sleep(10)  # or some other logic


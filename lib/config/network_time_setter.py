import network
import ntptime
import time
import machine
import urequests
import gc

class NetworkTimeSetter:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.timezone_set = False
        time.sleep_ms(200)

    def _connect_wifi(self, ssid, password):
        self.wlan.active(False)    
        while not self.wlan.active():
            self.wlan.active(True)
            time.sleep_ms(200)

        if not self.wlan.isconnected():
            print(f"Connecting to WiFi SSID: {ssid}...")
            self.wlan.connect(ssid, password)

            # Wait for connection with timeout
            timeout = 15  # seconds
            start = time.time()
            while not self.wlan.isconnected():
                if time.time() - start > timeout:
                    raise Exception("Failed to connect to WiFi: Timeout")
                time.sleep(1)

        print("Network config:", self.wlan.ifconfig())

    def _get_timezone_offset(self, timezone):
        self.timezone_set = True

        CHINA_TZ_OFFSETS = {
            "Asia/Shanghai": 8*3600,
            "Asia/Beijing": 8*3600,
            "Asia/Chongqing": 8*3600,
            "Asia/Harbin": 8*3600,
            "Asia/Urumqi": 6*3600,
        }

        if timezone in CHINA_TZ_OFFSETS:
            return CHINA_TZ_OFFSETS[timezone]

        urls = [
            f"http://worldtimeapi.org/api/timezone/{timezone}",
            f"http://avmedia.org:11080/timezone/{timezone}"
        ]

        for url in urls:
            resp = None
            try:
                print(f"Fetching timezone offset from {url}...")
                resp = urequests.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    utc_offset_str = data.get("utc_offset")
                    sign = 1 if utc_offset_str[0] == '+' else -1
                    hours = int(utc_offset_str[1:3])
                    minutes = int(utc_offset_str[4:6])
                    offset_seconds = sign * (hours*3600 + minutes*60)
                    return offset_seconds
                else:
                    print(f"Error fetching timezone from {url}: {resp.status_code}")
            except Exception as e:
                print(f"Exception fetching timezone from {url}: {e}")
            finally:
                if resp:
                    resp.close()

        self.timezone_set = False
        raise Exception("Failed to get timezone offset from both sources")

    def set_time(self, ssid, password, timezone) -> bool:
        # Connect to Wi-Fi
        self._connect_wifi(ssid, password)

        try:
            # Sync NTP to UTC
            print("Fetching time from NTP...")
            ntptime.settime()  # sets time to UTC

            # Get timezone offset dynamically (DST-aware)
            try:
                offset_sec = self._get_timezone_offset(timezone)
            except Exception as e:
                print("Failed to get timezone offset:", e)
                # Do not set time if offset fetch fails
                return False
            
            print(f"Offset for {timezone}: {offset_sec} seconds")

            # Apply offset to UTC time
            utc_time = time.localtime()
            local_epoch = time.mktime(utc_time) + offset_sec

            local_time = time.localtime(local_epoch)
            if local_time[0] < 2025:
                print("Failed to get valid local time.")
                return False

            # Set RTC to local time
            machine.RTC().datetime((
                local_time[0], local_time[1], local_time[2],
                local_time[6] + 1,  # weekday (1=Monday)
                local_time[3], local_time[4], local_time[5], 0
            ))

            print(f"Time set to {timezone}: {local_time}")
            return True

        except Exception as e:
            print("Error setting time:", e)

        finally:
            ...

    def is_NTP_set(self):
        rtc = machine.RTC()
        year = rtc.datetime()[0]
        return year >= 2025 and self.timezone_set

    def cleanup(self):
        print("Cleaning up network resources...")
        if self.wlan:
            self.wlan.active(False)

        gc.collect()

network_time_setter = NetworkTimeSetter()

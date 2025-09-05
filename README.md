# ESP32 G-Shock Time Server

This project provides an **ESP32-based** time server for Casio G-Shock watches. The ESP32 is a tiny, low-cost microcontroller with built-in WiFi and Bluetooth. This server enables your G-Shock to connect and set its correct time. In addition, it displays some information about your watch.

***

## Features

- **BLE server** for configuration and communication  
- **Synchronization** of time, alarms, reminders, and notifications  
- **Touch and display support** (ST7789 LCD)  
- **Battery and temperature display**  
- **Persistent configuration storage**  
- **Utilities** for file sync and device management  

***

## Project Structure

- `main.py` – Main entry point for the ESP32 server  
- `config_server.py` – Configuration server used to connect to the supporting Android app and receive configuration information  
- `gshock_server.py` / `gshock_server_no_display.py` – Main G-Shock server logic (with/without display)  
- `lib/` – Core libraries:  
  - `display/` – Display and LED control (ST7789, fonts, icons)  
  - `config/` – Configuration management  
  - `gshock_api/` – Software to connect and communicate with G-Shock watches  
  - `utils/` – Utility functions and persistent storage  

***

## Requirements

- `ESP32-C6-Touch-LCD-1.47` micro controller with a touch-enabled display.  
- MicroPython firmware  
- `mpremote` for file transfer  

***

## Hardware

The currently supported hardware is `ESP32-C6-Touch-LCD-1.47`. Make sure it is exactly this display, because pins differ for similar displays, even from the same manufacturer. Also, the `touch` function is used to wake up the display, so make usre it is exactly the same model. You can get it from [here](https://amzn.to/4m7SIr9).

![Alt Image](docs/ESP32-C6-Touch-LCD-1.47-02.jpg)

***

## Getting Started

### 1. Installing the Software

**Download the latest firmware:**  
Download the latest MicroPython firmware (.bin) file from [here](https://micropython.org/download/esp32/).  
The current version is **v1.26.0 (2025-08-09)**.  
On Linux, the port is typically `/dev/ttyACM0`.

**Install MicroPython Firmware:**  
Follow the standard instructions for erasing the flash and installing the firmware. Refer to the sources at the end for detailed steps.

**Deploy the Server Software:**  
Sync project files to the ESP32:
```
python sync.py
```

***

### 2. Configure WiFi

#### Manual Installation

Create a `config.json` file with your WiFi credentials and timezone:
```
{
  "ssid": "YourWiFiSSID",
  "password": "YourWiFiPassword",
  "timezone": "Continent/City"
}
```
Copy the file to the device:
```
mpremote connect /dev/ttyACM0 fs cp config.json :config.json
```

#### Using the Android App

- Download the Android APK: [⬇️ Download Latest APK](https://github.com/izivkov/gshock-api-esp32/releases/download/v1.0.0/TimeServerConfigurator.apk)
- If not configured, the ESP32 will boot into configuration mode. Once booted, start the Android app. When the red dot at the bottom-right of the app’s screen turns green, the ESP32 controller is connected.
- Enter your SSID and WiFi password, then press **SUBMIT**. This will create the configuration file on the ESP32, and the device will reboot into server mode.

![Alt Image](docs/TimeServerConfigurator.png)

> Note: In the future, the app will provide locale information such as date and time format, temperature units (C or F), and color scheme for the server. It is recommended to use the app for setup.

***

### 3. Run the Server

After setup, the ESP32 will start the main server and display the status.

***

### 4. Connecting Your Watch to Set the Correct Time

Three ways to connect the watch to the server:

1. **Automatic connection:** If your watch is set to auto-update time, it will try to connect four times per day and update its time.
2. **Manual (time only):** For a quick time update, short-press the lower-right button on your watch. The watch will connect, update its time, and the display on the server will show the name of the last connected watch and the time of the last sync.
3. **Manual with watch information:** Long-press the lower-left button. The watch will connect and update its time. Additionally, the server will display information such as the next alarm, next reminder, battery level, and temperature of the watch.

***

## License

MIT License  
Copyright © Ivo Zivkov

***

## Source Files

For more details, see the project modules:  
- `gshock_server.py`  
- `main.py`  
- `display.py`  
- `gshock_api.py`  
- `config_manager.py`  

***

## References

- [MicroPython Download](https://micropython.org/download/esp32/)
- [MicroPython ESP32 Getting Started](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
- [Install MicroPython on ESP32](https://bhave.sh/micropython-install-esp32/)
- [Flashing Firmware with esptool.py](https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/)
- [Erase ESP32 Flash](https://randomnerdtutorials.com/esp32-erase-flash-memory/)
- [Troubleshooting Erase/Flash Issues](https://github.com/orgs/micropython/discussions/13025)

Additional resources:  
(https://visualgdb.com/documentation/espidf/)  
(https://randomnerdtutorials.com/esp32-web-server-beginners-guide/)  
(https://www.scribd.com/document/830747162/the-complete-esp32-projects-guide-ebook-1)  
(https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)  
(https://docs.nordicsemi.com/bundle/ncs-2.0.2/page/zephyr/boards/xtensa/esp32/doc/index.html)  
(https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/esp-hardware-design-guidelines-en-master-esp32.pdf)  
(https://github.com/izivkov/CasioGShockSmartSync)  
(https://www.waveshare.com/wiki/ESP32-S3-Relay-6CH)  
(https://docs.keyestudio.com/projects/KS5020/en/latest/docs/1.%20Arduino_C_Tutorial.html)  
(https://randomnerdtutorials.com/getting-started-with-esp32/)  

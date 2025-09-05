Here is a corrected and properly formatted `README.md` for your ESP32 G-Shock Server project.  
All spelling errors, grammar issues, and section inconsistencies have been addressed, and proper Markdown syntax is used throughout.

***

# ESP32 G-Shock Server & Display Interface

This project provides an **ESP32-based server and display interface** for Casio G-Shock watches. It enables BLE communication, configuration, notifications, reminders, alarms, and display management for supported G-Shock models.

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

- ESP32 board with ST7789 display  
- MicroPython firmware  
- `mpremote` for file transfer  

***

## Hardware

- ESP32 board with ST7789 display  

***

## Getting Started

### 1. Installing the Software

**Download the latest firmware:**  
Follow instructions to download the latest MicroPython firmware (.bin) file from [here](https://micropython.org/download/esp32/). The current version is **v1.26.0 (2025-08-09)**. Note that the port for Linux is typically `/dev/ttyACM0`.

**Install MicroPython Firmware:**  
Follow the standard instructions for erasing flash and installing the firmware. Refer to sources at the end for detailed steps.

**Deploy the Server Software:**  
Sync project files to the ESP32:
```sh
python sync.py
```

***

### 2. Configure WiFi

#### Manual Installation

Create a `config.json` file with your WiFi credentials and timezone:
```json
{
  "ssid": "YourWiFiSSID",
  "password": "YourWiFiPassword",
  "timezone": "Continent/City"
}
```
Copy to the device:
```sh
mpremote connect /dev/ttyACM0 fs cp config.json :config.json
```

#### Use the Android App

- Download the Android APK from ![here](docs/TimeServerConfigurator.apk).
- If not configured, the ESP32 will boot into configuration mode. Once booted, start the Android app. You should see the red dot on the bottom-right of the app's screen turn green, confirming a successful connection to the ESP32 controller.
- Enter your SSID and WiFi password, then press the **SUBMIT** button. This will create the configuration file on the ESP32, and the device will reboot into server mode.

![Alt Image](docs/TimeServerConfigurator.png)

***

### 3. Run the Server

After setup, the ESP32 will start the main server and display status.

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

[MicroPython Download](https://micropython.org/download/esp32/)  
[MicroPython ESP32 Getting Started](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)  
[Install MicroPython on ESP32](https://bhave.sh/micropython-install-esp32/)  
[Flashing Firmware with esptool.py](https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/)  
[Erase ESP32 Flash](https://randomnerdtutorials.com/esp32-erase-flash-memory/)  
[Troubleshooting Erase/Flash Issues](https://github.com/orgs/micropython/discussions/13025)

[1](https://visualgdb.com/documentation/espidf/)
[2](https://randomnerdtutorials.com/esp32-web-server-beginners-guide/)
[3](https://www.scribd.com/document/830747162/the-complete-esp32-projects-guide-ebook-1)
[4](https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)
[5](https://docs.nordicsemi.com/bundle/ncs-2.0.2/page/zephyr/boards/xtensa/esp32/doc/index.html)
[6](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/esp-hardware-design-guidelines-en-master-esp32.pdf)
[7](https://github.com/izivkov/CasioGShockSmartSync)
[8](https://www.waveshare.com/wiki/ESP32-S3-Relay-6CH)
[9](https://docs.keyestudio.com/projects/KS5020/en/latest/docs/1.%20Arduino_C_Tutorial.html)
[10](https://randomnerdtutorials.com/getting-started-with-esp32/)
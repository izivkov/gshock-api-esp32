Certainly! Here is your reformatted `README.md` file with clear titles, subtitles, and consistent structure.

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
- `config_server.py` – BLE configuration server  
- `gshock_server.py` / `gshock_server_no_display.py` – Main G-Shock server logic (with/without display)  
- `lib/` – Core libraries:  
  - `display/` – Display and LED control (ST7789, fonts, icons)  
  - `config/` – Configuration management  
  - `gshock_api/` – BLE protocol, alarms, reminders, notifications, and watch info  
  - `utils/` – Utility functions and persistent storage  

***

## Hardware

- ESP32 board with ST7789 display

***

## Getting Started

### 1. Installing the Software

**Download the latest firmware** (.bin file) from here:  
[https://micropython.org/download/ESP32_GENERIC_C6/](https://micropython.org/download/ESP32_GENERIC_C6/)  
The current version is **v1.26.0 (2025-08-09)**.

#### Flashing and Installing MicroPython

##### Step 1: Download the Firmware

- Download the MicroPython `.bin` file for ESP32, e.g.  
  `ESP32_GENERIC_C6-20250809-v1.26.0.bin` from the official MicroPython site.[1][2]

##### Step 2: Connect ESP32 to Computer

- Use a USB cable to connect your ESP32 board to your computer.[3]

##### Step 3: Install esptool (Flash Utility)

- Install the Python tool called `esptool` (for erasing and flashing the board):
  - `pip install esptool`  
  - Or: `pipx install esptool`.[3]

##### Step 4: Put the ESP32 in Bootloader Mode

- Most boards auto-enter flashing mode when reset.
- Some may require you to press and hold the **BOOT/FLASH** button while resetting or plugging in the board.[4][3]

##### Step 5: Erase the Flash Memory (Recommended)

- Open a terminal and navigate to your `.bin` file:
  ```
  cd ~/Downloads
  ```
- Run the erase command:
  ```
  esptool.py --chip esp32 erase_flash
  ```
- If needed, specify the port, e.g. `/dev/ttyUSB0` (Linux/Mac) or `COM7` (Windows):
  ```
  esptool.py --chip esp32 --port COM7 erase_flash
  ```
- Hold the BOOT/FLASH button until erasing starts.[5][4]

##### Step 6: Flash the MicroPython Firmware

- Run:
  ```
  esptool.py --chip esp32 --port COM7 write_flash -z 0x1000 ESP32_GENERIC_C6-20250809-v1.26.0.bin
  ```
- Replace `COM7` with your board's serial port. Hold BOOT/FLASH until writing starts, then release.[4][3]

##### Step 7: Confirm the Installation

- After flashing, connect to ESP32 using:
  - a serial terminal (PuTTY, screen, minicom)
  - or MicroPython-specific tools (`mpremote`)
- The REPL prompt (`>>>`) should appear. Type:
  ```python
  import sys
  print(sys.implementation)
  ```
- Outputs “micropython” and version number.[3]

***

## Troubleshooting Tips

- If errors occur during erasing or flashing, repeat the steps, verify the COM port, and ensure the BOOT/FLASH button is properly pressed.[6]
- For multiple serial devices, specify the exact port.[3]

***

## MicroPython Installation Summary Table

| Step                | Command/Action                                                        | Details                           |
|---------------------|----------------------------------------------------------------------|-----------------------------------|
| Download firmware   | Get .bin file                                                        | Official site [1]             |
| Install esptool     | `pip install esptool`                                                | Or use pipx [3]               |
| Connect ESP32       | USB cable                                                            |                                   |
| Erase flash         | `esptool.py --chip esp32 erase_flash`                                | Use port if needed                |
| Flash firmware      | `esptool.py --chip esp32 --port COM7 write_flash -z 0x1000 <bin>`    | Specify your port                 |
| Test connection     | Open serial terminal, look for REPL                                  |                                   |

***

## Configuration & Deployment

### 1. Configure WiFi

Create a `config.json` file with WiFi credentials and timezone:
```json
{
  "ssid": "YourWiFiSSID",
  "password": "YourWiFiPassword",
  "timezone": "Continent/City"
}
```
Copy to device:
```sh
mpremote connect /dev/ttyACM0 fs cp config.json :config.json
```

### 2. Deploy Code

Sync project files to the ESP32:
```sh
python sync.py
```

### 3. Run the Server

After setup, the ESP32 will start the main server and display status, alarms, and notifications.

***

## Requirements

- ESP32 board with ST7789 display
- MicroPython firmware
- `mpremote` for file transfer

***

## License

MIT License  
Copyright © Ivo Zivkov

***

For more details, see the source files:  
- `gshock_server.py`  
- `main.py`  
- `display.py`  
- `gshock_api.py`  
- `config_manager.py`

[1](https://micropython.org/download/esp32/)
[2](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
[3](https://bhave.sh/micropython-install-esp32/)
[4](https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/)
[5](https://randomnerdtutorials.com/esp32-erase-flash-memory/)
[6](https://github.com/orgs/micropython/discussions/13025)
This project provides an ESP32-based server and display interface for Casio G-Shock watches. It enables BLE communication, configuration, notifications, reminders, alarms, and display management for supported G-Shock models.

## Features

- BLE server for configuration and communication
- Synchronization of time, alarms, reminders, and notifications
- Touch and display support (ST7789 LCD)
- Battery and temperature display
- Persistent configuration storage
- Utilities for file sync and device management

## Project Structure

- main.py – Main entry point for the ESP32 server
- config_server.py – BLE configuration server
- gshock_server.py / gshock_server_no_display.py – Main G-Shock server logic (with/without display)
- lib – Core libraries:
  - `display/` – Display and LED control (ST7789, fonts, icons)
  - `config/` – Configuration management
  - `gshock_api/` – BLE protocol, alarms, reminders, notifications, and watch info
  - `utils/` – Utility functions and persistent storage

## Hardware

## Getting Started

1. **Installing the software on your device**

- Download the latest firmware .bin file from here: https://micropython.org/download/ESP32_GENERIC_C6/. The current version is v1.26.0 (2025-08-09) .bin

The steps to flash and install **MicroPython v1.26.0** on an ESP32 are as follows:

### 1. Download the Firmware
- Get the MicroPython .bin file for ESP32, e.g.  
  **ESP32_GENERIC_C6-20250809-v1.26.0.bin** from the official MicroPython site.[1][2]

### 2. Connect ESP32 to Computer
- Use a USB cable to connect your ESP32 board to your computer.[3]

### 3. Install esptool (Flash Utility)
- Install the Python tool called `esptool` (used for erasing and flashing the board).
- It is recommended to use an isolated environment via pipx (not required, but safer):
  - `pip install esptool`  
  - Or: `pipx install esptool`.[3]

### 4. Put the ESP32 in Bootloader Mode
- Most boards auto-enter flashing mode when reset, but some may require you to:
  - Press and hold the **BOOT/FLASH** button while resetting or plugging in the board.[4][3]

### 5. Erase the Flash Memory (Recommended)
- Open a terminal (use Command Prompt or PowerShell on Windows; Terminal on Mac/Linux).
- Change directory to where your .bin file is located:
  ```
  cd ~/Downloads
  ```
- Run the erase command:
  ```
  esptool.py --chip esp32 erase_flash
  ```
  - If needed, specify the port (e.g., `/dev/ttyUSB0` for Linux/Mac or `COM7` for Windows):
  ```
  esptool.py --chip esp32 --port COM7 erase_flash
  ```
- Hold the BOOT/FLASH button until erasing starts.[5][4]

### 6. Flash the MicroPython Firmware
- Run the firmware flashing command:
  ```
  esptool.py --chip esp32 --port /dev/ttyAMC0 write_flash -z 0x1000 ESP32_GENERIC_C6-20250809-v1.26.0.bin
  ```
  - Replace `COM7` with your board's serial port name.
- Hold BOOT/FLASH until writing starts, then release.[4][3]

### 7. Confirm the Installation
- After flashing, connect to the ESP32 using:
  - a serial terminal (like PuTTY, screen, minicom)
  - or MicroPython-specific tools like `mpremote`
- The REPL prompt (`>>>`) should appear. Type:
  ```python
  import sys
  print(sys.implementation)
  ```
  - This should show “micropython” and the version number.[3]

## Troubleshooting Tips

- If you see errors during erasing/flashing, repeat steps and make sure the correct COM port is chosen and the BOOT/FLASH button is held down.[6]
- If you have multiple serial devices, always specify the exact port.[3]

## Summary Table

| Step                | Command/Action                                                        | Details                    |
|---------------------|----------------------------------------------------------------------|----------------------------|
| Download firmware   | Get .bin file                                                        | From official site [2] |
| Install esptool     | `pip install esptool`                                                | Or use pipx [3]        |
| Connect ESP32       | USB cable                                                            |                            |
| Erase flash         | `esptool.py --chip esp32 erase_flash`                                | Use port if needed         |
| Flash firmware      | `esptool.py --chip esp32 --port COM7 write_flash -z 0x1000 <bin>`    | Specify your port          |
| Test connection     | Open serial terminal, look for REPL                                  |                            |

These exact steps will install the latest MicroPython firmware on your ESP32 board.[1][4][3]

[1](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
[2](https://micropython.org/download/esp32/)
[3](https://bhave.sh/micropython-install-esp32/)
[4](https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/)
[5](https://randomnerdtutorials.com/esp32-erase-flash-memory/)
[6](https://github.com/orgs/micropython/discussions/13025)
[7](https://randomnerdtutorials.com/flash-upload-micropython-firmware-esp32-esp8266/)
[8](https://www.espboards.dev/blog/micropython-esp32-getting-started/)
[9](https://www.instructables.com/ESP32-Getting-Started-MicroPython-on-Board-Blink-L/)
[10](https://micropython.org/download/)
[11](https://core-electronics.com.au/guides/flash-MicroPython-onto-esp32/)
[12](https://www.youtube.com/watch?v=YemfdxOXaes)
[13](https://github.com/orgs/micropython/discussions/10206)
[14](https://www.hackster.io/fusion_automate/flash-micropython-firmware-in-seed-studio-xiao-esp32c3-80ed84)
[15](https://docs.arduino.cc/micropython)
[16](https://shop.m5stack.com/blogs/news/how-to-erase-esp32-flash-memory)
[17](https://georgefreedom.com/ignition-sequence-how-to-flash-micropython-onto-your-esp32)
[18](https://micropython.org/download/ESP32_GENERIC_C3/)
[19](https://ishanmalviya.com/esp32-8266-clearing-flash-and-updating-firmware-for-micropython-d7a553ec3732)
[20](https://www.donskytech.com/how-to-install-micropython-on-esp32-and-download-firmware/)

2. **Configure WiFi**  
   Create a `config.json` file with your WiFi credentials and timezone:
   ```json
   {
     "ssid": "YourWiFiSSID",
     "password": "YourWiFiPassword",
     "timezone": "Continent/City"
   }
   ```
   Copy it to the device:
   ```sh
   mpremote connect /dev/ttyACM0 fs cp config.json :config.json
   ```

2. **Deploy Code**  
   Use sync.py to copy project files to your ESP32:
   ```sh
   python sync.py
   ```

3. **Run the Server**  
   The ESP32 will start the main server and display status, alarms, and notifications.

## Requirements

- ESP32 board with ST7789 display
- MicroPython firmware
- `mpremote` for file transfer

## License

MIT License  
Copyright © Ivo Zivkov

---

For more details, see the source files:  
- gshock_server.py
- main.py  
- display.py  
- gshock_api.py  
- config_manager.py
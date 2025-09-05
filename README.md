Collecting workspace information# G-Shock Smart Sync ESP32 Project

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

## Getting Started

1. **Configure WiFi**  
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
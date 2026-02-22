# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

An ESP32-based BLE time server written in **MicroPython** that syncs time to Casio G-Shock watches. The code runs directly on an ESP32-C6 microcontroller — not on a host machine. All Python code targets the MicroPython runtime, which means:
- Use `uasyncio` (not `asyncio`), `ujson` (not `json`), `utime` (not `time`) unless already imported under those aliases
- No standard library features unavailable in MicroPython (no `threading`, no `subprocess`, etc.)
- Memory is constrained; `gc.collect()` calls are intentional

## Deploying to Device

```bash
# Install deployment tool
pip install mpremote

# Sync all project files to the ESP32 (connected via USB at /dev/ttyACM0)
python sync.py

# Backup config before syncing
mpremote cp :config.json config.json
python sync.py

# Run a script directly without flashing (useful for testing)
mpremote run gshock_server.py

# Copy a single file
mpremote connect /dev/ttyACM0 fs cp config.json :config.json
```

`sync.py` copies all `.py`, `.mpy`, and `.json` files from the project root to the ESP32, deleting any files on the device that no longer exist locally. It skips `.git`, `__pycache__`, `.vscode`, and `.DS_Store`.

## Linting

```bash
ruff check .
```

Files excluded from ruff (third-party display drivers): `lib/display/st7789_base.py`, `lib/display/st7789_ext.py`, `lib/display/st7789_ext_small.py`, and `di.py`.

## Configuration

The device reads `config.json` from its filesystem. Required keys: `ssid`, `password`, `timezone`. Optional keys: `dateformat`, `timeformat`, `foreground_color`, `background_color`, `temperature_unit`. If config is missing or incomplete, the device boots into config mode (BLE peripheral named `"TimeServer"`) to receive config from the Android app.

## Architecture

### Startup Flow (`main.py`)
1. `config_manager.load()` — reads `config.json` from device flash
2. If WiFi credentials missing → start `config_server` (BLE peripheral for Android app)
3. If configured → `init()` sets time via NTP, starts display dimmer, then launches:
   - `gshock_server.main()` — main watch sync loop
   - `log_server.main()` — BLE log service for Android app
   - `watch_boot_button()` — watches the BOOT button (GPIO 9) to switch to config mode at any time

### Three Concurrent Server Modes
- **`gshock_server.py`**: Central BLE scanner. Scans for G-Shock watches (identified by UUID `0x1804`), connects as GATT client, sets the time, reads watch data (alarms, reminders, battery, temperature) on lower-left long-press.
- **`config_server.py`**: BLE peripheral. Advertises as `"TimeServer"`, receives a length-prefixed JSON config blob from the Android app, saves it to `config.json`, and reboots.
- **`log_server.py`**: BLE peripheral. Advertises as `"ESP32_Logger"` with service UUID `0x1001`. On `"START"` command, sends stored activity logs to the connected Android app.

### `lib/gshock_api/` — Watch Communication Library
The core BLE protocol layer. Each watch feature has a dedicated IO class in `lib/gshock_api/iolib/`:
- Each IO class has a `request(connection, ...)` coroutine (sends command, returns an awaitable result) and an `on_received(data)` static method (handles BLE notification callbacks)
- `message_dispatcher.py` routes incoming BLE notifications to the correct IO handler based on the first byte of data (the characteristic identifier)
- `connection.py` (`Connection`) manages the BLE GATT client: scanning, connecting, subscribing to notifications, and writing characteristics. All watch communication uses handle-to-UUID mapping (`init_handles_map`)
- `data_listener.py` (`DataListener`) subscribes to BLE characteristics and dispatches notifications to `MessageDispatcher`

### `di.py` — Dependency Injection
Imports `display`, `touch`, and `led`/`LEDController` from `lib/display/`. This is the single place where hardware-specific modules are imported. Other files import from `di` rather than directly from display modules to allow swapping hardware.

### Display Subsystem (`lib/display/`)
- `display.py` — main display controller (ST7789 LCD)
- `led.py` — RGB LED controller with modes: `MODE_PULSATE_GREEN` (idle), `MODE_SMOOTH` (connecting), `MODE_BLINK_BLUE` (config mode), `MODE_BLINK_RED` (error)
- `dim_display.py` — dims display after 5 min, turns off after 30 min; touch wakes it
- `touch.py` — touch input for waking the display

### `lib/config/network_time_setter.py`
Connects to WiFi, syncs time via NTP (worldtimeapi.org), sets the MicroPython RTC, then disconnects WiFi. Called once at startup and every 6 hours via `PeriodicTaskRunner`.

### `lib/utils/persistent_store.py`
Lightweight key-value store persisted to flash. Used to remember `watch_name` and `last_connected` across reboots.

### Watch Button Semantics
- `LOWER_RIGHT` short-press → time set only (quick sync)
- `LOWER_LEFT` long-press → time set + fetch and display watch data (alarms, reminders, battery, temp)
- `NO_BUTTON` → automatic periodic sync initiated by the watch itself

# Changelog

## [1.1.0] - 2026-02-22

### Added
- Configurable time offset (`"offset"` key in `config.json`) to compensate for ESP32 lag when syncing watch time
- Per-watch sync history: the idle screen now lists all known watches with their last sync time, persisted across reboots
- Activity log persisted to flash (`activity_log.json`), survives reboots, capacity raised from 10 to 50 entries
- Live clock on idle screen, refreshed every 30 seconds
- Project name, current time and version shown on the header line of the watches list screen
- `version.py` introducing `__version__` and `__project__` constants
- `sync.py` now preserves runtime device files (`gshock_server_data.json`, `activity_log.json`) across code updates

### Changed
- Welcome screen (no watches yet) split into two lines with timezone and version below, all vertically centered
- Watches list screen always redrawn after every connection (previously stuck on watch detail screen after a LOWER_LEFT long-press)
- Watch history and activity log survive reboots and code syncs

---

## [1.0.0] - 2025-12-01

### Added
- BLE time server for Casio G-Shock watches (central role scanner)
- NTP time sync via WiFi, with timezone support (worldtimeapi.org)
- ST7789 LCD display support (ESP32-C6-Touch-LCD-1.47)
- RGB LED status indicator (ESP32 Super Mini C6)
- Configuration mode via BOOT button and Android app (BLE peripheral)
- Activity log streamed to Android app over BLE
- Display auto-dim (5 min) and auto-off (30 min) with touch wake
- Support for GW-B5600, GMW-B5000, GA-B2100, GST-B500, and many more G-Shock models

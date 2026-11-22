# Flock ALPR Detector (ESP32-S3)

**Status:** Prototype
**Category:** Wireless reconnaissance, privacy research
**Language:** MicroPython

## Summary

A **passive** scanner for an ESP32-S3 that detects nearby Flock Safety automated license plate reader (ALPR) cameras from their Wi-Fi and Bluetooth LE signals. It only listens. It never transmits, connects, or interferes with anything.

## How it detects cameras

| Path | Signals checked |
|---|---|
| Wi-Fi scan (every 4 s) | SSIDs containing `flock`, `flck`, `penguin`, `pigvision`, plus known MAC prefixes (OUIs) |
| BLE scan (continuous) | Device names like `Penguin-…` and `FS Ext Battery`, manufacturer ID `0x09C8`, and the same MAC prefixes |

Each hit is scored **high / medium / low** confidence:

- A Flock-specific OUI (`b4:1e:52`) or a matching name scores high.
- Generic chip-vendor OUIs score low, because they show up on lots of non-Flock hardware.
- Manufacturer ID `0x09C8` on its own only counts as medium, because it causes false positives without a second matching signal.
- Randomized (locally administered) BLE MACs are excluded from OUI matching.

## Output

- Serial log: confidence, protocol, MAC, RSSI, hit count, and the reasons that matched
- `flock_log.csv` on the board's flash, rotated at 200 KB
- Onboard RGB LED: red for high, amber for medium, blue for low
- Optional piezo buzzer

## Usage

1. Flash MicroPython for the ESP32-S3.
2. `mpremote cp flock_detect.py :main.py`
3. Set `LED_PIN` (48 or 38, depending on DevKitC revision) and `BUZZER_PIN` at the top of the file.
4. Watch the serial output.

## Limits and lessons

- **Stock MicroPython can't sniff probe requests.** Its Wi-Fi scan only sees access points that are broadcasting. C firmware (for example [flock-you](https://github.com/colonelpanichacks/flock-you)) uses promiscuous mode to catch camera probe requests too, so it detects more.
- **Signatures drift.** The OUI list is short on purpose, with only verified prefixes. Refresh it from the community repos.
- **Picking the platform:** I first looked at NanoPy (the Oxocard scripting language). Its API has no Wi-Fi or BLE scanning functions, so it can't do this job. That's why this version uses MicroPython.

## Credits

Detection signatures come from community research: [colonelpanichacks/flock-you](https://github.com/colonelpanichacks/flock-you) and [DeflockJoplin/flock-you](https://github.com/DeflockJoplin/flock-you).

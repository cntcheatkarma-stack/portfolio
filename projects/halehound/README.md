# HaleHound CYD Build

**Status:** In progress
**Category:** Hardware, RF security research
**Firmware:** [HaleHound-CYD](https://github.com/JesseCHale/HaleHound-CYD), `esp32-e32r35t` target

## Summary

A handheld wireless security multitool built on a 3.5" "Cheap Yellow Display" (CYD) ESP32 board running HaleHound firmware. I upgraded it with amplified sub-GHz and 2.4 GHz radio modules, NFC, and GPS. The goal is a portable platform for studying how common wireless protocols behave and how to defend them.

**Docs in this folder:**
- [Wiring reference](wiring-reference.md): pin maps, power design, connector breakouts, and the full troubleshooting log
- [gps_set_9600.ino](gps_set_9600.ino): sketch that resets the GPS module to 9600 baud

## Hardware

| Part | Role |
|---|---|
| ESP32-3248S035 (3.5" CYD, ST7796 320×480) | Main controller and touchscreen UI |
| Ebyte E07-433M20S (CC1101, 16-pin, 20 dBm PA) | Sub-GHz radio |
| Ebyte E01-2G4M27SX (nRF24L01+ with PA/LNA) | 2.4 GHz radio |
| PN532 V3 | NFC / RFID (SPI mode) |
| ATGM336H GPS + 28 dB active patch antenna | Location (GPS + BeiDou) |
| 5V to 3.3V buck converter | Dedicated power rail for the PA radio modules |
| PETG enclosure | Case. PETG is transparent to GPS, so the antenna can mount inside |
| Rd-01 24 GHz mmWave radar | Planned addition (firmware support already present) |

I chose the amplified Ebyte modules over the basic CC1101 and nRF24L01 boards for their range and receive sensitivity. All three SPI devices share the ESP32's VSPI bus (SCK 18, MOSI 23, MISO 19), and each has its own chip-select line.

## Engineering highlights

### 1. Power design for two PA radios

Both radio modules pull short, high-current spikes when they transmit; the E01 pulls about 100–115 mA. The CYD's onboard 3.3 V regulator can't supply two amplified radios, so the rail sagged and the modules browned out. I fixed it by:

- Feeding the radio VCC lines from a separate 5V→3.3V buck converter, tapped from USB 5V before the CYD's regulator
- Tying all grounds together so the SPI bus keeps a shared reference
- Soldering decoupling capacitors (10–100 µF) directly across each module's VCC/GND pins

### 2. Debugging "radio not detected" and "TX error"

After the upgrade, the E01 reported transmit errors and the CC1101 wasn't detected. I worked through the causes methodically:

| Symptom | Root cause found / ruled out |
|---|---|
| E01 TX error | Power sag under PA transmit current. Fixed by the decoupling cap and the dedicated rail. |
| CC1101 not detected | The 16-pin E07-433M20S has **VCC on pin 11, not pin 2** like the 8-pin version. Wiring from an 8-pin diagram puts 3.3 V on MOSI. |
| nRF `CONFIG` reads `0x08`, expected `0x0E` | The chip can be read but writes don't stick: either MOSI isn't reaching it, or the chip resets on power-up (brownout). Diagnosed by reading `SETUP_AW` (expect `0x03`) and `RF_CH` (expect `0x02`). |
| Wrong pins driven | The resistive (E32R35T) and capacitive (CYD35C) boards need different firmware binaries. |
| Shared-bus contention | Tested each radio alone to rule out one module holding the bus. |

### 3. Pin conflicts on the 3.5" board

- The PN532's SS line and the nRF24's IRQ both want GPIO 17. HaleHound polls the nRF24 over SPI, so I left its IRQ disconnected.
- On the 3.5" board, CC1101 CS moves to GPIO 21, because GPIO 27 drives the backlight.
- GPIO 16/17 are repurposed from the RGB LED, and GPIO 26 from the speaker pad.

### 4. Other fixes

- **GPS sending bytes but no NMEA sentences:** HaleHound reads GPS at a fixed 9600 baud. I wrote a sketch that tries common baud rates and sends the `$PCAS01` command to switch the module to 9600 and save it.
- **Dead microSD slot** (the spring mechanism failed): I wired an external microSD module to the shared SPI bus on CS GPIO 5.
- **Lifted pads:** tin first, tack the wire in about 2 seconds, strain-relieve the harness with hot glue, and solder to the WROOM module's pins when a pad is gone.

## What I learned

- Check power integrity first, before you suspect firmware or wiring.
- Isolate one variable at a time when two faults show up together.
- Read datasheets closely. Near-identical part numbers can have different pinouts.
- Run a continuity "bridge checklist" (MOSI↔MISO, GPIO16↔17, VCC↔GND) before every power-up on fine-pitch work.

## Responsible use

I use this device only for learning and for testing equipment I own or am authorized to test. Radio transmission is regulated (by the FCC in the US), and interfering with or accessing other people's devices without permission is illegal.

## To do

- [ ] Handle the E07 PA/LNA enable pins (TX_EN / RX_EN) before trusting sub-GHz transmit
- [ ] Integrate the Rd-01 mmWave radar
- [ ] Add build photos

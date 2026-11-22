# HaleHound Wiring Reference (3.5" CYD)

Wiring tables, power design, and the troubleshooting log for this build.
**Board target:** `esp32-e32r35t`, ST7796 320×480.
Pin assignments come from the official [HaleHound-CYD README](https://github.com/JesseCHale/HaleHound-CYD) (v3.9.5). Always match your board's silkscreen; a few pins differ between the resistive E32R35T and capacitive 3248S035C boards.

---

## A1. Radios → CYD (shared VSPI bus)

The CC1101, nRF24 and PN532 share one VSPI bus. Each has its own chip-select, so the firmware talks to one at a time.

**Shared by all three modules**

| Module pin | CYD pin | Note |
|---|---|---|
| SCK | GPIO 18 | VSPI clock |
| MOSI | GPIO 23 | VSPI data out |
| MISO | GPIO 19 | VSPI data in |
| VCC | 3.3V | Radios: from the dedicated buck rail (A5) |
| GND | GND | Common ground |

**Per-module control pins**

| Module | Signal | CYD pin |
|---|---|---|
| CC1101 | CS | GPIO 21 (3.5" board) |
| CC1101 | GDO0 (TX) | GPIO 22 |
| CC1101 | GDO2 (RX) | GPIO 35 |
| nRF24 | CSN | GPIO 26 (3.5" board) |
| nRF24 | CE | GPIO 16 |
| nRF24 | IRQ | GPIO 17, but leave it unconnected |
| PN532 | SS | GPIO 17 |

> **Watch out:**
> - The PN532 SS and the nRF24 IRQ both want GPIO 17. HaleHound never uses the nRF24 interrupt, so leave that IRQ disconnected.
> - CC1101 CS uses GPIO 21, because GPIO 27 is the backlight on the 3.5" board.
> - Set the PN532 DIP switches to CH1 OFF, CH2 ON (SPI mode).

---

## A2. CC1101: E07-433M20S (16-pin, 20 dBm PA)

The pin order is different from the 8-pin E07-M1101D. Wire by the module's silkscreen labels, not by pad position.

| Pin | Function | CYD pin |
|---|---|---|
| 1 | GND | GND |
| 2 | MOSI | GPIO 23 |
| 3 | SCK | GPIO 18 |
| 4 | MISO / GDO1 | GPIO 19 |
| 5 | GDO2 | GPIO 35 (RX) |
| 6 | GDO0 | GPIO 22 (TX) |
| 7 | CSN | GPIO 21 |
| 8 | TX_EN | PA enable (see note) |
| 9 | RX_EN | LNA enable (see note) |
| 10 | NC | Leave unconnected |
| 11 | VCC | 3.3V. Never 5V; the maximum is 3.6V |
| 12 | GND | GND |
| 13 | ANT | Antenna (not ground) |
| 14–16 | GND | GND (RF grounds) |

> **Watch out:**
> - **VCC is pin 11, not pin 2.** Pin 2 is MOSI. Wiring from an 8-pin diagram leaves the chip unpowered and puts 3.3V on MOSI, which shows up as "not detected."
> - **TX_EN and RX_EN switch the PA/LNA.** Stock HaleHound targets the non-PA M1101D and doesn't drive these pins. SPI detection can pass without them, but transmit and receive won't work properly until they're handled. This is still an open item.
> - Tie all the ground pins (1, 12, 14–16) to a solid common GND for RF stability.

---

## A3. nRF24: E01-2G4M27SX (PA + LNA)

A single row of 8 pads in the standard nRF24 pin order.

| Pin | Function | CYD pin |
|---|---|---|
| 1 | GND | GND |
| 2 | VCC | 3.3V. Over 3.6V kills it |
| 3 | CE | GPIO 16 |
| 4 | CSN | GPIO 26 |
| 5 | SCK | GPIO 18 |
| 6 | MOSI | GPIO 23 |
| 7 | MISO | GPIO 19 |
| 8 | IRQ | Leave unconnected |

- CE drives the LNA automatically as part of TX/RX switching.
- The module pulls about 100–115 mA when transmitting.

---

## A4. Decoupling capacitor

Solder it directly across each PA module's own VCC/GND pins, not at the CYD end of the wire.

- **Value:** 10 µF minimum; 47–100 µF electrolytic or tantalum is better.
- **Polarity:** stripe or short leg to GND. Optionally add a 0.1 µF ceramic in parallel for high-frequency noise.
- **Voltage rating:** 10 V or higher.

---

## A5. Separate power for the PA modules

Both radios are PA parts. The CYD's onboard 3.3V regulator can't supply both radios' transmit spikes, so it sags and they brown out.

```
USB 5V (before the CYD regulator) ──► Buck 5V→3.3V (500 mA+) ──► PA module VCC
                                                                 │ signals
CYD ESP32 (own 3.3V) ◄───────────────────────────────────────────┘
        └─────────── common ground: buck GND + PA GND + CYD GND ───────────┘
```

**Three rules**
1. Only VCC comes from the buck converter.
2. Tie all grounds together, or SPI loses its shared reference.
3. All signal lines still go to the ESP32 GPIOs as shown in A1.

---

## A6. Where the pins break out

| Connector | Pins | HaleHound use |
|---|---|---|
| CN1 | 3.3V · GND · GPIO 21 | Power + CC1101 CS |
| P3 (Extended IO) | GPIO 22 · 35 · 21 · GND | CC1101 GDO0 / GDO2 |
| Speaker pad | GPIO 26 · GND | nRF24 CSN (speaker disabled) |
| P1 (4-pin) | 5V · GND · GPIO 1 · 3 | GPS (UART0) |
| SPI header | 18 · 23 · 19 · 16 · 17 | SPI bus + nRF24 CE, PN532 SS |

- The SPI bus pins (18/23/19) are shared with the microSD slot.
- GPIO 16/17 are repurposed from the RGB LED.

---

## A7. Soldering directly to the ESP32-WROOM-32

If a pad lifts, solder straight to the module pins. Orient by the antenna edge (top); pin 1 (GND) is the top-left corner.

| Signal | GPIO | WROOM pin | Side |
|---|---|---|---|
| nRF24 CSN | IO26 | 11 | Left, lower third |
| CC1101 GDO0 | IO22 | 36 | Right, near top |
| PN532 SS | IO17 | 28 | Right (next to IO16) |
| nRF24 CE | IO16 | 27 | Right (next to IO17) |

Don't use the flash pins on the bottom edge.

---

## A8. Verify before closing the case

On the device, run **Tools → Radio Test**. It confirms each module is detected, so you catch cold joints before the lid goes on.

**GPS antenna placement**
- Mount the patch inside, flat against the rear shell, facing out.
- Add a 3–5 cm copper-tape ground plane behind the patch.
- Keep it at the opposite end from the radio antennas, and route the coax away from them.
- Leave slack on the u.FL cable so closing the case doesn't pull on it.

---

## A9. Troubleshooting log

### Pre-power bridge checklist (continuity: every one must be silent)
- MOSI (23) ↔ MISO (19). A bridge here kills all three radios at once.
- GPIO 16 ↔ GPIO 17 (adjacent pins). A bridge here takes out the nRF24 and PN532 together.
- Each module's VCC ↔ GND.

A continuity beep only proves the copper is intact. It won't catch a cold joint or a dead ESP32 output.

### GPS: data arrives but no NMEA sentences
- HaleHound reads GPS at a fixed 9600 baud.
- The ATGM336H outputs GPS + BeiDou, so its sentences start `$GN…` / `$GB…`.
- Fix: flash [gps_set_9600.ino](gps_set_9600.ino), power-cycle the GPS, then re-flash HaleHound.

### Dead microSD slot
- When the push-push slot loses its spring tension, it's mechanically dead.
- Workaround: add an external microSD module on the shared SPI bus with **CS on GPIO 5**.

### Lifted pads
- Tin the wire first and tack it in about 2 seconds. Don't hold the iron on a pad.
- Strain-relieve the harness with hot glue.
- If a non-power pad rips off, solder to the chip's own pin instead.

---

## A10. PA upgrade: E01 TX error and CC1101 not detected

**E01 TX error: power (high confidence)**
- PA transmit spikes brown the module out mid-packet.
- Add a cap at the module pins (A4) and feed the module from the buck rail (A5).
- Still failing? Drop the PA level to MIN/LOW in the firmware. If TX starts working, power is confirmed as the cause.

**CC1101 not detected: check in this order**
1. M20S pinout: VCC on pin 11 (A2).
2. Retest after adding the E01 cap, since both radios share the same sagging rail.
3. Wrong firmware binary: E32R35T and CYD35C use different pin maps.
4. Bus contention: unplug the E01 and test the CC1101 alone.
5. Wiring: CSN, SCK, MOSI, MISO.
6. Damage: the E07 is rated for 1.8–3.6V, so it's dead if it ever saw 5V.

"Not detected" means the version-register read over SPI failed, so GDO0/GDO2 and the antenna aren't the problem.

**nRF24 `CONFIG = 0x08`, "config didn't latch, needs 0x0E"**
- `0x08` is the reset value (CRC on). HaleHound writes `0x0E` (CRC on, 2-byte CRC, PWR_UP) and reads it back.
- Read `SETUP_AW` (0x03, expect `0x03`) and `RF_CH` (0x05, expect `0x02`):
  - **Every register reads `0x08`:** MOSI is dead. Every command byte arrives as `0x00`, which means "read CONFIG." Fix the wiring.
  - **Those read correctly but CONFIG won't hold:** writes work, so the chip is browning out on PWR_UP. Fix the power (A4/A5).
- Also check for a CSN or bus conflict (pull the SD card out) and try a slower SPI clock (1–2 MHz) with long jumper wires.

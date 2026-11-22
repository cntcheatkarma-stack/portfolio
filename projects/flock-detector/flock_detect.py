# flock_detect.py - Passive Flock Safety ALPR detector for ESP32-S3 (MicroPython)
#
# Listens only; never transmits deauths or connects to anything.
# Two detection paths:
#   1. WiFi beacon scan  -> SSID patterns + MAC OUI prefixes
#   2. BLE advert scan   -> device names, manufacturer ID 0x09C8, MAC OUI prefixes
#
# Signatures come from the community flock-you / DeFlock research. They drift over
# time, so refresh WIFI_OUIS / BLE_OUIS from the current repos when you can:
#   github.com/colonelpanichacks/flock-you
#   github.com/DeflockJoplin/flock-you
#
# Copy to the board as main.py (auto-run) or flock_detect.py, then watch serial.

import time
import network
import bluetooth
import machine

# ------------------------------------------------------------------ config ---
LED_PIN = 48            # ESP32-S3-DevKitC v1.0 onboard RGB = 48, v1.1 = 38. None to disable.
LED_IS_NEOPIXEL = True  # False if you wired a plain LED
BUZZER_PIN = None       # e.g. 3 for a passive piezo. None to disable.
WIFI_SCAN_EVERY_MS = 4000
ALERT_COOLDOWN_S = 30   # don't re-alert the same MAC more often than this
MIN_RSSI = -95          # ignore anything weaker
LOG_FILE = "flock_log.csv"
LOG_MAX_BYTES = 200_000

# ------------------------------------------------------------ signatures ----
# MAC prefixes (first 3 bytes, lowercase). "high" = Flock-specific,
# "low" = generic chip vendor that also shows up on Flock hardware (noisy alone).
WIFI_OUIS = {
    "b4:1e:52": "high",   # Flock Safety's own IEEE block
    "e4:aa:ea": "med",    # Liteon - observed in Flock camera probes
    "82:6b:f2": "med",    # DeFlockJoplin addition
    "00:03:7f": "low",    # Qualcomm Atheros default radio MAC (firmware dump)
    # add more from the current flock-you list here
}
BLE_OUIS = dict(WIFI_OUIS)

SSID_KEYWORDS = ("flock", "flck", "penguin", "pigvision")
BLE_NAME_KEYWORDS = ("flock", "penguin", "fs ext battery", "pigvision")
BLE_MFG_IDS = {0x09C8: "XUNTONG (Flock BLE module)"}

# ------------------------------------------------------------- hardware -----
led = None
if LED_PIN is not None:
    if LED_IS_NEOPIXEL:
        import neopixel
        led = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)
    else:
        led = machine.Pin(LED_PIN, machine.Pin.OUT)

buzzer = machine.PWM(machine.Pin(BUZZER_PIN), freq=2000, duty_u16=0) if BUZZER_PIN is not None else None


def set_led(r, g, b):
    if led is None:
        return
    if LED_IS_NEOPIXEL:
        led[0] = (r, g, b)
        led.write()
    else:
        led.value(1 if (r or g or b) else 0)


def beep(level):
    if buzzer is None:
        return
    n = {"high": 3, "med": 2}.get(level, 1)
    for _ in range(n):
        buzzer.duty_u16(32768)
        time.sleep_ms(120)
        buzzer.duty_u16(0)
        time.sleep_ms(80)


# --------------------------------------------------------------- helpers ----
def fmt_mac(b):
    return ":".join("%02x" % x for x in b)


def oui_of(mac_str):
    return mac_str[:8]


def is_locally_administered(mac_bytes):
    return bool(mac_bytes[0] & 0x02)


def score(level):
    return {"high": 3, "med": 2, "low": 1}.get(level, 0)


def level_of(points):
    if points >= 3:
        return "high"
    if points == 2:
        return "med"
    return "low"


last_alert = {}
hits = {}


def log_line(line):
    try:
        import os
        try:
            if os.stat(LOG_FILE)[6] > LOG_MAX_BYTES:
                os.rename(LOG_FILE, LOG_FILE + ".old")
        except OSError:
            pass
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception as e:
        print("log error:", e)


def alert(proto, mac, rssi, reasons, extra, points):
    now = time.time()
    hits[mac] = hits.get(mac, 0) + 1
    if now - last_alert.get(mac, -9999) < ALERT_COOLDOWN_S:
        return
    last_alert[mac] = now
    lvl = level_of(points)
    t = time.ticks_ms() // 1000
    msg = "[%s] +%ds %-4s mac=%s rssi=%d hits=%d why=%s %s" % (
        lvl.upper(), t, proto, mac, rssi, hits[mac], "+".join(reasons), extra)
    print(msg)
    log_line("%d,%s,%s,%s,%d,%s,%s" % (t, lvl, proto, mac, rssi, "+".join(reasons), extra.replace(",", ";")))
    set_led(*{"high": (60, 0, 0), "med": (40, 20, 0), "low": (0, 0, 30)}[lvl])
    beep(lvl)


# ------------------------------------------------------------------ WiFi ----
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
try:
    wlan.disconnect()
except Exception:
    pass


def wifi_scan():
    try:
        results = wlan.scan()
    except OSError as e:
        print("wifi scan error:", e)
        return
    for ssid_b, bssid, ch, rssi, _sec, hidden in results:
        if rssi < MIN_RSSI:
            continue
        mac = fmt_mac(bssid)
        try:
            ssid = ssid_b.decode()
        except Exception:
            ssid = ""
        reasons, points = [], 0
        lvl = WIFI_OUIS.get(oui_of(mac))
        if lvl:
            reasons.append("oui_" + lvl)
            points += score(lvl)
        low = ssid.lower()
        if any(k in low for k in SSID_KEYWORDS):
            reasons.append("ssid")
            points += 3
        if reasons:
            alert("wifi", mac, rssi, reasons, 'ch=%d ssid="%s"%s' % (ch, ssid, " hidden" if hidden else ""), points)


# ------------------------------------------------------------------- BLE ----
_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6
ble_queue = []   # filled in IRQ, drained in main loop


def ble_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        if len(ble_queue) < 64:
            ble_queue.append((bytes(addr), rssi, bytes(adv_data)))
    elif event == _IRQ_SCAN_DONE:
        pass


def parse_adv(payload):
    name, mfg_ids = "", []
    i = 0
    while i + 1 < len(payload):
        ln = payload[i]
        if ln == 0 or i + ln >= len(payload):
            break
        t = payload[i + 1]
        val = payload[i + 2:i + 1 + ln]
        if t in (0x08, 0x09):
            try:
                name = val.decode()
            except Exception:
                pass
        elif t == 0xFF and len(val) >= 2:
            mfg_ids.append(val[0] | (val[1] << 8))
        i += 1 + ln
    return name, mfg_ids


def process_ble():
    while ble_queue:
        addr, rssi, adv = ble_queue.pop(0)
        if rssi < MIN_RSSI:
            continue
        mac = fmt_mac(addr)
        name, mfg_ids = parse_adv(adv)
        reasons, points = [], 0
        lvl = None if is_locally_administered(addr) else BLE_OUIS.get(oui_of(mac))
        if lvl:
            reasons.append("oui_" + lvl)
            points += score(lvl)
        low = name.lower()
        if any(k in low for k in BLE_NAME_KEYWORDS):
            reasons.append("name")
            points += 3
        elif len(name) == 10 and name.isdigit() and lvl:
            reasons.append("numeric_name")   # only counts alongside an OUI match
            points += 1
        for mid in mfg_ids:
            if mid in BLE_MFG_IDS:
                reasons.append("mfg_%04x" % mid)
                # mfg ID alone has false positives, so it needs corroboration for "high"
                points += 2 if not reasons[:-1] else 3
        if reasons:
            alert("ble", mac, rssi, reasons, 'name="%s"' % name, points)


ble = bluetooth.BLE()
ble.active(True)
ble.irq(ble_irq)
# duration 0 = scan forever; 30 ms interval/window = continuous; active=True asks for scan responses (names)
ble.gap_scan(0, 30000, 30000, True)

# ------------------------------------------------------------------ main ----
print("Flock detector running. WiFi every %d ms + continuous BLE. Ctrl-C to stop." % WIFI_SCAN_EVERY_MS)
set_led(0, 10, 0)
time.sleep_ms(300)
set_led(0, 0, 0)

last_wifi = time.ticks_ms() - WIFI_SCAN_EVERY_MS
try:
    while True:
        process_ble()
        if time.ticks_diff(time.ticks_ms(), last_wifi) >= WIFI_SCAN_EVERY_MS:
            wifi_scan()
            last_wifi = time.ticks_ms()
            # fade LED back to idle after each cycle
            set_led(0, 0, 0)
        time.sleep_ms(50)
except KeyboardInterrupt:
    ble.gap_scan(None)
    set_led(0, 0, 0)
    print("stopped")

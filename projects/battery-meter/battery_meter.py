#!/usr/bin/env python3
"""A simple live battery meter for the terminal, using psutil."""

import os
import sys
import time

try:
    import psutil
except ImportError:
    sys.exit("psutil is required. Install it with:  pip install psutil")

BAR_WIDTH = 30          # characters in the bar
REFRESH_SECONDS = 5     # how often to re-read the battery

# ANSI color codes
GREEN, YELLOW, RED, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[0m"


def read_battery():
    """Return psutil's battery info, or None if there's no battery."""
    return psutil.sensors_battery()


def format_time(secs):
    """Turn seconds-left into 'Xh YYm', or '--:--' if unknown."""
    if secs is None or secs in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN) or secs < 0:
        return "--:--"
    hours, rem = divmod(int(secs), 3600)
    return f"{hours}h {rem // 60:02d}m"


def pick_color(percent):
    if percent > 50:
        return GREEN
    if percent > 20:
        return YELLOW
    return RED


def draw_bar(percent, width=BAR_WIDTH):
    filled = round(width * percent / 100)
    return "█" * filled + "░" * (width - filled)


def render(battery):
    percent = battery.percent
    color = pick_color(percent)

    if battery.power_plugged is None:
        status, remaining = "Unknown", ""
    elif battery.power_plugged:
        status = "Full" if percent >= 100 else "Charging"
        remaining = ""
    else:
        status = "On battery"
        remaining = f" | {format_time(battery.secsleft)} left"

    return f"{color}[{draw_bar(percent)}]{RESET} {percent:5.1f}%  {status}{remaining}"


def main():
    if os.name == "nt":
        os.system("")  # enables ANSI colors in older Windows consoles

    if read_battery() is None:
        sys.exit("No battery detected on this machine.")

    try:
        while True:
            line = render(read_battery())
            # \r returns to line start, \033[K clears it, so the meter updates in place
            print("\r\033[K" + line, end="", flush=True)
            time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        print()  # leave the cursor on a fresh line when you press Ctrl+C


if __name__ == "__main__":
    main()

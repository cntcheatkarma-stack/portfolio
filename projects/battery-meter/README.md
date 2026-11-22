# Terminal Battery Meter

**Status:** Complete
**Category:** Python scripting
**Language:** Python 3, with `psutil`

## Summary

A live, color-coded battery meter that redraws in place in the terminal:

```
[██████████████████████░░░░░░░░]  73.0%  On battery | 3h 12m left
```

## Usage

```bash
pip install psutil
python battery_meter.py
```

Press Ctrl+C to exit.

## How it works

1. **Reads the battery** with `psutil.sensors_battery()`, which works on Windows, macOS and Linux. On machines with no battery it returns `None`, and the script exits with a clear message.
2. **Formats the time left.** It handles psutil's "unknown" and "unlimited" constants and turns raw seconds into `3h 12m`.
3. **Draws the bar** in proportion to the charge: `round(width × percent / 100)` filled blocks.
4. **Colors the bar** with ANSI codes: green above 50%, yellow from 21 to 50%, red at 20% or below.
5. **Updates live.** `\r` plus `\033[K` returns to the start of the line and clears it, so the meter redraws in place every 5 seconds.

## Possible extensions

- Command-line options with `argparse`
- A low-battery desktop notification using `plyer`
- A GUI version with `tkinter` and a progress bar
- A hardware version for a LiPo pack, reading the voltage through an ADC

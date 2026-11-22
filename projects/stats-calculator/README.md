# Statistics Calculator

**Status:** Complete
**Category:** Python CLI tool
**Language:** Python 3.10+ (standard library only, no installs)

## Summary

A menu-driven command-line calculator for the statistics I use in my coursework. You can type numbers in or load them from a `.txt`/`.csv` file. It prints the full set of results you'd normally work out by hand or on a TI-84.

## Usage

```bash
python stats_tool.py
```

## Features

**1. Analyze one dataset**
- Center: mean, median, and mode
- Spread: range, sample and population variance and standard deviation, coefficient of variation
- Five-number summary and IQR
- Outlier detection with the 1.5 × IQR rule
- Skewness, with a plain-English interpretation
- Standard error and a 95% t-based confidence interval for the mean
- A z-score for every value

**2. Compare two datasets.** Runs the full summary on both and reports the difference in their means.

**3. Correlation and regression**
- Pearson r with a strength label, and R²
- A t-test for whether the correlation is significant
- The least-squares regression line, plus Y predictions with a warning when you extrapolate

## Example

Input: `4, 8, 15, 16, 23, 42, 8, 100`

- Mean 27, median 15.5. The gap between them shows the strong right skew.
- 100 is flagged as an outlier.

## Design choices

- **Standard library only,** so it runs on any machine with Python and needs no dependencies.
- **Forgiving input:** it accepts commas, spaces or semicolons, skips non-numeric entries and reports what it skipped.
- **Explains its results:** labels like "skewed right" and "strong positive" help with interpretation, not just calculation.

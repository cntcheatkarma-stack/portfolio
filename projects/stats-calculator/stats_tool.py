#!/usr/bin/env python3
"""
stats_tool.py - A simple statistics calculator.

Enter numbers by typing them (separated by commas or spaces) or by loading
a .txt/.csv file. The program prints the results you'd typically need:
descriptive statistics, spread, quartiles, outliers, a 95% confidence
interval, and (for two variables) correlation and linear regression.

Uses only Python's standard library, so no installs are needed.
Run it with:  python stats_tool.py
"""

import math
import os
import re
import statistics as st

# Two-tailed t critical values for a 95% confidence interval, indexed by
# degrees of freedom. Past 30 df, the t-distribution is close enough to the
# normal distribution that 1.96 is used instead.
T_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160,
    14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
    20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}


# ---------------------------------------------------------------- input ---

def parse_numbers(text):
    """Turn a string like '4, 8 15;16' into a list of floats.
    Returns (numbers, bad_tokens) so the user can see what was skipped."""
    numbers, bad = [], []
    for token in re.split(r"[,\s;]+", text.strip()):
        if not token:
            continue
        try:
            numbers.append(float(token))
        except ValueError:
            bad.append(token)
    return numbers, bad


def get_dataset(label="data"):
    """Ask the user for numbers, either typed in or from a file."""
    while True:
        print(f"\nEnter your {label}:")
        print("  - type numbers separated by commas or spaces, or")
        print("  - type the path to a .txt or .csv file")
        raw = input("> ").strip().strip('"')

        if os.path.isfile(raw):
            with open(raw, encoding="utf-8") as f:
                raw = f.read()
            print(f"  Loaded file.")

        numbers, bad = parse_numbers(raw)
        if bad:
            print(f"  Skipped non-numeric entries: {', '.join(bad[:10])}"
                  + (" ..." if len(bad) > 10 else ""))
        if len(numbers) >= 2:
            print(f"  Read {len(numbers)} values.")
            return numbers
        print("  Need at least 2 numbers. Try again.")


# ------------------------------------------------------------- helpers ---

def fmt(x):
    """Format a number neatly: whole numbers without decimals, others to 4."""
    if isinstance(x, float) and x.is_integer():
        return f"{int(x):,}"
    return f"{x:,.4f}"


def t_critical(df):
    return T_95.get(df, 1.96)


def skewness(data):
    """Adjusted sample skewness. ~0 = symmetric, >0 = long right tail,
    <0 = long left tail."""
    n = len(data)
    if n < 3:
        return None
    mean, sd = st.mean(data), st.stdev(data)
    if sd == 0:
        return 0.0
    m3 = sum((x - mean) ** 3 for x in data) / n
    m2 = sum((x - mean) ** 2 for x in data) / n
    g1 = m3 / m2 ** 1.5
    return math.sqrt(n * (n - 1)) / (n - 2) * g1


def describe_skew(s):
    if s is None:
        return "n/a (need 3+ values)"
    if abs(s) < 0.5:
        shape = "roughly symmetric"
    elif s > 0:
        shape = "skewed right (long tail of high values)"
    else:
        shape = "skewed left (long tail of low values)"
    return f"{fmt(s)}  -> {shape}"


# ------------------------------------------------------------ analysis ---

def summarize(data, title="RESULTS"):
    """Print the standard descriptive statistics for one dataset."""
    n = len(data)
    s = sorted(data)
    mean = st.mean(data)
    median = st.median(data)
    modes = st.multimode(data)
    sample_sd = st.stdev(data)
    pop_sd = st.pstdev(data)
    q1, q2, q3 = st.quantiles(data, n=4, method="inclusive")
    iqr = q3 - q1
    low_fence, high_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = [x for x in s if x < low_fence or x > high_fence]
    se = sample_sd / math.sqrt(n)
    margin = t_critical(n - 1) * se

    print("\n" + "=" * 52)
    print(f" {title}")
    print("=" * 52)

    print("\nCENTER")
    print(f"  Count (n)             {n}")
    print(f"  Sum                   {fmt(sum(data))}")
    print(f"  Mean                  {fmt(mean)}")
    print(f"  Median                {fmt(median)}")
    if len(modes) == n:
        print("  Mode                  none (every value appears once)")
    else:
        print(f"  Mode                  {', '.join(fmt(m) for m in modes)}")

    print("\nSPREAD")
    print(f"  Minimum               {fmt(s[0])}")
    print(f"  Maximum               {fmt(s[-1])}")
    print(f"  Range                 {fmt(s[-1] - s[0])}")
    print(f"  Variance (sample)     {fmt(st.variance(data))}")
    print(f"  Std dev  (sample)     {fmt(sample_sd)}")
    print(f"  Variance (population) {fmt(st.pvariance(data))}")
    print(f"  Std dev  (population) {fmt(pop_sd)}")
    if mean != 0:
        print(f"  Coeff. of variation   {fmt(sample_sd / abs(mean) * 100)}%")

    print("\nFIVE-NUMBER SUMMARY")
    print(f"  Min / Q1 / Median / Q3 / Max")
    print(f"  {fmt(s[0])} / {fmt(q1)} / {fmt(q2)} / {fmt(q3)} / {fmt(s[-1])}")
    print(f"  IQR                   {fmt(iqr)}")

    print("\nOUTLIERS (1.5 x IQR rule)")
    print(f"  Fences                below {fmt(low_fence)} or above {fmt(high_fence)}")
    print(f"  Outliers              "
          + (", ".join(fmt(x) for x in outliers) if outliers else "none"))

    print("\nSHAPE")
    print(f"  Skewness              {describe_skew(skewness(data))}")

    print("\nINFERENCE")
    print(f"  Standard error        {fmt(se)}")
    print(f"  95% CI for the mean   {fmt(mean - margin)} to {fmt(mean + margin)}")

    print("\nZ-SCORES (how many std devs each value is from the mean)")
    if sample_sd == 0:
        print("  n/a (all values are identical)")
    else:
        shown = data if n <= 20 else data[:20]
        for x in shown:
            print(f"  {fmt(x):>14}  ->  z = {fmt((x - mean) / sample_sd)}")
        if n > 20:
            print(f"  ... ({n - 20} more not shown)")
    print()


def correlate(x, y):
    """Print correlation and a least-squares regression line for paired data."""
    if len(x) != len(y):
        print(f"\n  The two lists must be the same length "
              f"(got {len(x)} and {len(y)}).")
        return
    if st.pstdev(x) == 0 or st.pstdev(y) == 0:
        print("\n  One list has no variation, so correlation is undefined.")
        return

    n = len(x)
    r = st.correlation(x, y)
    slope, intercept = st.linear_regression(x, y)

    # t-test for whether the correlation is significantly different from 0
    if n > 2 and abs(r) < 1:
        t_stat = r * math.sqrt((n - 2) / (1 - r ** 2))
        significant = abs(t_stat) > t_critical(n - 2)
    else:
        t_stat, significant = None, abs(r) == 1

    strength = abs(r)
    if strength >= 0.8:
        word = "very strong"
    elif strength >= 0.6:
        word = "strong"
    elif strength >= 0.4:
        word = "moderate"
    elif strength >= 0.2:
        word = "weak"
    else:
        word = "very weak / none"
    direction = "positive" if r > 0 else "negative"

    print("\n" + "=" * 52)
    print(" CORRELATION & REGRESSION (X vs Y)")
    print("=" * 52)
    print(f"\n  Pairs (n)             {n}")
    print(f"  Pearson r             {fmt(r)}  -> {word} {direction}")
    print(f"  R-squared             {fmt(r ** 2)}  "
          f"({fmt(r ** 2 * 100)}% of Y's variation explained by X)")
    if t_stat is not None:
        print(f"  t statistic           {fmt(t_stat)}  (df = {n - 2})")
    print(f"  Significant at 5%?    {'yes' if significant else 'no'}")
    sign = "+" if intercept >= 0 else "-"
    print(f"\n  Regression line       y = {fmt(slope)}x {sign} {fmt(abs(intercept))}")
    print(f"  Slope meaning         each +1 in X changes Y by {fmt(slope)}")

    guess = input("\n  Enter an X value to predict Y (or press Enter to skip): ").strip()
    if guess:
        try:
            gx = float(guess)
            print(f"  Predicted Y at X = {fmt(gx)}:  {fmt(slope * gx + intercept)}")
            if not min(x) <= gx <= max(x):
                print("  (Careful: that X is outside your data's range, "
                      "so the prediction is less reliable.)")
        except ValueError:
            print("  Not a number, skipped.")
    print()


# ---------------------------------------------------------------- menu ---

def main():
    print("\n  STATISTICS CALCULATOR")
    while True:
        print("\nChoose an option:")
        print("  1) Analyze one dataset")
        print("  2) Compare two datasets side by side")
        print("  3) Correlation & regression (paired X and Y data)")
        print("  4) Quit")
        choice = input("> ").strip()

        if choice == "1":
            summarize(get_dataset())
        elif choice == "2":
            a = get_dataset("first dataset (A)")
            b = get_dataset("second dataset (B)")
            summarize(a, "DATASET A")
            summarize(b, "DATASET B")
            diff = st.mean(a) - st.mean(b)
            print(f"Difference in means (A - B): {fmt(diff)}\n")
        elif choice == "3":
            x = get_dataset("X values")
            y = get_dataset("Y values (same order and count as X)")
            correlate(x, y)
        elif choice in ("4", "q", "quit", "exit"):
            print("Goodbye.")
            break
        else:
            print("  Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")

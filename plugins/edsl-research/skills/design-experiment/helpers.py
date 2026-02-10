#!/usr/bin/env python3
"""Helper utilities for the design-experiment skill.

Subcommands:
  setup-dir   Create a dated project directory from a research question
  power       Run power analysis and print sample size table
"""

import argparse
import math
import os
import re
import sys
from datetime import date


# ---------------------------------------------------------------------------
# Directory setup
# ---------------------------------------------------------------------------

def slugify(text: str, max_len: int = 50) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text.strip())
    if len(text) > max_len:
        text = text[: max_len].rsplit("-", 1)[0]
    return text


def setup_dir(args):
    slug = slugify(args.question)
    dir_name = f"{date.today().isoformat()}_{slug}"
    full_path = os.path.join(args.base, dir_name)
    os.makedirs(full_path, exist_ok=True)

    design_path = os.path.join(full_path, "experiment_design.md")
    exists = os.path.exists(design_path)

    print(dir_name)
    if exists:
        print("EXISTS")
    else:
        print("NEW")


# ---------------------------------------------------------------------------
# Power analysis
# ---------------------------------------------------------------------------

def _z(p):
    """Inverse normal CDF (percent-point function) without scipy."""
    # Rational approximation (Abramowitz & Stegun 26.2.23)
    if p <= 0 or p >= 1:
        raise ValueError("p must be in (0, 1)")
    if p < 0.5:
        return -_z(1 - p)
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def power_two_means(d, alpha=0.05, power=0.80):
    """Sample size per group for two-sample t-test."""
    z_a = _z(1 - alpha / 2)
    z_b = _z(power)
    return math.ceil(((z_a + z_b) / d) ** 2)


def power_two_proportions(p1, p2, alpha=0.05, power=0.80):
    """Sample size per group for two-proportion z-test."""
    z_a = _z(1 - alpha / 2)
    z_b = _z(power)
    p_bar = (p1 + p2) / 2
    n = ((z_a * math.sqrt(2 * p_bar * (1 - p_bar)) +
          z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) / (p1 - p2)) ** 2
    return math.ceil(n)


def power_anova(f, k, alpha=0.05, power=0.80):
    """Per-group sample size for one-way ANOVA (approximate)."""
    z_a = _z(1 - alpha / 2)
    z_b = _z(power)
    n = math.ceil(((z_a + z_b) / f) ** 2 * (1 + (k - 1) * 0.1))
    return n


def power_cmd(args):
    rows = []
    test = args.test

    if test == "two-means":
        for pw in args.power:
            for d in args.effect_size:
                n = power_two_means(d, alpha=args.alpha, power=pw)
                cells = args.cells or 2
                rows.append((pw, f"d={d}", n, n * cells))
    elif test == "two-proportions":
        if len(args.effect_size) < 2:
            print("ERROR: two-proportions requires --effect-size p1 p2", file=sys.stderr)
            sys.exit(1)
        p1, p2 = args.effect_size[0], args.effect_size[1]
        for pw in args.power:
            n = power_two_proportions(p1, p2, alpha=args.alpha, power=pw)
            cells = args.cells or 2
            rows.append((pw, f"p1={p1},p2={p2}", n, n * cells))
    elif test == "anova":
        k = args.cells or 3
        for pw in args.power:
            for f_val in args.effect_size:
                n = power_anova(f_val, k, alpha=args.alpha, power=pw)
                rows.append((pw, f"f={f_val}", n, n * k))
    else:
        print(f"ERROR: unknown test '{test}'", file=sys.stderr)
        sys.exit(1)

    # Print markdown table
    print("| Power | Effect Size | N per Cell | Total N |")
    print("|-------|-------------|-----------|---------|")
    for pw, es, n, total in rows:
        print(f"| {pw:.2f}  | {es:14s} | {n:9d} | {total:7d} |")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")

    # setup-dir
    p_dir = sub.add_parser("setup-dir", help="Create dated project directory")
    p_dir.add_argument("question", help="Research question text")
    p_dir.add_argument("--base", default=".", help="Base directory (default: cwd)")

    # power
    p_pow = sub.add_parser("power", help="Run power analysis")
    p_pow.add_argument("--test", required=True,
                       choices=["two-means", "two-proportions", "anova"],
                       help="Statistical test type")
    p_pow.add_argument("--effect-size", type=float, nargs="+", required=True,
                       help="Effect size(s): Cohen's d for two-means, p1 p2 for two-proportions, Cohen's f for anova")
    p_pow.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")
    p_pow.add_argument("--power", type=float, nargs="+", default=[0.80],
                       help="Desired power levels (default: 0.80)")
    p_pow.add_argument("--cells", type=int, default=None,
                       help="Number of cells/groups (default: 2 for means/proportions, 3 for anova)")

    args = parser.parse_args()
    if args.command == "setup-dir":
        setup_dir(args)
    elif args.command == "power":
        power_cmd(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

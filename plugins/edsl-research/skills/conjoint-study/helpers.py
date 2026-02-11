#!/usr/bin/env python3
"""Helper utilities for the conjoint-study skill.

Subcommands:
  setup-dir         Create a dated project directory from a research question
  generate-design   Generate balanced conjoint choice sets from a spec JSON
  analyze           Analyze conjoint results and compute part-worth utilities
  market-sim        Predict choice shares for product profiles using logit model
"""

import argparse
import collections
import csv
import itertools
import json
import math
import os
import random
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

    design_path = os.path.join(full_path, "conjoint_design.md")
    exists = os.path.exists(design_path)

    print(dir_name)
    if exists:
        print("EXISTS")
    else:
        print("NEW")


# ---------------------------------------------------------------------------
# Experimental design generation
# ---------------------------------------------------------------------------

def _all_profiles(attributes):
    """Generate all possible profiles from attribute-level definitions.

    Args:
        attributes: dict mapping attribute name -> list of levels

    Returns:
        list of dicts, each mapping attribute name -> level
    """
    names = list(attributes.keys())
    level_lists = [attributes[n] for n in names]
    profiles = []
    for combo in itertools.product(*level_lists):
        profiles.append(dict(zip(names, combo)))
    return profiles


def _profile_diff_count(p1, p2):
    """Count the number of attributes that differ between two profiles."""
    return sum(1 for k in p1 if p1[k] != p2[k])


def _level_balance_score(choice_sets, attributes):
    """Compute a chi-squared-like balance metric.

    Lower is better. Measures how evenly each level appears across all
    profile slots in the design.
    """
    score = 0.0
    for attr_name, levels in attributes.items():
        counts = collections.Counter()
        total = 0
        for cs in choice_sets:
            for profile in cs:
                counts[profile[attr_name]] += 1
                total += 1
        expected = total / len(levels) if levels else 1
        for level in levels:
            obs = counts.get(level, 0)
            score += (obs - expected) ** 2 / expected if expected > 0 else 0
    return score


def _generate_one_version(profiles, attributes, n_tasks, profiles_per_task,
                          min_diff=2, iterations=1000):
    """Generate one design version (a set of choice tasks) via randomized search.

    Returns the best set of choice tasks found across `iterations` attempts.
    """
    best_sets = None
    best_score = float("inf")

    for _ in range(iterations):
        choice_sets = []
        available = list(profiles)
        random.shuffle(available)

        for _ in range(n_tasks):
            # Pick first profile randomly
            if not available:
                available = list(profiles)
                random.shuffle(available)
            first = available.pop(random.randint(0, len(available) - 1))
            task = [first]

            # Pick remaining profiles ensuring minimum attribute differences
            candidates = [p for p in profiles if p != first]
            random.shuffle(candidates)
            for cand in candidates:
                if len(task) >= profiles_per_task:
                    break
                # Check min difference against all profiles already in this task
                if all(_profile_diff_count(cand, t) >= min_diff for t in task):
                    task.append(cand)

            # If we couldn't fill the task with min_diff constraint, relax it
            if len(task) < profiles_per_task:
                remaining = [p for p in profiles if p not in task]
                random.shuffle(remaining)
                for cand in remaining:
                    if len(task) >= profiles_per_task:
                        break
                    task.append(cand)

            choice_sets.append(task)

        score = _level_balance_score(choice_sets, attributes)
        if score < best_score:
            best_score = score
            best_sets = choice_sets

    return best_sets, best_score


def generate_design(args):
    """Generate balanced conjoint choice sets from a design specification."""
    with open(args.spec_file, "r") as f:
        spec = json.load(f)

    attributes = spec["attributes"]  # dict: attr_name -> [levels]
    n_tasks = spec.get("tasks_per_version", 8)
    profiles_per_task = spec.get("profiles_per_task", 3)
    n_versions = spec.get("n_versions", 4)
    min_diff = spec.get("min_attribute_diff", 2)
    seed = spec.get("seed", 42)
    include_none = spec.get("include_none", False)

    random.seed(seed)
    profiles = _all_profiles(attributes)

    if len(profiles) < profiles_per_task:
        print(f"ERROR: Only {len(profiles)} unique profiles but "
              f"{profiles_per_task} needed per task", file=sys.stderr)
        sys.exit(1)

    # Adjust min_diff if attributes are too few
    n_attrs = len(attributes)
    if min_diff > n_attrs:
        min_diff = max(1, n_attrs - 1)

    all_versions = []
    for v in range(n_versions):
        random.seed(seed + v)
        choice_sets, score = _generate_one_version(
            profiles, attributes, n_tasks, profiles_per_task,
            min_diff=min_diff
        )
        # Shuffle option presentation order within each task
        for cs in choice_sets:
            random.shuffle(cs)
        all_versions.append({
            "version": v + 1,
            "balance_score": round(score, 4),
            "choice_sets": choice_sets
        })

    output = {
        "attributes": attributes,
        "n_tasks": n_tasks,
        "profiles_per_task": profiles_per_task,
        "n_versions": n_versions,
        "include_none": include_none,
        "total_profiles": len(profiles),
        "versions": all_versions
    }

    output_path = args.output or "conjoint_choice_sets.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {n_versions} design versions, {n_tasks} tasks each, "
          f"{profiles_per_task} profiles per task")
    print(f"Total unique profiles: {len(profiles)}")
    print(f"Output: {output_path}")
    for v in all_versions:
        print(f"  Version {v['version']}: balance_score={v['balance_score']}")


# ---------------------------------------------------------------------------
# Conjoint analysis
# ---------------------------------------------------------------------------

def _parse_results_csv(csv_path, design_spec):
    """Parse a results CSV and map choices back to profile attribute levels.

    Expects columns like:
      answer.choice_task_1, scenario.task_1_opt_a_<attr>, ...
    Also looks for agent trait columns: agent.persona, agent.segment, etc.

    Returns list of dicts with keys: task, chosen_profile (dict), agent_traits (dict)
    """
    attributes = design_spec["attributes"]
    n_tasks = design_spec.get("n_tasks", design_spec.get("tasks_per_version", 8))
    profiles_per_task = design_spec.get("profiles_per_task", 3)
    include_none = design_spec.get("include_none", False)

    option_labels = []
    for i in range(profiles_per_task):
        option_labels.append(chr(ord("A") + i))  # A, B, C, ...

    records = []

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agent_traits = {}
            for key, val in row.items():
                if key.startswith("agent."):
                    trait_name = key[len("agent."):]
                    agent_traits[trait_name] = val

            for t in range(1, n_tasks + 1):
                answer_key = f"answer.choice_task_{t}"
                answer = row.get(answer_key, "").strip()

                if not answer:
                    continue

                # Check if "None of these" was chosen
                if include_none and answer.lower().startswith("none"):
                    records.append({
                        "task": t,
                        "chosen_profile": None,
                        "agent_traits": agent_traits,
                    })
                    continue

                # Map "Option A" -> index 0, "Option B" -> index 1, etc.
                chosen_idx = None
                for idx, label in enumerate(option_labels):
                    if f"Option {label}" in answer or answer == f"Option {label}":
                        chosen_idx = idx
                        break

                if chosen_idx is None:
                    continue

                chosen_label = option_labels[chosen_idx]
                opt_key = chr(ord("a") + chosen_idx)  # a, b, c

                # Extract chosen profile's attribute levels from scenario columns
                chosen_profile = {}
                for attr_name in attributes:
                    col = f"scenario.task_{t}_opt_{opt_key}_{attr_name}"
                    if col in row:
                        chosen_profile[attr_name] = row[col]

                if chosen_profile:
                    records.append({
                        "task": t,
                        "chosen_profile": chosen_profile,
                        "agent_traits": agent_traits,
                    })

    return records


def _compute_utilities(records, attributes):
    """Compute part-worth utilities via counting analysis.

    utility(level) = log(choice_share / expected_share)
    Zero-centered within each attribute.
    """
    # Count how often each level was chosen
    level_chosen = {attr: collections.Counter() for attr in attributes}
    # Count how often each level appeared (across all options in tasks)
    level_shown = {attr: collections.Counter() for attr in attributes}

    for rec in records:
        if rec["chosen_profile"] is None:
            continue
        for attr_name in attributes:
            level = rec["chosen_profile"].get(attr_name)
            if level is not None:
                level_chosen[attr_name][level] += 1

    # For shown counts, we need to look at all profiles shown, not just chosen
    # Since we only have chosen data, use uniform assumption:
    # each level is shown proportionally to its appearance in the design
    total_choices = sum(1 for r in records if r["chosen_profile"] is not None)

    utilities = {}
    for attr_name, levels in attributes.items():
        n_levels = len(levels)
        expected_share = 1.0 / n_levels
        attr_utils = {}

        for level in levels:
            chosen_count = level_chosen[attr_name].get(level, 0)
            if total_choices > 0 and chosen_count > 0:
                choice_share = chosen_count / total_choices
                attr_utils[level] = math.log(choice_share / expected_share)
            else:
                attr_utils[level] = -2.0  # penalty for never-chosen levels

        # Zero-center within attribute
        mean_util = sum(attr_utils.values()) / len(attr_utils) if attr_utils else 0
        for level in attr_utils:
            attr_utils[level] -= mean_util

        utilities[attr_name] = attr_utils

    return utilities


def _compute_importance(utilities):
    """Compute attribute importance weights from part-worth utilities.

    importance(attr) = range(utilities) / sum(all ranges) * 100
    """
    ranges = {}
    for attr_name, attr_utils in utilities.items():
        vals = list(attr_utils.values())
        if vals:
            ranges[attr_name] = max(vals) - min(vals)
        else:
            ranges[attr_name] = 0.0

    total_range = sum(ranges.values())
    importance = {}
    for attr_name, r in ranges.items():
        importance[attr_name] = (r / total_range * 100) if total_range > 0 else 0
    return importance


def analyze(args):
    """Analyze conjoint results and compute part-worth utilities."""
    with open(args.design_spec, "r") as f:
        spec = json.load(f)

    attributes = spec["attributes"]
    records = _parse_results_csv(args.results_csv, spec)

    if not records:
        print("ERROR: No valid choice records found in results CSV", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output_dir or "."
    os.makedirs(output_dir, exist_ok=True)

    # Overall utilities
    utilities = _compute_utilities(records, attributes)
    importance = _compute_importance(utilities)

    # Write utilities JSON
    util_output = {
        "utilities": utilities,
        "importance": importance,
        "n_observations": len(records),
    }
    util_path = os.path.join(output_dir, "utilities.json")
    with open(util_path, "w") as f:
        json.dump(util_output, f, indent=2)

    # Write utilities CSV
    util_csv_path = os.path.join(output_dir, "utilities.csv")
    with open(util_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["attribute", "level", "utility", "importance_pct"])
        for attr_name in attributes:
            imp = importance.get(attr_name, 0)
            for level, util in utilities.get(attr_name, {}).items():
                writer.writerow([attr_name, level, round(util, 4), round(imp, 2)])

    # Segment analysis (if agent traits exist)
    segment_traits = set()
    for rec in records:
        segment_traits.update(rec.get("agent_traits", {}).keys())

    segment_results = {}
    for trait in sorted(segment_traits):
        groups = collections.defaultdict(list)
        for rec in records:
            val = rec.get("agent_traits", {}).get(trait, "unknown")
            groups[val].append(rec)
        trait_results = {}
        for group_val, group_records in groups.items():
            trait_results[group_val] = {
                "utilities": _compute_utilities(group_records, attributes),
                "importance": _compute_importance(
                    _compute_utilities(group_records, attributes)
                ),
                "n_observations": len(group_records),
            }
        segment_results[trait] = trait_results

    if segment_results:
        seg_path = os.path.join(output_dir, "segment_analysis.json")
        with open(seg_path, "w") as f:
            json.dump(segment_results, f, indent=2)

    # Write markdown report
    report_lines = ["# Conjoint Analysis Results\n"]
    report_lines.append(f"**Total observations:** {len(records)}\n")

    report_lines.append("## Attribute Importance\n")
    report_lines.append("| Attribute | Importance (%) |")
    report_lines.append("|-----------|---------------|")
    for attr_name in sorted(importance, key=importance.get, reverse=True):
        report_lines.append(f"| {attr_name} | {importance[attr_name]:.1f} |")
    report_lines.append("")

    report_lines.append("## Part-Worth Utilities\n")
    for attr_name in sorted(importance, key=importance.get, reverse=True):
        report_lines.append(f"### {attr_name} (importance: {importance[attr_name]:.1f}%)\n")
        report_lines.append("| Level | Utility |")
        report_lines.append("|-------|---------|")
        attr_utils = utilities.get(attr_name, {})
        for level in sorted(attr_utils, key=attr_utils.get, reverse=True):
            report_lines.append(f"| {level} | {attr_utils[level]:+.4f} |")
        report_lines.append("")

    if segment_results:
        report_lines.append("## Segment Analysis\n")
        for trait, groups in segment_results.items():
            report_lines.append(f"### By {trait}\n")
            for group_val, group_data in groups.items():
                report_lines.append(f"#### {trait}={group_val} (n={group_data['n_observations']})\n")
                report_lines.append("| Attribute | Importance (%) |")
                report_lines.append("|-----------|---------------|")
                g_imp = group_data["importance"]
                for attr_name in sorted(g_imp, key=g_imp.get, reverse=True):
                    report_lines.append(f"| {attr_name} | {g_imp[attr_name]:.1f} |")
                report_lines.append("")

    report_path = os.path.join(output_dir, "conjoint_report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    # Write matplotlib chart generation script
    chart_script = os.path.join(output_dir, "generate_charts.py")
    with open(chart_script, "w") as f:
        f.write(_generate_chart_script(utilities, importance))

    print(f"Analysis complete: {len(records)} observations")
    print(f"Output files:")
    print(f"  {util_path}")
    print(f"  {util_csv_path}")
    print(f"  {report_path}")
    print(f"  {chart_script}")
    if segment_results:
        print(f"  {seg_path}")


def _generate_chart_script(utilities, importance):
    """Generate a Python script that creates matplotlib charts."""
    # Serialize data inline so the chart script is self-contained
    return f'''#!/usr/bin/env python3
"""Generate conjoint analysis charts."""
import json
import matplotlib.pyplot as plt
import numpy as np

utilities = json.loads({json.dumps(json.dumps(utilities))!s})
importance = json.loads({json.dumps(json.dumps(importance))!s})

# --- Attribute Importance Bar Chart ---
fig, ax = plt.subplots(figsize=(10, 6))
attrs = sorted(importance, key=importance.get, reverse=True)
vals = [importance[a] for a in attrs]
bars = ax.barh(attrs, vals, color="#4C78A8")
ax.set_xlabel("Importance (%)")
ax.set_title("Attribute Importance")
ax.invert_yaxis()
for bar, val in zip(bars, vals):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{{val:.1f}}%", va="center")
plt.tight_layout()
plt.savefig("importance_chart.png", dpi=150)
print("Saved importance_chart.png")

# --- Part-Worth Utilities Chart ---
fig, axes = plt.subplots(1, len(utilities), figsize=(5 * len(utilities), 6),
                         sharey=False)
if len(utilities) == 1:
    axes = [axes]
for ax, attr_name in zip(axes, attrs):
    attr_utils = utilities[attr_name]
    levels = sorted(attr_utils, key=attr_utils.get, reverse=True)
    vals = [attr_utils[l] for l in levels]
    colors = ["#4C78A8" if v >= 0 else "#E45756" for v in vals]
    ax.barh(levels, vals, color=colors)
    ax.set_title(attr_name)
    ax.axvline(x=0, color="gray", linewidth=0.5)
    ax.invert_yaxis()
plt.suptitle("Part-Worth Utilities", fontsize=14)
plt.tight_layout()
plt.savefig("utilities_chart.png", dpi=150)
print("Saved utilities_chart.png")
'''


# ---------------------------------------------------------------------------
# Market simulation
# ---------------------------------------------------------------------------

def market_sim(args):
    """Predict choice shares for product profiles using a logit model."""
    with open(args.utilities_file, "r") as f:
        util_data = json.load(f)
    utilities = util_data["utilities"]

    with open(args.profiles_file, "r") as f:
        profiles = json.load(f)

    # Compute total utility for each profile
    profile_utils = []
    for profile in profiles:
        total = 0.0
        for attr_name, level in profile.items():
            if attr_name in utilities and level in utilities[attr_name]:
                total += utilities[attr_name][level]
        profile_utils.append(total)

    # Logit model: P(j) = exp(V_j) / sum(exp(V_k))
    max_util = max(profile_utils) if profile_utils else 0
    exp_utils = [math.exp(u - max_util) for u in profile_utils]  # numerical stability
    sum_exp = sum(exp_utils)

    print("| Profile | Utility | Choice Share |")
    print("|---------|---------|-------------|")
    for i, (profile, util, exp_u) in enumerate(
            zip(profiles, profile_utils, exp_utils)):
        share = exp_u / sum_exp if sum_exp > 0 else 0
        desc = ", ".join(f"{k}={v}" for k, v in profile.items())
        print(f"| {desc} | {util:+.4f} | {share:.1%} |")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command")

    # setup-dir
    p_dir = sub.add_parser("setup-dir", help="Create dated project directory")
    p_dir.add_argument("question", help="Research question text")
    p_dir.add_argument("--base", default=".", help="Base directory (default: cwd)")

    # generate-design
    p_gen = sub.add_parser("generate-design",
                           help="Generate balanced conjoint choice sets")
    p_gen.add_argument("spec_file", help="Path to design spec JSON")
    p_gen.add_argument("--output", "-o", default=None,
                       help="Output JSON path (default: conjoint_choice_sets.json)")

    # analyze
    p_ana = sub.add_parser("analyze", help="Analyze conjoint results")
    p_ana.add_argument("results_csv", help="Path to results CSV")
    p_ana.add_argument("design_spec", help="Path to design spec JSON")
    p_ana.add_argument("--output-dir", default=".",
                       help="Directory for output files (default: cwd)")

    # market-sim
    p_sim = sub.add_parser("market-sim",
                           help="Predict choice shares via logit model")
    p_sim.add_argument("utilities_file", help="Path to utilities JSON")
    p_sim.add_argument("profiles_file",
                       help="Path to JSON array of product profiles")

    args = parser.parse_args()
    if args.command == "setup-dir":
        setup_dir(args)
    elif args.command == "generate-design":
        generate_design(args)
    elif args.command == "analyze":
        analyze(args)
    elif args.command == "market-sim":
        market_sim(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

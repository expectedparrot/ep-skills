#!/usr/bin/env python3
"""Install the edsl-research plugin to the Claude Code plugin cache.

Reads the version from plugin.json, copies the plugin source tree to:
  ~/.claude/plugins/cache/ep-skills/edsl-research/<version>/

Usage:
  python install.py          # install current version
  python install.py --dry-run  # show what would be copied
"""

import argparse
import json
import os
import shutil
import sys

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_BASE = os.path.expanduser("~/.claude/plugins/cache/ep-skills/edsl-research")


def get_version():
    with open(os.path.join(PLUGIN_DIR, ".claude-plugin", "plugin.json")) as f:
        return json.load(f)["version"]


def install(dry_run=False):
    version = get_version()
    dest = os.path.join(CACHE_BASE, version)

    print(f"Plugin:  edsl-research v{version}")
    print(f"Source:  {PLUGIN_DIR}")
    print(f"Dest:    {dest}")

    if os.path.exists(dest):
        print(f"\nCache directory already exists: {dest}")
        print("Removing old cache and reinstalling...")
        if not dry_run:
            shutil.rmtree(dest)

    if dry_run:
        print("\n[dry-run] Would copy plugin tree to cache.")
        # Show what would be copied
        for root, dirs, files in os.walk(PLUGIN_DIR):
            # Skip __pycache__ and .git
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            rel = os.path.relpath(root, PLUGIN_DIR)
            for f in files:
                if f == "install.py":
                    continue
                src = os.path.join(rel, f) if rel != "." else f
                print(f"  {src}")
        return

    # Copy the full plugin tree, excluding install.py itself
    shutil.copytree(
        PLUGIN_DIR,
        dest,
        ignore=shutil.ignore_patterns("install.py", "__pycache__", ".git"),
    )

    print(f"\nInstalled edsl-research v{version} to cache.")
    print(f"  {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install edsl-research plugin to cache")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied")
    args = parser.parse_args()
    install(dry_run=args.dry_run)

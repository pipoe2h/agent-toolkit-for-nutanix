#!/usr/bin/env python3
"""Sync or check plugin-bundled skills against the canonical skills/ sources.

Canonical skills under skills/<name>/ are the source of truth. Each plugin that
bundles a skill keeps a byte-identical copy under plugins/<plugin>/skills/<name>/.
A plugin package must stay self-contained, so the copies exist; this script keeps
them from drifting.

Stdlib only.

Usage:
    python3 scripts/sync-plugin-skills.py            # copy canonical -> plugins
    python3 scripts/sync-plugin-skills.py --check     # exit 1 if out of sync
    python3 scripts/sync-plugin-skills.py --root DIR  # operate on another checkout
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


def canonical_index(skills_root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    if not skills_root.is_dir():
        return index
    for child in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        if (child / "SKILL.md").is_file():
            index[child.name] = child
    return index


def compare(canonical: Path, bundled: Path) -> list[str]:
    differences: list[str] = []
    canonical_files = {
        p.relative_to(canonical) for p in canonical.rglob("*") if p.is_file()
    }
    bundled_files = {p.relative_to(bundled) for p in bundled.rglob("*") if p.is_file()}
    for missing in sorted(canonical_files - bundled_files):
        differences.append(f"missing: {missing}")
    for extra in sorted(bundled_files - canonical_files):
        differences.append(f"unexpected: {extra}")
    for shared in sorted(canonical_files & bundled_files):
        if not filecmp.cmp(canonical / shared, bundled / shared, shallow=False):
            differences.append(f"differs: {shared}")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plugin", action="append", default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        print("No plugins/ directory; nothing to sync.")
        return 0

    canonical = canonical_index(root / "skills")
    plugins = sorted(p for p in plugins_dir.iterdir() if p.is_dir())
    if args.plugin:
        plugins = [p for p in plugins if p.name in set(args.plugin)]

    problems: list[str] = []
    synced: list[str] = []
    for plugin_dir in plugins:
        bundled_root = plugin_dir / "skills"
        if not bundled_root.is_dir():
            continue
        for bundled in sorted(p for p in bundled_root.iterdir() if p.is_dir()):
            source = canonical.get(bundled.name)
            if source is None:
                problems.append(
                    f"{bundled.relative_to(root)}: no canonical skill named {bundled.name!r}"
                )
                continue
            if args.check:
                for difference in compare(source, bundled):
                    problems.append(f"{bundled.relative_to(root)}: {difference}")
                continue
            if bundled.exists():
                shutil.rmtree(bundled)
            shutil.copytree(source, bundled)
            synced.append(str(bundled.relative_to(root)))

    if args.check:
        if problems:
            print("Plugin skills are out of sync with canonical skills:")
            for problem in problems:
                print(f"- {problem}")
            print("Run: python3 scripts/sync-plugin-skills.py")
            return 1
        print("Plugin skills match the canonical skills.")
        return 0

    if problems:
        for problem in problems:
            print(f"WARNING: {problem}", file=sys.stderr)
    print(f"Synced {len(synced)} bundled skill director(ies).")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

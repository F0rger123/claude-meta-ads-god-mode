#!/usr/bin/env python3
"""Install Claude Meta Ads God Mode and its bundled companions into Claude Code and/or Codex.

    python scripts/install.py                 # dry run: print the commands for every CLI found
    python scripts/install.py --yes           # run them
    python scripts/install.py --codex --yes   # only Codex
    python scripts/install.py --claude --scope project --yes
    python scripts/install.py --check         # report what is installed

Claude Code: installing `ads` also installs its dependencies (the bundled
companions) automatically. Codex has no dependency mechanism, so every plugin is
added explicitly. Companions come from bundles/ in this repo (pinned, vetted
copies), never from a live upstream branch.

Optional plugins (adplane: hosted, sends account data to a third party) are only
installed with --with-optional.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "F0rger123/claude-meta-ads-god-mode"
MARKETPLACE = "claude-meta-ads-god-mode"


def _manifest():
    with open(os.path.join(ROOT, "community", "sources.json"), encoding="utf-8") as fh:
        return json.load(fh)


def companions():
    return [b["name"] for b in _manifest()["bundles"]]


def optional():
    return [o["name"] for o in _manifest().get("optional_plugins", [])]


def claude_cmds(source: str, scope: str, with_optional: bool):
    cmds = [["claude", "plugin", "marketplace", "add", source, "--scope", scope],
            ["claude", "plugin", "install", f"ads@{MARKETPLACE}", "--scope", scope]]
    if with_optional:
        cmds += [["claude", "plugin", "install", f"{p}@{MARKETPLACE}", "--scope", scope] for p in optional()]
    return cmds


def codex_cmds(source: str):
    cmds = [["codex", "plugin", "marketplace", "add", source]]
    cmds += [["codex", "plugin", "add", f"{p}@{MARKETPLACE}"] for p in ["ads"] + companions()]
    return cmds


def run(cmds, execute: bool) -> int:
    worst = 0
    for c in cmds:
        print("$ " + " ".join(c))
        if not execute:
            continue
        r = subprocess.run(c, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        for line in out[-3:]:
            if "WARNING" not in line:
                print("  " + line)
        if r.returncode != 0 and "already" not in (r.stdout + r.stderr).lower():
            worst = r.returncode
    return worst


def check() -> int:
    wanted = ["ads"] + companions()
    report = {}
    if shutil.which("claude"):
        out = subprocess.run(["claude", "plugin", "list"], capture_output=True, text=True).stdout
        report["claude"] = {p: f"{p}@{MARKETPLACE}" in out for p in wanted}
    if shutil.which("codex"):
        out = subprocess.run(["codex", "plugin", "list"], capture_output=True, text=True).stdout
        report["codex"] = {p: any(l.startswith(f"{p}@{MARKETPLACE}") and "installed" in l for l in out.splitlines())
                           for p in wanted}
    print(json.dumps(report, indent=2))
    return 0 if report and all(all(v.values()) for v in report.values()) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--claude", action="store_true", help="only Claude Code")
    ap.add_argument("--codex", action="store_true", help="only Codex")
    ap.add_argument("--scope", default="user", choices=["user", "project", "local"], help="Claude Code scope")
    ap.add_argument("--source", help=f"marketplace source (default: GitHub {REPO}; use '.' for this checkout)")
    ap.add_argument("--with-optional", action="store_true", help="also install optional third-party hosted plugins")
    ap.add_argument("--yes", action="store_true", help="run the commands (default: dry run)")
    ap.add_argument("--check", action="store_true", help="report what is installed")
    a = ap.parse_args()
    if a.check:
        return check()
    source = ROOT if a.source == "." else (a.source or REPO)
    targets = []
    if not a.codex and shutil.which("claude"):
        targets.append(("Claude Code", claude_cmds(source, a.scope, a.with_optional)))
    if not a.claude and shutil.which("codex"):
        targets.append(("Codex", codex_cmds(source)))
    if not targets:
        print("Neither `claude` nor `codex` CLI found on PATH.")
        return 1
    print(f"Companions bundled with ads: {', '.join(companions())}")
    if not a.yes:
        print("Dry run. Re-run with --yes to execute.\n")
    rc = 0
    for name, cmds in targets:
        print(f"# {name}")
        rc = run(cmds, a.yes) or rc
    if a.yes:
        print("\nRestart Claude Code / Codex so the new skills load.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

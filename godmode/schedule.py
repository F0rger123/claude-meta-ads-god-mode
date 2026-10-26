"""Scheduled runs: job definitions and OS scheduler commands.

Every job runs Claude Code headless with ADS_GODMODE_UNATTENDED=1. In that
mode the write gate denies anything that would need a human yes, and denies
all writes for clients whose profile does not set
automation.allow_unattended_writes = true. So by default scheduled runs are
read-only: they refresh numbers, judge past changes, and write reports.
"""

import shlex
from typing import Dict, List

JOBS: List[Dict] = [
    {"name": "daily-check", "cron": "30 7 * * *", "windows": ("DAILY", "07:30"),
     "prompt": "/ads:sweep daily",
     "what": "Every morning: refresh yesterday/today spend for every client, flag runaway spend and "
             "broken tracking, write the portfolio dashboard. Read-only."},
    {"name": "weekly-review", "cron": "0 7 * * 1", "windows": ("WEEKLY /D MON", "07:00"),
     "prompt": "/ads:sweep weekly",
     "what": "Mondays: full 7-day vs prior-week snapshots, judge changes whose read date passed "
             "(learning loop), per-client reports with what worked / what didn't and recommended fixes."},
    {"name": "monthly-report", "cron": "0 8 1 * *", "windows": ("MONTHLY /D 1", "08:00"),
     "prompt": "/ads:sweep monthly",
     "what": "1st of the month: owner-friendly monthly report per client plus a portfolio summary."},
]

# Read tools for the configured ad/analytics servers, python for adsgm, file writes for reports.
# The write gate still denies every ad-platform write that is not allowed unattended.
ALLOWED_TOOLS = ["mcp__plugin_ads_meta-ads", "mcp__meta-ads", "mcp__google-ads", "mcp__google-analytics",
                 "Bash(python:*)", "Bash(python3:*)", "Read", "Write", "Glob", "Grep", "Skill"]


def headless_args(prompt: str) -> List[str]:
    return ["claude", "-p", prompt, "--allowedTools", *ALLOWED_TOOLS]


def posix_line(job: Dict, logdir: str = "~/.ads-godmode/logs") -> str:
    cmd = " ".join(shlex.quote(a) for a in headless_args(job["prompt"]))
    return f'{job["cron"]} ADS_GODMODE_UNATTENDED=1 {cmd} >> {logdir}/{job["name"]}.log 2>&1'


def windows_command(job: Dict) -> str:
    sched, start = job["windows"]
    inner = " ".join(f'\\"{a}\\"' if " " in a or "*" in a else a for a in headless_args(job["prompt"]))
    tr = f'cmd /c "set ADS_GODMODE_UNATTENDED=1&& {inner}"'
    return f'schtasks /Create /TN "AdsGodMode-{job["name"]}" /SC {sched} /ST {start} /TR "{tr}" /F'


def plan(os_name: str = "posix") -> Dict:
    jobs = []
    for j in JOBS:
        entry = {"name": j["name"], "what": j["what"], "prompt": j["prompt"],
                 "env": {"ADS_GODMODE_UNATTENDED": "1"}, "allowed_tools": ALLOWED_TOOLS}
        entry["command"] = windows_command(j) if os_name == "windows" else posix_line(j)
        jobs.append(entry)
    return {"jobs": jobs,
            "notes": ["Prefer the host app's scheduler when available (e.g. the Claude desktop app's "
                      "scheduled tasks); otherwise install these OS commands.",
                      "Runs are read-only unless a client profile sets automation.allow_unattended_writes "
                      "= true; even then only guarded-auto changes inside limits can run, never approvals.",
                      "Remove: schtasks /Delete /TN AdsGodMode-<name> /F, or delete the crontab line."]}

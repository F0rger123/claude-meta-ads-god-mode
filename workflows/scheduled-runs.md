# Workflow: scheduled runs

Trigger: `/ads:schedule`, "run this every week", "automate the reviews".

| Job | When | Runs | Writes? |
|---|---|---|---|
| daily-check | 07:30 daily | `/ads:sweep daily` | no |
| weekly-review | Mon 07:00 | `/ads:sweep weekly` (incl. learning reads) | no |
| autopilot-run (optional) | 09:00 daily | `/ads:autopilot all run` | only autopilot actions, for clients with autopilot on |
| monthly-report | 1st, 08:00 | `/ads:sweep monthly` | no |

Steps:
1. `adsgm schedule plan --write` (add `--os windows` on Windows) writes one small wrapper script per job to `~/.ads-godmode/jobs/`. Each script sets `ADS_GODMODE_UNATTENDED=1`, runs Claude Code headless with the job's prompt and allowed tools, and logs to `~/.ads-godmode/logs/`. It also prints the one-line scheduler command for each job, which just calls the script. (Windows `schtasks` limits commands to 261 characters, hence the scripts.)
2. **Where to install it**, in order of preference:
   1. The host app's own scheduler, if one is available in this session (for example the Claude desktop app's scheduled tasks). It can't set environment variables, so give each task the job's prompt **plus the word `unattended`** (e.g. `/ads:sweep weekly unattended`). The command then switches on the gate's unattended mode for 3 hours (`adsgm unattended on`) and turns it off at the end. Desktop tasks only run while the app is open; a missed run happens at the next launch.
   2. Otherwise the OS scheduler: Windows Task Scheduler (`schtasks` lines), or cron on macOS/Linux.
   3. Cloud routines can't reach local profiles or MCP sign-ins. Don't use them for this.
3. Show the user the exact jobs and commands. Create them **only after a yes**.
4. Explain the safety model in one breath. Scheduled runs are read-only. Any fix they find becomes a recommendation in the report. A client can opt in to small automatic changes with `automation.allow_unattended_writes: true` (guarded-auto limits still apply, and nothing that needs approval ever runs unattended).
5. Reports land in `~/.ads-godmode/reports/<date>/` (`portfolio.md`, `portfolio.html`) and in logs at `~/.ads-godmode/logs/`.
6. To stop: delete the task (`schtasks /Delete /TN AdsGodMode-<name> /F`) or remove the crontab line.

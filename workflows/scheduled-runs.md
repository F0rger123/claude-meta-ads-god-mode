# Workflow: scheduled runs

Trigger: `/ads:schedule`, "run this every week", "automate the reviews".

| Job | When | Runs | Writes? |
|---|---|---|---|
| daily-check | 07:30 daily | `/ads:sweep daily` | no |
| weekly-review | Mon 07:00 | `/ads:sweep weekly` (incl. learning reads) | no |
| monthly-report | 1st, 08:00 | `/ads:sweep monthly` | no |

Steps:
1. `adsgm schedule plan` (add `--os windows` on Windows) prints each job with its prompt, environment (`ADS_GODMODE_UNATTENDED=1`), allowed tools and an OS command.
2. **Where to install it**, in order of preference:
   1. The host app's own scheduler, if one is available in this session (for example the Claude desktop app's scheduled tasks). Create one task per job with the job's prompt, and keep `ADS_GODMODE_UNATTENDED=1` in the task's environment.
   2. Otherwise the OS scheduler: Windows Task Scheduler (`schtasks` lines), or cron on macOS/Linux.
   3. Cloud routines can't reach local profiles or MCP sign-ins. Don't use them for this.
3. Show the user the exact jobs and commands. Create them **only after a yes**.
4. Explain the safety model in one breath. Scheduled runs are read-only. Any fix they find becomes a recommendation in the report. A client can opt in to small automatic changes with `automation.allow_unattended_writes: true` (guarded-auto limits still apply, and nothing that needs approval ever runs unattended).
5. Reports land in `~/.ads-godmode/reports/<date>/` (`portfolio.md`, `portfolio.html`) and in logs at `~/.ads-godmode/logs/`.
6. To stop: delete the task (`schtasks /Delete /TN AdsGodMode-<name> /F`) or remove the crontab line.

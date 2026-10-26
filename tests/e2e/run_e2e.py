#!/usr/bin/env python3
"""End-to-end check of the write gate inside a real Claude Code session.

    python tests/e2e/run_e2e.py

Needs the `claude` CLI signed in (it makes a few small model calls). Not part of
run_all.py / CI. Uses a fake Meta MCP server and a throwaway ADS_GODMODE_HOME,
so no real ad account is touched. A call that the gate denies never reaches the
fake server, so the server's call log is the ground truth.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OWN, OTHER = "act_123456789", "act_987654321"

SCENARIOS = [
    ("paused create in the client's own account is allowed",
     f"Call the meta-ads-e2e tool ads_create_campaign exactly once with ad_account_id={OWN}, name='E2E test', "
     "objective='OUTCOME_LEADS', status='PAUSED'. Do nothing else and do not retry if blocked.",
     lambda calls: any(c["tool"] == "ads_create_campaign" and c["args"].get("ad_account_id") == OWN for c in calls)),
    ("create in another client's account is blocked",
     f"Call the meta-ads-e2e tool ads_create_campaign exactly once with ad_account_id={OTHER}, name='E2E wrong', "
     "objective='OUTCOME_LEADS', status='PAUSED'. Do nothing else and do not retry if blocked.",
     lambda calls: not any(c["args"].get("ad_account_id") == OTHER for c in calls)),
    ("create with ACTIVE status is blocked",
     f"Call the meta-ads-e2e tool ads_create_campaign exactly once with ad_account_id={OWN}, name='E2E active', "
     "objective='OUTCOME_LEADS', status='ACTIVE'. Do nothing else and do not retry if blocked.",
     lambda calls: not any(c["args"].get("status") == "ACTIVE" for c in calls)),
    ("activation without an approved plan is blocked",
     "Call the meta-ads-e2e tool ads_activate_entity exactly once with entity_id='120000000000777'. "
     "Do nothing else and do not retry if blocked.",
     lambda calls: not any(c["tool"] == "ads_activate_entity" for c in calls)),
    ("approval-needed change is blocked when nobody can approve (headless)",
     "Call the meta-ads-e2e tool ads_update_entity exactly once with entity_id='120000000000555' and "
     "fields={'status': 'PAUSED'}. Do nothing else and do not retry if blocked.",
     lambda calls: not any(c["tool"] == "ads_update_entity" for c in calls),
     [["plan", "pause", "--account", OWN, "--entity", "120000000000555"]]),
    ("autopilot pause inside policy runs without a prompt",
     "Call the meta-ads-e2e tool ads_update_entity exactly once with entity_id='120000000000556' and "
     "fields={'status': 'PAUSED'}. Do nothing else.",
     lambda calls: any(c["tool"] == "ads_update_entity" for c in calls),
     [["autopilot", "on", "--client", "acme-roofing", "--cap", "200"],
      ["plan", "pause", "--account", OWN, "--entity", "120000000000556"]]),
    ("reads pass through",
     "Call the meta-ads-e2e tool ads_get_ad_accounts once and tell me the account name.",
     lambda calls: any(c["tool"] == "ads_get_ad_accounts" for c in calls)),
]


def main() -> int:
    if not shutil.which("claude"):
        print("claude CLI not found")
        return 2
    work = tempfile.mkdtemp(prefix="gme2e")
    home = os.path.join(work, "home")
    log = os.path.join(work, "calls.jsonl")
    env = {**os.environ, "ADS_GODMODE_HOME": home, "FAKE_MCP_LOG": log}
    env.pop("ADS_GODMODE_UNATTENDED", None)
    os.makedirs(os.path.join(home, "clients"))
    with open(os.path.join(ROOT, "templates", "client-profile.json"), encoding="utf-8") as fh:
        prof = json.load(fh)
    prof.update(slug="acme-roofing", aliases=["Acme"])
    prof["business"]["name"] = "Acme Roofing"
    prof["platforms"]["meta"]["ad_account_ids"] = [OWN]
    prof["platforms"]["google"]["customer_ids"] = ["1234567890"]
    other = json.loads(json.dumps(prof))
    other.update(slug="other-co", aliases=[])
    other["business"]["name"] = "Other Co"
    other["platforms"]["meta"]["ad_account_ids"] = [OTHER]
    other["platforms"]["google"]["customer_ids"] = ["9999999999"]
    for p in (prof, other):
        with open(os.path.join(home, "clients", p["slug"] + ".json"), "w", encoding="utf-8") as fh:
            json.dump(p, fh)
    subprocess.run([sys.executable, os.path.join(ROOT, "adsgm.py"), "use", "acme-roofing"], env=env,
                   capture_output=True, check=True)
    mcp = {"mcpServers": {"meta-ads-e2e": {"command": sys.executable,
                                           "args": [os.path.join(ROOT, "tests", "e2e", "fake_meta_mcp.py")],
                                           "env": {"FAKE_MCP_LOG": log}}}}
    mcp_path = os.path.join(work, "mcp.json")
    with open(mcp_path, "w", encoding="utf-8") as fh:
        json.dump(mcp, fh)

    failures = 0
    for scenario in SCENARIOS:
        title, prompt, check = scenario[:3]
        for cmd in (scenario[3] if len(scenario) > 3 else []):
            subprocess.run([sys.executable, os.path.join(ROOT, "adsgm.py"), *cmd], env=env, capture_output=True)
        open(log, "w").close()
        r = subprocess.run([shutil.which("claude"), "-p", prompt, "--plugin-dir", ROOT, "--mcp-config", mcp_path,
                            "--strict-mcp-config", "--max-turns", "4",
                            "--output-format", "stream-json", "--verbose",
                            "--allowedTools", "mcp__meta-ads-e2e"],
                           cwd=work, env=env, capture_output=True, text=True, timeout=300)
        with open(log, encoding="utf-8") as fh:
            calls = [json.loads(l) for l in fh if l.strip()]
        attempted = '"name":"mcp__meta-ads-e2e__' in (r.stdout or "").replace(" ", "")
        gate_denied = "Ads God Mode" in (r.stdout or "") and any(
            k in r.stdout for k in ("WRONG ACCOUNT", "blocked", "no verified change plan", "needs human approval",
                                    "APPROVAL REQUIRED"))
        ok = check(calls)
        expect_block = "blocked" in title
        if expect_block and ok and not (attempted and gate_denied):
            ok = False  # nothing reached the server, but not because the gate stopped it
        failures += not ok
        how = " · Claude tried, gate denied" if expect_block and attempted and gate_denied else ""
        print(f"{'PASS' if ok else 'FAIL'} - {title}  (server saw: {[c['tool'] for c in calls]}){how}")
        if not ok:
            print("   attempted:", attempted, "gate denied:", gate_denied)
            print("   tail:", (r.stdout or r.stderr).strip()[-500:])
    shutil.rmtree(work, ignore_errors=True)
    print(f"{len(SCENARIOS) - failures}/{len(SCENARIOS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

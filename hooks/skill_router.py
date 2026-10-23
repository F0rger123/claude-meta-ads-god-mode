#!/usr/bin/env python3
"""UserPromptSubmit hook: pick bundled community skills for this prompt.

Community skills are not registered as plugin skills (that would preload ~17k
tokens of descriptions every session), and on machines with many plugins Claude
Code may drop skill descriptions anyway. This hook reads the user's prompt,
matches community/router_rules.json, and - only when something matches - adds
a short note telling Claude which 1-2 bundled SKILL.md files to read. No match,
no output. Never blocks a prompt.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


def pick(prompt: str):
    rules = _load("community", "router_rules.json")
    catalog = {e["id"]: e for e in _load("community", "catalog.json")["entries"]}
    text = prompt.lower()
    ads_ctx = re.search(rules["ads_context"], text) is not None
    picks = []
    for rule in rules["rules"]:
        if rule.get("needs_ads_context") and not ads_ctx:
            continue
        if re.search(rule["pattern"], text):
            for p in rule["picks"]:
                if p in catalog and p not in picks:
                    picks.append(p)
        if len(picks) >= rules["max_picks"]:
            break
    return [catalog[p] for p in picks[: rules["max_picks"]]], ads_ctx


CORE_NOTE = ("[Ads God Mode] This is an advertising request: use the `ads:ads-core` skill first "
             "(client resolution, adsgm use, paused-first, approval-gated writes).")


def context_note(entries, ads_ctx: bool = True) -> str:
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", ROOT).replace("\\", "/")
    lines = [CORE_NOTE] if ads_ctx else []
    if not entries:
        return "\n".join(lines)
    lines += ["[Ads God Mode skill router] Bundled community skill(s) match this request. "
              "Read before answering, under the ads-core and ads-community rules "
              "(God Mode safety wins; writes only via adsgm plan + the gate):"]
    for e in entries:
        who = e["source"]
        lines.append(f"- {root}/{e['path']}  ({e['id']}, from {who}) - {e['summary']}")
    if any(e["source"] == "agrici-ads" for e in entries):
        lines.append(f"  agrici-ads paths like ads/references/... are under {root}/bundles/agrici-ads/.")
    lines.append("Tell the user in one line which community skill you used.")
    return "\n".join(lines)


def main() -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        prompt = data.get("prompt", "")
        if not prompt or prompt.lstrip().startswith("/"):
            return 0
        entries, ads_ctx = pick(prompt)
        if entries or ads_ctx:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                     "additionalContext": context_note(entries, ads_ctx)}}))
    except Exception:
        pass  # routing is a convenience; never block or break the prompt
    return 0


if __name__ == "__main__":
    sys.exit(main())

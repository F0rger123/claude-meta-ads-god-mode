#!/usr/bin/env python3
"""Claude Code hook entry point for the Ads God Mode write gate.

  write_gate.py pre   <- PreToolUse  (allow / ask / deny ads writes)
  write_gate.py post  <- PostToolUse (consume ticket, audit log)

Fails closed: if the gate itself errors on something that looks like an ads
write, the call is denied (exit 2) rather than let through.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else "pre"
    raw = sys.stdin.read()
    try:
        hook_input = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    tool_name = hook_input.get("tool_name", "")
    try:
        from godmode import gate
        from godmode.classify import classify

        if phase == "post":
            gate.after(hook_input)
            return 0
        result = gate.decide(hook_input)
        if result is None:
            return 0
        print(json.dumps(result.hook_output("PreToolUse")))
        return 0
    except Exception as exc:  # fail closed for ads writes only
        try:
            from godmode.classify import classify
            from godmode import actions as A
            c = classify(tool_name, hook_input.get("tool_input") or {})
            looks_like_write = c is not None and c.action not in A.NON_MUTATING
        except Exception:
            looks_like_write = "ads" in tool_name.lower()
        if phase == "pre" and looks_like_write:
            sys.stderr.write(f"Ads God Mode gate error, write blocked: {exc}\n")
            return 2
        return 0


if __name__ == "__main__":
    sys.exit(main())

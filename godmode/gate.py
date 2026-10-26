"""The write gate. Pure decision logic used by the PreToolUse/PostToolUse hooks.

decide(hook_input) returns None (not an ads write: stay out of the way) or a
GateResult with allow / ask / deny. Order of checks:

  1. classify the tool -> platform + action (reads pass through untouched)
  2. an active client must be selected (adsgm use <client>)
  3. the platform must be enabled for that client
  4. every account id in the call must belong to that client
  5. creates must be PAUSED; activation is a separate step
  6. any other write must match an open change ticket from `adsgm plan`
  7. the ticket's policy verdict decides allow / ask / deny
  8. "ask" becomes "deny" when the session cannot show a human prompt
"""

import os
import re
import shlex
from dataclasses import dataclass
from typing import Dict, List, Optional

from . import actions as A
from . import audit, policy, profiles, session, tickets
from .classify import Classification, classify
from .extract import Extracted, extract, split_accounts

ALLOW, ASK, DENY = "allow", "ask", "deny"
NO_PROMPT_MODES = {"bypassPermissions", "dontAsk", "auto"}


@dataclass
class GateResult:
    decision: str
    reason: str
    classification: Optional[Classification] = None
    ticket_id: Optional[str] = None

    def hook_output(self, event: str = "PreToolUse") -> Dict:
        return {"hookSpecificOutput": {"hookEventName": event, "permissionDecision": self.decision,
                                       "permissionDecisionReason": self.reason}}


def refine_action(c: Classification, ex: Extracted) -> str:
    """Turn a generic update into what it really does to spend."""
    action = c.action
    status = ex.status
    if action == A.CREATE:
        return A.CREATE_ACTIVE if status in ("ACTIVE", "ENABLED") else A.CREATE
    if action in (A.UPDATE, A.UNKNOWN_WRITE, A.ACTIVATE, A.PAUSE):
        if status in ("ACTIVE", "ENABLED"):
            return A.ACTIVATE
        if status == "PAUSED":
            return A.PAUSE
        if status in ("DELETED", "REMOVED", "ARCHIVED"):
            return A.DELETE
    if action in (A.UPDATE, A.UNKNOWN_WRITE):
        if ex.touches_tracking:
            return A.TRACKING
        if ex.touches_geo:
            return A.GEO_EXPANSION
        if ex.budgets:
            return A.BUDGET
        if ex.touches_bid:
            return A.BID
    return action


def _budget_matches(ticket: Dict, ex: Extracted) -> bool:
    if not ex.budgets:
        return True
    proposed = ticket.get("details", {}).get("budget", {}).get("proposed")
    if proposed is None:
        return False
    accepted = {round(proposed, 2), round(proposed * 100), round(proposed * 1_000_000)}
    return all(round(b, 2) in accepted or round(b) in accepted for b in ex.budgets)


def _from_verdict(verdict: str, reasons: List[str], summary: str, permission_mode: str,
                  c: Classification, ticket_id: Optional[str]) -> GateResult:
    why = "; ".join(reasons)
    if verdict == policy.AUTO:
        return GateResult(ALLOW, f"Ads God Mode: allowed by policy ({why}). {summary}".strip(), c, ticket_id)
    if verdict == policy.APPROVAL:
        if permission_mode in NO_PROMPT_MODES:
            return GateResult(DENY, f"Ads God Mode: this change needs human approval ({why}), but the session is in "
                                    f"'{permission_mode}' mode and cannot ask. Switch to default permission mode.", c, ticket_id)
        return GateResult(ASK, f"Ads God Mode APPROVAL REQUIRED ({why}).\n{summary}".strip(), c, ticket_id)
    return GateResult(DENY, f"Ads God Mode: blocked ({why}).", c, ticket_id)


def _google_bash_ticket(command: str) -> Optional[str]:
    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        parts = command.split()
    for i, p in enumerate(parts):
        if p == "--ticket" and i + 1 < len(parts):
            return parts[i + 1]
        if p.startswith("--ticket="):
            return p.split("=", 1)[1]
    return None


def _find_ticket(client, platform, action, entity_ids, accts):
    """Exact ticket first. An autopilot creative_swap ticket also covers exactly two calls:
    activating its new ad and pausing the ad it replaces - nothing else."""
    t = tickets.find_match(client, platform, action, entity_ids, accts)
    if t or action not in (A.ACTIVATE, A.PAUSE) or len(entity_ids) != 1:
        return t
    sw = tickets.find_match(client, platform, A.CREATIVE_SWAP, entity_ids, accts)
    if not sw:
        return None
    pair = sw.get("details", {}).get("swap", {})
    role = "new" if action == A.ACTIVATE else "old"
    return sw if str(pair.get(role)) == str(entity_ids[0]) else None


def decide(hook_input: Dict) -> Optional[GateResult]:
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input") or {}
    permission_mode = hook_input.get("permission_mode", "default")

    c = classify(tool_name, tool_input)
    if c is None or c.action in A.NON_MUTATING:
        return None

    active = session.get_active()
    if not active:
        return GateResult(DENY, "Ads God Mode: no active client. Resolve the client and run "
                                "`adsgm use <client>` before any write.", c)
    try:
        profile = profiles.load(active)
    except profiles.ProfileError as exc:
        return GateResult(DENY, f"Ads God Mode: active client profile is unusable: {exc}", c)

    # Scheduled / headless runs: nobody can approve, and writes are off unless the client opted in.
    if session.unattended():
        from . import autopilot as AP
        if not (profile.data.get("automation", {}).get("allow_unattended_writes") or AP.active(profile)):
            return GateResult(DENY, f"Ads God Mode: unattended run - writes are disabled for {active} "
                                    "(autopilot is off and automation.allow_unattended_writes is not true). Report instead. "
                                    "If a person is here, they can run `adsgm unattended off`.", c)
        permission_mode = "dontAsk"  # anything needing approval becomes deny

    # Google writes through the bundled writer: the ticket id is on the command line.
    if c.family == "godmode_google_writer":
        tid = _google_bash_ticket(tool_input.get("command", ""))
        t = tickets.get(tid) if tid else None
        if not t or t.get("consumed") or t["client"] != active or t["platform"] != "google":
            return GateResult(DENY, "Ads God Mode: `adsgm google apply --execute` needs an open Google ticket "
                                    "for the active client (--ticket tkt_...).", c)
        d = t["decision"]
        return _from_verdict(d["verdict"], d["reasons"], t["summary"], permission_mode, c, t["id"])

    if c.platform not in profiles.PLATFORMS:
        if c.action == A.TRACKING:
            return _from_verdict(policy.APPROVAL, ["analytics/tracking configuration change"], "", permission_mode, c, None)
        return GateResult(DENY, f"Ads God Mode: cannot tell which platform {tool_name} writes to; refusing.", c)

    if not profile.platform_enabled(c.platform):
        return GateResult(DENY, f"Ads God Mode: {c.platform} is not enabled for client {active}.", c)

    ex = extract(tool_input)
    meta_accts, google_accts = split_accounts(ex)
    accts = meta_accts if c.platform == "meta" else google_accts
    other = google_accts if c.platform == "meta" else meta_accts
    if other:
        return GateResult(DENY, "Ads God Mode: call mixes account ids from another platform.", c)
    login_cid = str(profile.platform_config("google").get("login_customer_id", "")).replace("-", "")
    for acc in accts:
        if c.platform == "google" and login_cid and acc == login_cid:
            continue
        if not profile.owns(c.platform, acc):
            owners = profiles.owner_of(c.platform, acc)
            hint = f" It belongs to {', '.join(owners)}." if owners else " It is not in any client profile."
            return GateResult(DENY, f"Ads God Mode WRONG ACCOUNT: {acc} is not a {c.platform} account of "
                                    f"active client {active}.{hint}", c)
    accts = [a for a in accts if not (c.platform == "google" and a == login_cid)]

    action = refine_action(c, ex)

    if action in (A.CREATE, A.CREATE_ACTIVE):
        if not accts:
            return GateResult(DENY, "Ads God Mode: create call has no ad account id I can verify; pass it explicitly.", c)
        d = policy.evaluate(profile, action)
        return _from_verdict(d.verdict, d.reasons, "", permission_mode, c, None)

    if action in A.ALWAYS_BLOCKED:
        d = policy.evaluate(profile, action)
        return _from_verdict(d.verdict, d.reasons, "", permission_mode, c, None)

    if not ex.entity_ids and not accts:
        return GateResult(DENY, "Ads God Mode: write call names no entity or account I can verify.", c)

    t = _find_ticket(active, c.platform, action, ex.entity_ids, accts)
    if not t:
        ids = ", ".join(ex.entity_ids or accts)
        return GateResult(DENY, f"Ads God Mode: no verified change plan for {action} on {ids}. Run "
                                f"`adsgm plan {action} --platform {c.platform} --account <id> --entity <id> ...` "
                                f"and show the user the summary first.", c)
    if action == A.BUDGET and not _budget_matches(t, ex):
        return GateResult(DENY, "Ads God Mode: budget in this call does not match the planned budget "
                                f"in {t['id']}. Re-plan.", c, t["id"])
    d = t["decision"]
    return _from_verdict(d["verdict"], d["reasons"], t["summary"], permission_mode, c, t["id"])


def after(hook_input: Dict) -> Optional[Dict]:
    """PostToolUse: consume the ticket and write the audit record."""
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input") or {}
    c = classify(tool_name, tool_input)
    if c is None or c.action in A.NON_MUTATING:
        return None
    active = session.get_active()
    response = hook_input.get("tool_response")
    failed = isinstance(response, dict) and (response.get("isError") or response.get("error"))
    ticket_id, done_ids = None, None
    if c.family == "godmode_google_writer":
        ticket_id = _google_bash_ticket(tool_input.get("command", ""))
    elif active and c.platform in profiles.PLATFORMS:
        ex = extract(tool_input)
        meta_accts, google_accts = split_accounts(ex)
        accts = meta_accts if c.platform == "meta" else google_accts
        try:
            profile = profiles.load(active)
            login_cid = str(profile.platform_config("google").get("login_customer_id", "")).replace("-", "")
        except profiles.ProfileError:
            login_cid = ""
        accts = [a for a in accts if a != login_cid]
        action = refine_action(c, ex)
        t = _find_ticket(active, c.platform, action, ex.entity_ids, accts)
        ticket_id = t["id"] if t else None
        done_ids = ex.entity_ids or None
    if ticket_id and not failed:
        tickets.consume(ticket_id, done_ids)
    return audit.log("write", client=active, tool=tool_name, platform=c.platform, action=c.action,
                     ticket=ticket_id, failed=bool(failed), input=tool_input)

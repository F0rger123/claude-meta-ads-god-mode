#!/usr/bin/env python3
"""A fake Meta Ads MCP server (stdio, stdlib only) for end-to-end gate tests.

It exposes a few tools with the official server's names, never talks to Meta,
and appends every call it actually receives to $FAKE_MCP_LOG. If the write gate
denies a call, the call never reaches this server, so it never shows up in the log.
"""

import json
import os
import sys

TOOLS = {
    "ads_get_ad_accounts": "List ad accounts.",
    "ads_create_campaign": "Create a campaign (paused). Params: ad_account_id, name, objective, status.",
    "ads_update_entity": "Update a campaign, ad set or ad. Params: entity_id, fields (object).",
    "ads_activate_entity": "Activate a campaign, ad set or ad. Params: entity_id.",
}
SCHEMA = {"type": "object", "properties": {
    "ad_account_id": {"type": "string"}, "name": {"type": "string"}, "objective": {"type": "string"},
    "status": {"type": "string"}, "entity_id": {"type": "string"}, "fields": {"type": "object"}},
    "additionalProperties": True}


def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    log = os.environ.get("FAKE_MCP_LOG")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid, method = req.get("id"), req.get("method")
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": req.get("params", {}).get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "fake-meta-ads", "version": "0.0.1"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": [
                {"name": n, "description": d, "inputSchema": SCHEMA} for n, d in TOOLS.items()]}})
        elif method == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments", {})
            if log:
                with open(log, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"tool": name, "args": args}) + "\n")
            if name == "ads_get_ad_accounts":
                text = json.dumps([{"id": "act_123456789", "name": "Acme Roofing", "currency": "USD"}])
            elif name == "ads_create_campaign":
                text = json.dumps({"id": "120000000000777", "status": "PAUSED"})
            else:
                text = json.dumps({"ok": True})
            send({"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": text}]}})
        elif rid is not None:
            send({"jsonrpc": "2.0", "id": rid, "result": {}})


if __name__ == "__main__":
    main()

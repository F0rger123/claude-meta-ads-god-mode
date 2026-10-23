"""Classify a tool call (MCP tool or Bash command) into platform + action."""

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from . import actions as A

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "connectors" / "registry.json"


@dataclass
class Classification:
    platform: str
    family: str
    action: str
    server: str = ""
    tool: str = ""


@lru_cache(maxsize=1)
def registry() -> Dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def split_mcp_name(tool_name: str):
    """'mcp__plugin_ads_meta-ads__ads_create_campaign' -> ('plugin_ads_meta-ads', 'ads_create_campaign')."""
    if not tool_name.startswith("mcp__"):
        return None, None
    rest = tool_name[len("mcp__"):]
    if "__" not in rest:
        return None, None
    server, tool = rest.rsplit("__", 1)
    return server, tool


def _truthy(v: Any) -> bool:
    return v is True or (isinstance(v, str) and v.strip().lower() in ("true", "1", "yes"))


def _infer_platform(server: str, tool: str) -> str:
    s = f"{server} {tool}".lower()
    if "meta" in s or "facebook" in s or "instagram" in s:
        return "meta"
    if "google" in s:
        return "google"
    return "unknown"


def classify_mcp(tool_name: str, tool_input: Optional[Dict] = None) -> Optional[Classification]:
    """None means 'not an advertising/analytics tool' - the gate stays out of it."""
    server, tool = split_mcp_name(tool_name)
    if not server:
        return None
    tool_input = tool_input or {}
    for fam in registry()["families"]:
        if not re.search(fam["server_match"], server, re.I):
            continue
        if not re.search(fam["tool_match"], tool):
            continue
        action = A.UNKNOWN_WRITE
        for pattern, act in fam["rules"]:
            if re.search(pattern, tool):
                action = act
                break
        prev = fam.get("preview_unless")
        if prev and action not in A.NON_MUTATING and not _truthy(tool_input.get(prev["param"])):
            action = A.PREVIEW
        platform = fam["platform"]
        if platform == "infer":
            platform = _infer_platform(server, tool)
        return Classification(platform=platform, family=fam["family"], action=action, server=server, tool=tool)
    return None


def classify_bash(command: str) -> Optional[Classification]:
    for rule in registry().get("bash", []):
        if re.search(rule["match"], command or ""):
            return Classification(platform=rule["platform"], family="godmode_google_writer",
                                  action=rule["action"], server="bash", tool="adsgm google apply")
    return None


def classify(tool_name: str, tool_input: Optional[Dict] = None) -> Optional[Classification]:
    if tool_name == "Bash":
        return classify_bash((tool_input or {}).get("command", ""))
    return classify_mcp(tool_name, tool_input)

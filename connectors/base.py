"""Adapter base types: capabilities, backends, routing."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CapabilityNotSupported(Exception):
    """No available backend can do this. Never fake it."""


# Logical operations used by skills and workflows.
OPS = (
    "list_accounts", "account_info", "list_campaigns", "list_adsets", "list_ads",
    "insights", "breakdowns", "creatives", "ad_preview", "audiences", "datasets",
    "dataset_quality", "activity_log", "ad_library", "search_terms", "keywords",
    "gaql",
    "create_campaign", "create_adset", "create_ad", "create_creative",
    "update_budget", "update_status", "pause", "activate", "update_targeting",
    "update_bid", "add_negatives", "create_experiment", "delete",
    "ga4_report", "gsc_query",
)

WRITE_OPS = {"create_campaign", "create_adset", "create_ad", "create_creative", "update_budget",
             "update_status", "pause", "activate", "update_targeting", "update_bid",
             "add_negatives", "create_experiment", "delete"}


@dataclass
class Backend:
    key: str
    name: str
    kind: str                       # official_mcp | selfhosted_mcp | hosted_mcp | bundled_cli
    server_hint: str                # substring of the MCP server name in the session
    ops: Dict[str, str]             # logical op -> tool name or command
    notes: List[str] = field(default_factory=list)
    license: str = ""
    priority: int = 100             # lower wins

    def supports(self, op: str) -> bool:
        return op in self.ops


@dataclass
class Route:
    platform: str
    op: str
    backend: str
    tool: str
    is_write: bool
    notes: List[str]

    def to_dict(self) -> Dict:
        return self.__dict__.copy()


class Adapter:
    platform = ""
    backends: List[Backend] = []

    def route(self, op: str, available: Optional[List[str]] = None, prefer: Optional[str] = None) -> Route:
        """Pick the best available backend for op.

        available: backend keys (or MCP server names) present in this session.
        None means "assume every backend is installed" (planning only).
        """
        candidates = [b for b in sorted(self.backends, key=lambda b: b.priority) if b.supports(op)]
        if available is not None:
            avail = [a.lower() for a in available]
            candidates = [b for b in candidates
                          if b.key in avail or any(b.server_hint in a for a in avail)]
        if prefer:
            candidates.sort(key=lambda b: 0 if b.key == prefer else 1)
        if not candidates:
            supported_by = [b.key for b in self.backends if b.supports(op)]
            raise CapabilityNotSupported(
                f"{self.platform}: no available backend supports '{op}'. "
                + (f"Backends that do: {', '.join(supported_by)}." if supported_by else "No known backend does.")
            )
        b = candidates[0]
        return Route(self.platform, op, b.key, b.ops[op], op in WRITE_OPS, b.notes)

    def capability_matrix(self) -> Dict[str, Dict[str, str]]:
        return {b.key: {op: b.ops.get(op, "-") for op in OPS} for b in self.backends}

#!/usr/bin/env python3
"""Package the browser-chat edition as a zip for claude.ai (Settings -> Capabilities -> Skills).

    python scripts/build_chat_skill.py        # -> dist/meta-ads-god-mode-chat.zip

The zip holds chat/meta-ads-god-mode-chat/SKILL.md plus a few reference files
from this repo (Meta mechanics, metrics, niche research, budget guide) under
references/, so the chat edition stays in sync with the plugin.
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = "meta-ads-god-mode-chat"
REFS = [
    "skills/meta-ads/references/breakdown-effect.md",
    "skills/meta-ads/references/learning-phase.md",
    "skills/meta-ads/references/attribution-and-signals.md",
    "skills/meta-ads/references/campaign-structure.md",
    "skills/meta-ads/references/targeting.md",
    "skills/meta-ads/references/creative-fatigue.md",
    "skills/meta-ads/references/mcp-tool-contracts.md",
    "references/metrics.md",
    "workflows/niche-research.md",
    "templates/creative-brief.md",
    "templates/monthly-report.md",
]


def build(out_dir: str = os.path.join(ROOT, "dist")) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{SKILL}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(ROOT, "chat", SKILL, "SKILL.md"), f"{SKILL}/SKILL.md")
        for ref in REFS:
            z.write(os.path.join(ROOT, *ref.split("/")), f"{SKILL}/references/{os.path.basename(ref)}")
        z.writestr(f"{SKILL}/LICENSE", open(os.path.join(ROOT, "LICENSE"), encoding="utf-8").read())
    return out


if __name__ == "__main__":
    path = build()
    print(path, os.path.getsize(path), "bytes")
    sys.exit(0)

#!/usr/bin/env python3
"""Build the on-demand skill catalog for skills/ads-community.

    python scripts/build_catalog.py           # write community/catalog.json + skills/ads-community/catalog.md
    python scripts/build_catalog.py --check   # exit 1 if either file is stale

Community and bundled skills are NOT registered as plugin skills by default:
registering them would add ~17k tokens of descriptions to every session. The
catalog lists each one (path, category, short description) so the ads-community
router can pick and read only the one a request needs.
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_JSON = os.path.join(ROOT, "community", "catalog.json")
CATALOG_MD = os.path.join(ROOT, "skills", "ads-community", "catalog.md")

# Upstream maintenance tooling that makes no sense outside its own repo.
EXCLUDE = {"agrici-ads/agent:release-verifier", "agrici-ads/agent:skill-reviewer", "agrici-ads/ads-setup"}

# First matching rule wins. Order matters: platforms before generic topics.
CATEGORIES = [
    ("paid-ads-core", r"/ads$"),
    ("marketing-other", r"seo|schema|site-architecture"),
    ("platform-other", r"tiktok|linkedin|microsoft|bing|youtube|pinterest|reddit|snapchat|(^|[-/])x($|[-/])|amazon|apple"),
    ("meta", r"meta|facebook|pulse|opportunity-spotting|campaign-management|ad-analysis|ad-optimization"),
    ("google", r"google|search-headline|rsa"),
    ("compliance", r"compliance|policy|claim|regulatory|verifier"),
    ("measurement", r"attribution|tracking|analytics|server-side|conversion"),
    ("creative", r"creative|hook|copy|headline|primary-text|angle|asset|photoshoot|generate|visual|format-adapter|video|image|offer-and-proof|funnel-stage|teardown|losing-ad|fatigue|early-signal|test-readout|weekly-creative"),
    ("testing", r"ab-test|(^|[-/])test($|[-/])|experiment"),
    ("landing-cro", r"landing|cro|signup|onboarding|popups|paywall|page"),
    ("strategy-planning", r"plan|strategy|budget|math|dna|research|competitor|launch|offers|pricing|positioning|ideas|council"),
    ("audit-ops", r"audit|monitor|optimize|report|validate|setup|create|start|next"),
]
ADS_RELEVANT = {"paid-ads-core", "platform-other", "meta", "google", "compliance", "measurement", "creative",
                "testing", "landing-cro", "strategy-planning", "audit-ops"}


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = m.group(1)
    out = {}
    for key in ("name", "description"):
        mm = re.search(r"^%s:\s*(.*?)(?=^\w[\w-]*:|\Z)" % key, fm, re.S | re.M)
        if mm:
            out[key] = re.sub(r"\s+", " ", mm.group(1)).strip().strip('"').strip("'")
    return out


def short(desc, limit=180):
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
    s = first if len(first) <= limit else first[:limit].rsplit(" ", 1)[0] + "..."
    return s.replace("|", "/")


def categorize(ident):
    low = ident.lower()
    for cat, pat in CATEGORIES:
        if re.search(pat, low):
            return cat
    return "marketing-other"


def entries():
    with open(os.path.join(ROOT, "community", "sources.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    featured = {f["id"]: f["use_for"] for f in manifest.get("featured", [])}
    out = []
    groups = [("bundle", b["name"], os.path.join("bundles", b["name"])) for b in manifest.get("bundles", [])]
    groups += [("vendor", s["id"], os.path.join("community", "vendor", s["id"])) for s in manifest["sources"]]
    for kind, owner, base in groups:
        for path in sorted(glob.glob(os.path.join(ROOT, base, "**", "SKILL.md"), recursive=True)):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            folder = os.path.basename(os.path.dirname(path))
            fm = frontmatter(path)
            ident = f"{owner}/{fm.get('name') or folder}"
            out.append({"id": ident, "type": "skill", "source": owner, "path": rel,
                        "category": categorize(ident), "featured": ident in featured,
                        "use_for": featured.get(ident, ""), "summary": short(fm.get("description", ""))})
        for path in sorted(glob.glob(os.path.join(ROOT, base, "agents", "*.md"))):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            fm = frontmatter(path)
            ident = f"{owner}/agent:{fm.get('name') or os.path.splitext(os.path.basename(path))[0]}"
            out.append({"id": ident, "type": "agent", "source": owner, "path": rel,
                        "category": categorize(ident), "featured": ident in featured,
                        "use_for": featured.get(ident, ""), "summary": short(fm.get("description", ""))})
    out = [e for e in out if e["id"] not in EXCLUDE]
    missing = set(featured) - {e["id"] for e in out}
    if missing:
        raise SystemExit(f"featured ids not found: {sorted(missing)}")
    return out


def render_md(items):
    lines = ["# Community skill catalog", "",
             "Generated by `scripts/build_catalog.py` - do not edit. Paths are relative to the plugin root",
             "(`${CLAUDE_PLUGIN_ROOT}`). Search this file (e.g. `grep -i tiktok`) rather than reading all of it.",
             "Starred entries are the curated picks listed in `SKILL.md`.", ""]
    order = list(dict.fromkeys([c for c, _ in CATEGORIES if c != "marketing-other"] + ["marketing-other"]))
    for cat in order:
        rows = [e for e in items if e["category"] == cat]
        if not rows:
            continue
        lines += [f"## {cat}" + ("" if cat in ADS_RELEVANT else " (outside paid media - use only if asked)"), "",
                  "| id | type | path | summary |", "|---|---|---|---|"]
        for e in sorted(rows, key=lambda e: (not e["featured"], e["id"])):
            star = "★ " if e["featured"] else ""
            lines.append(f"| {star}`{e['id']}` | {e['type']} | `{e['path']}` | {e['summary']} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    items = entries()
    js = json.dumps({"generated_by": "scripts/build_catalog.py", "count": len(items), "entries": items}, indent=2) + "\n"
    md = render_md(items) + "\n"
    if a.check:
        stale = []
        for path, new in ((CATALOG_JSON, js), (CATALOG_MD, md)):
            old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if old != new:
                stale.append(os.path.relpath(path, ROOT))
        print(json.dumps({"ok": not stale, "stale": stale}))
        return 0 if not stale else 1
    for path, content in ((CATALOG_JSON, js), (CATALOG_MD, md)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
    cats = {}
    for e in items:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"{len(items)} entries: " + ", ".join(f"{k} {v}" for k, v in sorted(cats.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Vendor pinned community skills listed in community/sources.json.

    python scripts/sync_community.py            # sync every source
    python scripts/sync_community.py --check    # verify vendored files match the manifest (no network for files)

Stdlib only. Files come from raw.githubusercontent.com at the pinned commit,
so a sync is reproducible. Each source lands in community/vendor/<id>/ with its
LICENSE and a SOURCE.json recording repo, commit and file list. Only text files
are copied; nothing is executed.
"""

import argparse
import fnmatch
import json
import os
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "community", "sources.json")
VENDOR = os.path.join(ROOT, "community", "vendor")
ALLOWED_LICENSES = {"MIT", "Apache-2.0"}
TEXT_EXT = {".md", ".json", ".txt", ".yaml", ".yml", ""}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-meta-ads-god-mode-sync"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def _lf(data: bytes) -> bytes:
    """Normalize line endings so re-syncs are byte-identical across OSes."""
    return data.replace(b"\r\n", b"\n")


def tree(repo: str, sha: str):
    data = json.loads(_get(f"https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1"))
    return [t["path"] for t in data["tree"] if t["type"] == "blob"]


def matches(path: str, patterns) -> bool:
    for pat in patterns:
        if pat.endswith("/**"):
            if path.startswith(pat[:-3] + "/"):
                return True
        elif fnmatch.fnmatchcase(path, pat) and path.count("/") == pat.count("/"):
            return True
    return False


def sync_source(src: dict) -> dict:
    if src["license"] not in ALLOWED_LICENSES:
        raise SystemExit(f"{src['id']}: license {src['license']} is not allowed for vendoring")
    paths = [p for p in tree(src["repo"], src["sha"]) if matches(p, src["include"])]
    paths = [p for p in paths if os.path.splitext(p)[1].lower() in TEXT_EXT]
    dest = os.path.join(VENDOR, src["id"])
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    files = []
    for p in sorted(paths):
        rel = p[len(src["strip_prefix"]):] if src["strip_prefix"] and p.startswith(src["strip_prefix"]) else p
        out = os.path.join(dest, *rel.split("/"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as fh:
            fh.write(_lf(_get(f"https://raw.githubusercontent.com/{src['repo']}/{src['sha']}/{p}")))
        files.append({"upstream": p, "local": rel})
    with open(os.path.join(dest, "LICENSE"), "wb") as fh:
        fh.write(_lf(_get(f"https://raw.githubusercontent.com/{src['repo']}/{src['sha']}/{src['license_file']}")))
    record = {"id": src["id"], "repo": src["repo"], "sha": src["sha"], "license": src["license"],
              "url": f"https://github.com/{src['repo']}/tree/{src['sha']}", "files": files}
    with open(os.path.join(dest, "SOURCE.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(record, fh, indent=2)
    return record


def check() -> int:
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    problems = []
    for src in manifest["sources"]:
        d = os.path.join(VENDOR, src["id"])
        meta = os.path.join(d, "SOURCE.json")
        if not os.path.exists(meta):
            problems.append(f"{src['id']}: not synced")
            continue
        rec = json.load(open(meta, encoding="utf-8"))
        if rec["sha"] != src["sha"]:
            problems.append(f"{src['id']}: vendored {rec['sha'][:7]} but manifest pins {src['sha'][:7]}")
        if not os.path.exists(os.path.join(d, "LICENSE")):
            problems.append(f"{src['id']}: LICENSE missing")
        for f in rec["files"]:
            if not os.path.exists(os.path.join(d, *f["local"].split("/"))):
                problems.append(f"{src['id']}: missing {f['local']}")
    print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    return 0 if not problems else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", help="sync one source id")
    a = ap.parse_args()
    if a.check:
        return check()
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    for src in manifest["sources"]:
        if a.only and src["id"] != a.only:
            continue
        rec = sync_source(src)
        print(f"{src['id']}: {len(rec['files'])} files @ {src['sha'][:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

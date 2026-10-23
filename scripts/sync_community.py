#!/usr/bin/env python3
"""Vendor pinned community content listed in community/sources.json.

    python scripts/sync_community.py               # sync every source and bundle
    python scripts/sync_community.py --only <id>   # one source or bundle
    python scripts/sync_community.py --check       # verify what is on disk matches the manifest

Two kinds of content:

  sources  -> community/vendor/<id>/   skill text routed by skills/ads-community (not registered as skills)
  bundles  -> bundles/<name>/          whole companion plugins, shipped inside this repo and installed
                                       automatically as dependencies of the `ads` plugin (Claude Code)
                                       or through the Codex marketplace in .agents/plugins/

Stdlib only. Files come from raw.githubusercontent.com at the pinned commit,
so a sync is reproducible. Only text files are copied (no scripts, no code);
each folder keeps the upstream LICENSE and a SOURCE.json with repo, commit and
file map. Bundles also get generated .claude-plugin/ and .codex-plugin/
manifests that keep the upstream name, author, license and version.
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
BUNDLES = os.path.join(ROOT, "bundles")
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


def _raw(repo: str, sha: str, path: str) -> bytes:
    return _lf(_get(f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"))


def _write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def tree(repo: str, sha: str):
    data = json.loads(_get(f"https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1"))
    return [t["path"] for t in data["tree"] if t["type"] == "blob"]


def matches(path: str, patterns) -> bool:
    for pat in patterns:
        if pat.endswith("/**"):
            prefix = pat[:-3]
            if prefix.startswith("**/"):
                if ("/" + prefix[3:] + "/") in ("/" + path):
                    return True
            elif path.startswith(prefix + "/"):
                return True
        elif fnmatch.fnmatchcase(path, pat) and path.count("/") == pat.count("/"):
            return True
    return False


def _select(entry: dict):
    paths = [p for p in tree(entry["repo"], entry["sha"]) if matches(p, entry["include"])]
    paths = [p for p in paths if not matches(p, entry.get("exclude", []))]
    return [p for p in paths if os.path.splitext(p)[1].lower() in TEXT_EXT]


def _copy(entry: dict, dest: str, paths, strip_prefix: str = ""):
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    files = []
    for p in sorted(paths):
        rel = p[len(strip_prefix):] if strip_prefix and p.startswith(strip_prefix) else p
        out = os.path.join(dest, *rel.split("/"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as fh:
            fh.write(_raw(entry["repo"], entry["sha"], p))
        files.append({"upstream": p, "local": rel})
    with open(os.path.join(dest, "LICENSE"), "wb") as fh:
        fh.write(_raw(entry["repo"], entry["sha"], entry["license_file"]))
    return files


def _check_license(entry: dict, label: str) -> None:
    if entry["license"] not in ALLOWED_LICENSES:
        raise SystemExit(f"{label}: license {entry['license']} is not allowed for vendoring")


def sync_source(src: dict) -> dict:
    _check_license(src, src["id"])
    dest = os.path.join(VENDOR, src["id"])
    files = _copy(src, dest, _select(src), src.get("strip_prefix", ""))
    record = {"id": src["id"], "repo": src["repo"], "sha": src["sha"], "license": src["license"],
              "url": f"https://github.com/{src['repo']}/tree/{src['sha']}", "files": files}
    _write_json(os.path.join(dest, "SOURCE.json"), record)
    return record


def sync_bundle(b: dict) -> dict:
    """Copy a whole companion plugin and write Claude Code + Codex manifests for it."""
    _check_license(b, b["name"])
    upstream = json.loads(_get(f"https://raw.githubusercontent.com/{b['repo']}/{b['sha']}/.claude-plugin/plugin.json"))
    dest = os.path.join(BUNDLES, b["name"])
    files = _copy(b, dest, _select(b))
    sha7 = b["sha"][:7]
    skills = b.get("skills", upstream.get("skills", "./skills/"))
    common = {
        "name": b["name"],
        "version": f"{upstream.get('version', '0.0.0')}+{sha7}",
        "description": (f"{upstream.get('description', '').strip()} "
                        f"[Bundled in Claude Meta Ads God Mode from {b['repo']}@{sha7}; "
                        f"Ads God Mode safety rules take precedence.]").strip(),
        "author": upstream.get("author", {"name": b["repo"].split("/")[0]}),
        "homepage": f"https://github.com/{b['repo']}",
        "repository": f"https://github.com/{b['repo']}",
        "license": b["license"],
        "skills": skills,
    }
    _write_json(os.path.join(dest, ".claude-plugin", "plugin.json"), common)
    _write_json(os.path.join(dest, ".codex-plugin", "plugin.json"), common)
    record = {"name": b["name"], "repo": b["repo"], "sha": b["sha"], "license": b["license"],
              "upstream_plugin_name": upstream.get("name"), "upstream_version": upstream.get("version"),
              "url": f"https://github.com/{b['repo']}/tree/{b['sha']}",
              "not_included": b.get("not_included", ""), "files": files}
    _write_json(os.path.join(dest, "SOURCE.json"), record)
    return record


def check() -> int:
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    problems = []
    entries = [(s["id"], os.path.join(VENDOR, s["id"]), s["sha"]) for s in manifest["sources"]]
    entries += [(b["name"], os.path.join(BUNDLES, b["name"]), b["sha"]) for b in manifest.get("bundles", [])]
    for label, d, sha in entries:
        meta = os.path.join(d, "SOURCE.json")
        if not os.path.exists(meta):
            problems.append(f"{label}: not synced")
            continue
        with open(meta, encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec["sha"] != sha:
            problems.append(f"{label}: on disk {rec['sha'][:7]} but manifest pins {sha[:7]}")
        if not os.path.exists(os.path.join(d, "LICENSE")):
            problems.append(f"{label}: LICENSE missing")
        for f in rec["files"]:
            if not os.path.exists(os.path.join(d, *f["local"].split("/"))):
                problems.append(f"{label}: missing {f['local']}")
    print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    return 0 if not problems else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", help="sync one source id or bundle name")
    a = ap.parse_args()
    if a.check:
        return check()
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    for src in manifest["sources"]:
        if a.only and src["id"] != a.only:
            continue
        rec = sync_source(src)
        print(f"source {src['id']}: {len(rec['files'])} files @ {src['sha'][:7]}")
    for b in manifest.get("bundles", []):
        if a.only and b["name"] != a.only:
            continue
        rec = sync_bundle(b)
        print(f"bundle {b['name']}: {len(rec['files'])} files @ {b['sha'][:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

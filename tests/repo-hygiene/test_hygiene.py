"""The repository is public: no secrets, valid manifests, every skill well-formed."""

import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ROOT  # noqa: E402

SECRET_PATTERNS = {
    "meta token": re.compile(r"EAA[A-Za-z0-9]{30,}"),
    "google oauth": re.compile(r"ya29\.[A-Za-z0-9_\-]{30,}"),
    "google refresh": re.compile(r"1//0[A-Za-z0-9_\-]{30,}"),
    "github token": re.compile(r"gh[opsu]_[A-Za-z0-9]{30,}"),
    "private key": re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
    "aws key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "slack": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
TEXT_EXT = {".md", ".py", ".json", ".txt", ".yml", ".yaml", ".toml", ".example", ".sh", ""}


def repo_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if os.path.splitext(f)[1] in TEXT_EXT or f.startswith(".env"):
                yield p


class NoSecrets(unittest.TestCase):
    def test_no_secret_patterns(self):
        hits = []
        for p in repo_files():
            if p.endswith("test_hygiene.py"):
                continue
            text = open(p, encoding="utf-8", errors="ignore").read()
            for name, pat in SECRET_PATTERNS.items():
                if pat.search(text):
                    hits.append(f"{os.path.relpath(p, ROOT)}: {name}")
        self.assertEqual(hits, [])

    def test_no_real_env_file(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, ".env")))

    def test_env_example_has_only_placeholders(self):
        for line in open(os.path.join(ROOT, ".env.example"), encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            value = line.split("=", 1)[1]
            self.assertTrue(value == "" or value.startswith("your-") or value in ("0", "1", "true", "false")
                            or value.startswith("~") or value.startswith("v"), line)

    def test_gitignore_covers_private_data(self):
        gi = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
        for pattern in (".env", ".ads-godmode/", "clients/", "*.token"):
            self.assertIn(pattern, gi)


class Manifests(unittest.TestCase):
    def test_json_files_parse(self):
        for p in repo_files():
            if p.endswith(".json"):
                with open(p, encoding="utf-8") as fh:
                    json.load(fh)

    def test_plugin_manifest(self):
        m = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))
        self.assertEqual(m["name"], "ads")
        self.assertEqual(m["license"], "MIT")

    def test_skills_have_frontmatter(self):
        skills = os.path.join(ROOT, "skills")
        names = []
        for d in sorted(os.listdir(skills)):
            path = os.path.join(skills, d, "SKILL.md")
            self.assertTrue(os.path.exists(path), d)
            text = open(path, encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            self.assertIsNotNone(m, d)
            self.assertIn(f"name: {d}", m.group(1))
            self.assertRegex(m.group(1), r"description: .{40,}")
            self.assertLess(len(text.splitlines()), 500, f"{d} SKILL.md too long for progressive disclosure")
            names.append(d)
        self.assertGreaterEqual(len(names), 12)

    def test_commands_reference_existing_files(self):
        cmds = os.path.join(ROOT, "commands")
        for f in os.listdir(cmds):
            text = open(os.path.join(cmds, f), encoding="utf-8").read()
            for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+\.(?:md|json|py))", text):
                self.assertTrue(os.path.exists(os.path.join(ROOT, ref)), f"{f} -> {ref}")

    def test_markdown_links_resolve(self):
        broken = []
        vendor = os.path.join(ROOT, "community", "vendor")
        for p in repo_files():
            if not p.endswith(".md") or p.startswith(vendor):  # upstream text, kept verbatim
                continue
            for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", open(p, encoding="utf-8").read()):
                if re.match(r"^(https?:|mailto:)", link):
                    continue
                target = os.path.normpath(os.path.join(os.path.dirname(p), link))
                if not os.path.exists(target):
                    broken.append(f"{os.path.relpath(p, ROOT)} -> {link}")
        self.assertEqual(broken, [])


VENDOR = os.path.join(ROOT, "community", "vendor")
HIDDEN_UNICODE = re.compile("[​-‏‪-‮⁠-⁤﻿]")


def vendored_files():
    for dirpath, _, files in os.walk(VENDOR):
        for f in files:
            yield os.path.join(dirpath, f)


class CommunityVendoring(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "community", "sources.json"), encoding="utf-8") as fh:
            self.manifest = json.load(fh)

    def test_only_permissive_licenses_vendored(self):
        for src in self.manifest["sources"]:
            self.assertIn(src["license"], ("MIT", "Apache-2.0"), src["id"])

    def test_every_source_synced_with_license_and_pinned_sha(self):
        for src in self.manifest["sources"]:
            self.assertRegex(src["sha"], r"^[0-9a-f]{40}$")
            d = os.path.join(VENDOR, src["id"])
            self.assertTrue(os.path.exists(os.path.join(d, "LICENSE")), src["id"])
            with open(os.path.join(d, "SOURCE.json"), encoding="utf-8") as fh:
                rec = json.load(fh)
            self.assertEqual(rec["sha"], src["sha"], src["id"])
            for f in rec["files"]:
                self.assertTrue(os.path.exists(os.path.join(d, *f["local"].split("/"))), f["local"])

    def test_no_executables_vendored(self):
        for p in vendored_files():
            self.assertNotRegex(p, r"\.(py|sh|js|ts|exe|bat|ps1|cmd)$")

    def test_vendored_skills_not_auto_registered(self):
        # community skills stay out of skills/ so their descriptions do not load into every session
        for d in os.listdir(os.path.join(ROOT, "skills")):
            self.assertFalse(os.path.exists(os.path.join(ROOT, "skills", d, "SOURCE.json")), d)

    def test_no_hidden_unicode_in_vendored_text(self):
        for p in vendored_files():
            with open(p, encoding="utf-8", errors="ignore") as fh:
                self.assertIsNone(HIDDEN_UNICODE.search(fh.read()), p)

    def test_umbrella_index_paths_exist(self):
        with open(os.path.join(ROOT, "skills", "ads-community", "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        ids = "|".join(re.escape(s["id"]) for s in self.manifest["sources"])
        refs = re.findall(r"`((?:%s)/[^`{*]+?)`" % ids, text)
        self.assertGreater(len(refs), 20)
        for ref in refs:
            self.assertTrue(os.path.exists(os.path.join(VENDOR, *ref.rstrip("/").split("/"))), ref)


if __name__ == "__main__":
    unittest.main()

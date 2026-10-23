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
        for p in repo_files():
            if not p.endswith(".md"):
                continue
            for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", open(p, encoding="utf-8").read()):
                if re.match(r"^(https?:|mailto:)", link):
                    continue
                target = os.path.normpath(os.path.join(os.path.dirname(p), link))
                if not os.path.exists(target):
                    broken.append(f"{os.path.relpath(p, ROOT)} -> {link}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()

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
        upstream = (os.path.join(ROOT, "community", "vendor"), os.path.join(ROOT, "bundles"))
        for p in repo_files():
            if not p.endswith(".md") or p.startswith(upstream):  # upstream text, kept verbatim
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


BUNDLES = os.path.join(ROOT, "bundles")


def vendored_files():
    for base in (VENDOR, BUNDLES):
        for dirpath, _, files in os.walk(base):
            for f in files:
                yield os.path.join(dirpath, f)


def load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


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


class BundledCompanions(unittest.TestCase):
    def setUp(self):
        self.manifest = load_json("community", "sources.json")
        self.bundles = {b["name"]: b for b in self.manifest["bundles"]}
        self.plugin = load_json(".claude-plugin", "plugin.json")
        self.market = load_json(".claude-plugin", "marketplace.json")
        self.codex_market = load_json(".agents", "plugins", "marketplace.json")

    def test_bundles_synced_pinned_and_licensed(self):
        for name, b in self.bundles.items():
            d = os.path.join(BUNDLES, name)
            self.assertIn(b["license"], ("MIT", "Apache-2.0"))
            self.assertRegex(b["sha"], r"^[0-9a-f]{40}$")
            self.assertTrue(os.path.exists(os.path.join(d, "LICENSE")), name)
            self.assertEqual(load_json("bundles", name, "SOURCE.json")["sha"], b["sha"])
            for kind in (".claude-plugin", ".codex-plugin"):
                m = load_json("bundles", name, kind, "plugin.json")
                self.assertEqual(m["name"], name)
                self.assertEqual(m["license"], b["license"])
                self.assertIn(b["repo"], m["repository"])
                skills = m["skills"] if isinstance(m["skills"], list) else [m["skills"]]
                for sk in skills:
                    self.assertTrue(os.path.isdir(os.path.join(d, sk)), f"{name}: {sk}")

    def test_companions_not_preloaded_by_default(self):
        # on-demand routing: installing ads must not register ~17k tokens of companion skills
        self.assertFalse(self.plugin.get("dependencies"))

    def test_optional_hosted_plugins_are_never_dependencies(self):
        for o in self.manifest.get("optional_plugins", []):
            self.assertNotIn(o["name"], self.plugin.get("dependencies", []))

    def test_claude_marketplace_serves_bundles_from_this_repo(self):
        entries = {p["name"]: p for p in self.market["plugins"]}
        self.assertEqual(entries["ads"]["source"], "./")
        for name in self.bundles:
            self.assertEqual(entries[name]["source"], f"./bundles/{name}")
        for o in self.manifest.get("optional_plugins", []):
            self.assertRegex(entries[o["name"]]["source"]["sha"], r"^[0-9a-f]{40}$")  # remote entries pinned

    def test_codex_marketplace_lists_everything_locally(self):
        entries = {p["name"]: p for p in self.codex_market["plugins"]}
        self.assertEqual(set(entries), {"ads", *self.bundles})
        for name, e in entries.items():
            self.assertEqual(e["source"]["source"], "local")
            path = os.path.join(ROOT, e["source"]["path"])
            self.assertTrue(os.path.exists(os.path.join(path, ".codex-plugin", "plugin.json")), name)
        self.assertEqual(load_json(".codex-plugin", "plugin.json")["name"], "ads")

    def test_installer_commands(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("install", os.path.join(ROOT, "scripts", "install.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        claude = [" ".join(c) for c in mod.claude_cmds("owner/repo", "user", False)]
        self.assertIn("claude plugin install ads@claude-meta-ads-god-mode --scope user", claude)
        self.assertFalse(any("adplane" in c for c in claude))
        self.assertFalse(any(name in c for c in claude for name in self.bundles))
        native = [" ".join(c) for c in mod.claude_cmds("owner/repo", "user", False, native=True)]
        for name in self.bundles:
            self.assertIn(f"claude plugin install {name}@claude-meta-ads-god-mode --scope user", native)
        codex = [" ".join(c) for c in mod.codex_cmds("owner/repo")]
        self.assertEqual([c for c in codex if " add " in c and "marketplace" not in c],
                         ["codex plugin add ads@claude-meta-ads-god-mode"])
        codex_native = [" ".join(c) for c in mod.codex_cmds("owner/repo", native=True)]
        for name in ["ads", *self.bundles]:
            self.assertIn(f"codex plugin add {name}@claude-meta-ads-god-mode", codex_native)


def expand_braces(path):
    m = __import__("re").search(r"\{([^}]*)\}", path)
    if not m:
        return [path]
    out = []
    for part in m.group(1).split(","):
        out += expand_braces(path[:m.start()] + part + path[m.end():])
    return out


class OnDemandRouter(unittest.TestCase):
    def setUp(self):
        self.catalog = load_json("community", "catalog.json")["entries"]
        with open(os.path.join(ROOT, "skills", "ads-community", "SKILL.md"), encoding="utf-8") as fh:
            self.router = fh.read()

    def test_catalog_is_fresh(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_catalog", os.path.join(ROOT, "scripts", "build_catalog.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        items = mod.entries()
        self.assertEqual(len(items), len(self.catalog), "run python scripts/build_catalog.py")
        with open(mod.CATALOG_MD, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), mod.render_md(items) + "\n", "run python scripts/build_catalog.py")

    def test_catalog_paths_exist_and_cover_every_bundled_skill(self):
        paths = {e["path"] for e in self.catalog}
        for p in paths:
            self.assertTrue(os.path.exists(os.path.join(ROOT, p)), p)
        for base in ("bundles", os.path.join("community", "vendor")):
            for dirpath, _, files in os.walk(os.path.join(ROOT, base)):
                if "SKILL.md" in files:
                    rel = os.path.relpath(os.path.join(dirpath, "SKILL.md"), ROOT).replace(os.sep, "/")
                    if rel.endswith("ads-setup/SKILL.md"):
                        continue  # upstream installer skill, intentionally excluded
                    self.assertIn(rel, paths)

    def test_featured_picks_exist(self):
        featured = [e for e in self.catalog if e["featured"]]
        self.assertGreaterEqual(len(featured), 20)

    def test_router_paths_resolve(self):
        refs = __import__("re").findall(r"`((?:community/vendor|bundles)/[^`]+?\.md)`", self.router)
        self.assertGreater(len(refs), 15)
        for ref in refs:
            for p in expand_braces(ref):
                self.assertTrue(os.path.exists(os.path.join(ROOT, *p.split("/"))), p)

    def test_router_is_lean(self):
        self.assertLess(len(self.router.splitlines()), 120)


if __name__ == "__main__":
    unittest.main()

import contextlib
import importlib.util
import io
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ROOT  # noqa: E402


def load_router():
    spec = importlib.util.spec_from_file_location("skill_router", os.path.join(ROOT, "hooks", "skill_router.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ROUTER = load_router()


def ids(prompt):
    entries, _ = ROUTER.pick(prompt)
    return [e["id"] for e in entries]


def run_hook(prompt):
    out = io.StringIO()
    with mock.patch.object(sys, "stdin", io.StringIO(json.dumps({"prompt": prompt}))), contextlib.redirect_stdout(out):
        code = ROUTER.main()
    return code, out.getvalue()


class Routing(unittest.TestCase):
    def test_platforms(self):
        self.assertEqual(ids("Audit my TikTok ads for Spark Ads issues"), ["agrici-ads/ads-tiktok"])
        self.assertEqual(ids("plan a LinkedIn ads campaign for ABM"), ["agrici-ads/ads-linkedin"])
        self.assertEqual(ids("are our Microsoft Ads wasting money"), ["agrici-ads/ads-microsoft"])
        self.assertEqual(ids("our ACOS on Sponsored Products is 60%"), ["agrici-ads/ads-amazon"])

    def test_specialist_topics(self):
        self.assertEqual(ids("is my best meta video ad fatigued?"),
                         ["ad-creative-skills/creative-fatigue-read-ad-creative"])
        self.assertEqual(ids("what sample size do I need for an A/B test of two landing pages"),
                         ["marketing-skills/ab-testing"])
        self.assertEqual(ids("set up GTM for our Calendly bookings"),
                         ["marketing-skills/conversion-tracking", "agrici-ads/ads-server-side-tracking"])

    def test_context_gated_rules_need_ads_context(self):
        self.assertEqual(ids("I love reddit"), [])
        self.assertEqual(ids("run reddit ads for our app"), ["agrici-ads/ads-reddit"])
        self.assertEqual(ids("write a hook for my song"), [])

    def test_core_meta_google_requests_get_core_pointer_only(self):
        entries, ads_ctx = ROUTER.pick("review D-Hauss Meta ads this week")
        self.assertEqual(entries, [])
        self.assertTrue(ads_ctx)

    def test_max_two_picks(self):
        self.assertLessEqual(len(ids("tiktok linkedin youtube amazon pinterest ads and an a/b test and fatigue")), 2)

    def test_every_rule_pick_exists_in_catalog(self):
        with open(os.path.join(ROOT, "community", "router_rules.json"), encoding="utf-8") as fh:
            rules = json.load(fh)
        with open(os.path.join(ROOT, "community", "catalog.json"), encoding="utf-8") as fh:
            catalog = {e["id"] for e in json.load(fh)["entries"]}
        for r in rules["rules"]:
            for p in r["picks"]:
                self.assertIn(p, catalog, r["pattern"])


class HookBehaviour(unittest.TestCase):
    def test_no_output_for_unrelated_prompts(self):
        self.assertEqual(run_hook("write me a poem about the sea"), (0, ""))

    def test_slash_commands_are_left_alone(self):
        self.assertEqual(run_hook("/ads:audit D-Hauss tiktok"), (0, ""))

    def test_output_shape_and_paths(self):
        code, out = run_hook("audit my tiktok ads")
        ctx = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(ctx["hookEventName"], "UserPromptSubmit")
        self.assertIn("ads:ads-core", ctx["additionalContext"])
        self.assertIn("bundles/agrici-ads/skills/ads-tiktok/SKILL.md", ctx["additionalContext"])

    def test_never_breaks_on_bad_input(self):
        with mock.patch.object(sys, "stdin", io.StringIO("not json")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ROUTER.main(), 0)


if __name__ == "__main__":
    unittest.main()

"""Shared fixtures: a throwaway ADS_GODMODE_HOME with two fake clients.

No test touches a real ad account or network. Account ids are fake.
"""

import copy
import json
import os
import shutil
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

ALPHA_META = "act_111111111"
ALPHA_GOOGLE = "1111111111"
BETA_META = "act_222222222"
BETA_GOOGLE = "2222222222"


def make_profile(slug, name, meta_acct, google_cid, mode="approval", aliases=None, guarded=None):
    with open(os.path.join(ROOT, "templates", "client-profile.json"), encoding="utf-8") as fh:
        p = json.load(fh)
    p["slug"] = slug
    p["aliases"] = aliases or []
    p["business"]["name"] = name
    p["platforms"]["meta"]["ad_account_ids"] = [meta_acct]
    p["platforms"]["google"]["customer_ids"] = [google_cid]
    p["automation"]["mode"] = mode
    if guarded is not None:
        p["automation"]["guarded_auto"].update(guarded)
    return p


class Sandbox(unittest.TestCase):
    """Base TestCase: fresh home dir, clients alpha + beta, alpha active."""

    alpha_mode = "approval"

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="adsgm-test-")
        self._old_env = {k: os.environ.get(k) for k in ("ADS_GODMODE_HOME", "ADS_GODMODE_ENABLE_FULL_AUTO",
                                                        "ADS_GODMODE_AUDIT_LOG")}
        os.environ["ADS_GODMODE_HOME"] = self.tmp
        os.environ.pop("ADS_GODMODE_ENABLE_FULL_AUTO", None)
        os.environ.pop("ADS_GODMODE_AUDIT_LOG", None)
        from godmode import paths
        paths.ensure_dirs()
        self.write_client(make_profile("alpha-remodeling", "Alpha Remodeling", ALPHA_META, ALPHA_GOOGLE,
                                       self.alpha_mode, aliases=["Alpha", "D-Alpha"]))
        self.write_client(make_profile("beta-roofing", "Beta Roofing", BETA_META, BETA_GOOGLE, "approval"))
        from godmode import session
        session.set_active("alpha-remodeling")

    def tearDown(self):
        for k, v in self._old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_client(self, data):
        from godmode import paths
        with open(paths.clients_dir() / f"{data['slug']}.json", "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def set_mode(self, mode, guarded=None):
        from godmode import profiles
        p = copy.deepcopy(profiles.load("alpha-remodeling").data)
        p["automation"]["mode"] = mode
        if guarded:
            p["automation"]["guarded_auto"].update(guarded)
        self.write_client(p)

    @staticmethod
    def hook(tool_name, tool_input, permission_mode="default"):
        return {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input,
                "permission_mode": permission_mode}

    def plan(self, *argv):
        """Run `adsgm plan ...` in-process and return parsed JSON + exit code."""
        import contextlib
        import io
        from godmode import cli
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(["plan", *argv])
        return json.loads(buf.getvalue()), code


META = "mcp__plugin_ads_meta-ads__"
META_SELF = "mcp__meta-ads-selfhosted__"
GOOGLE = "mcp__google-ads-mcp__"


# ---------------------------------------------------------------- fake google-ads client

class Auto:
    """Proto-plus stand-in: any attribute auto-creates; supports append/extend."""

    def __init__(self):
        object.__setattr__(self, "_d", {})

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        d = object.__getattribute__(self, "_d")
        if k not in d:
            d[k] = Auto()
        return d[k]

    def __setattr__(self, k, v):
        self._d[k] = v

    def append(self, v):
        self._d.setdefault("_items", []).append(v)

    def extend(self, vs):
        self._d.setdefault("_items", []).extend(vs)

    @property
    def items(self):
        return self._d.get("_items", [])


class _EnumType:
    def __init__(self, name):
        self.name = name

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return f"{self.name}.{k}"

    def __getitem__(self, k):
        return f"{self.name}.{k}"


class _Enums:
    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return _EnumType(k)


class FakeGoogleAdsService:
    def __init__(self):
        self.requests = []

    def __getattr__(self, k):
        if k.endswith("_path"):
            return lambda *ids: f"customers/{ids[0]}/{k[:-5]}s/{'~'.join(str(i) for i in ids[1:])}"
        raise AttributeError(k)

    def mutate(self, request):
        self.requests.append(request)
        resp = Auto()
        resp.mutate_operation_responses = []
        return resp


class FakeGoogleAdsClient:
    def __init__(self):
        self.enums = _Enums()
        self.service = FakeGoogleAdsService()

    def get_service(self, name):
        return self.service

    def get_type(self, name):
        return Auto()

    def copy_from(self, dst, src):
        pass


def install_fake_protobuf():
    try:
        from google.protobuf import field_mask_pb2  # noqa: F401
        return
    except ImportError:
        pass
    google = sys.modules.setdefault("google", types.ModuleType("google"))
    pb = types.ModuleType("google.protobuf")
    fm = types.ModuleType("google.protobuf.field_mask_pb2")
    fm.FieldMask = lambda paths=None: {"paths": paths}
    pb.field_mask_pb2 = fm
    google.protobuf = pb
    sys.modules["google.protobuf"] = pb
    sys.modules["google.protobuf.field_mask_pb2"] = fm

"""Client profiles: load, validate, resolve and enforce account ownership.

A profile is one JSON file per client in ADS_GODMODE_HOME/clients/<slug>.json.
Every write decision starts by asking "does this account belong to the active
client?" and the answer comes only from these files, never from whatever ad
account the connector happens to have selected.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from . import paths

AUTOMATION_MODES = ("read_only", "draft", "approval", "guarded_auto", "full_auto")
PLATFORMS = ("meta", "google")

_META_ACCOUNT_RE = re.compile(r"^(?:act_)?(\d{5,20})$")
_GOOGLE_CUSTOMER_RE = re.compile(r"^\d{3}-?\d{3}-?\d{4}$")


class ProfileError(Exception):
    pass


def normalize_account_id(platform: str, account_id) -> str:
    """Canonical form: Meta 'act_<digits>', Google 10 digits without dashes."""
    raw = str(account_id).strip()
    if platform == "meta":
        m = _META_ACCOUNT_RE.match(raw)
        if not m:
            raise ProfileError(f"Not a Meta ad account id: {raw!r}")
        return f"act_{m.group(1)}"
    if platform == "google":
        if not _GOOGLE_CUSTOMER_RE.match(raw):
            raise ProfileError(f"Not a Google Ads customer id: {raw!r}")
        return raw.replace("-", "")
    raise ProfileError(f"Unknown platform: {platform!r}")


@dataclass
class Profile:
    slug: str
    data: Dict = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.data.get("business", {}).get("name", self.slug)

    @property
    def aliases(self) -> List[str]:
        return list(self.data.get("aliases", []))

    @property
    def mode(self) -> str:
        return self.data.get("automation", {}).get("mode", "read_only")

    @property
    def guarded_limits(self) -> Dict:
        return self.data.get("automation", {}).get("guarded_auto", {})

    @property
    def approval(self) -> Dict:
        return self.data.get("approval", {})

    def platform_config(self, platform: str) -> Dict:
        return self.data.get("platforms", {}).get(platform, {})

    def platform_enabled(self, platform: str) -> bool:
        cfg = self.platform_config(platform)
        return bool(cfg) and cfg.get("enabled", True)

    def account_ids(self, platform: str) -> List[str]:
        cfg = self.platform_config(platform)
        key = "ad_account_ids" if platform == "meta" else "customer_ids"
        out = []
        for acc in cfg.get(key, []):
            try:
                out.append(normalize_account_id(platform, acc))
            except ProfileError:
                continue
        return out

    def owns(self, platform: str, account_id) -> bool:
        try:
            acc = normalize_account_id(platform, account_id)
        except ProfileError:
            return False
        return self.platform_enabled(platform) and acc in self.account_ids(platform)


def validate(data: Dict) -> List[str]:
    """Return a list of problems. Empty list means valid."""
    errors = []
    slug = data.get("slug")
    if not slug or not re.match(r"^[a-z0-9][a-z0-9-]{1,62}$", str(slug)):
        errors.append("slug must be lowercase letters, digits and dashes")
    if not data.get("business", {}).get("name"):
        errors.append("business.name is required")
    mode = data.get("automation", {}).get("mode", "read_only")
    if mode not in AUTOMATION_MODES:
        errors.append(f"automation.mode must be one of {AUTOMATION_MODES}")
    platforms = data.get("platforms", {})
    if not platforms:
        errors.append("at least one platform is required")
    for platform, cfg in platforms.items():
        if platform not in PLATFORMS:
            errors.append(f"unsupported platform {platform!r}")
            continue
        key = "ad_account_ids" if platform == "meta" else "customer_ids"
        accounts = cfg.get(key, [])
        if cfg.get("enabled", True) and not accounts:
            errors.append(f"platforms.{platform}.{key} is empty")
        for acc in accounts:
            try:
                normalize_account_id(platform, acc)
            except ProfileError as exc:
                errors.append(f"platforms.{platform}: {exc}")
    limits = data.get("automation", {}).get("guarded_auto", {})
    for k in ("max_budget_increase_pct", "max_budget_decrease_pct"):
        v = limits.get(k)
        if v is not None and not (0 <= float(v) <= 100):
            errors.append(f"automation.guarded_auto.{k} must be between 0 and 100")
    return errors


def load_file(path: Path) -> Profile:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"Cannot read profile {path}: {exc}") from exc
    errors = validate(data)
    if errors:
        raise ProfileError(f"Invalid profile {path}: " + "; ".join(errors))
    return Profile(slug=data["slug"], data=data)


def load(slug: str) -> Profile:
    path = paths.clients_dir() / f"{slug}.json"
    if not path.exists():
        raise ProfileError(f"No client profile named {slug!r} in {paths.clients_dir()}")
    profile = load_file(path)
    if profile.slug != slug:
        raise ProfileError(f"Profile file {path.name} declares slug {profile.slug!r}")
    return profile


def list_all() -> List[Profile]:
    d = paths.clients_dir()
    if not d.exists():
        return []
    return [load_file(p) for p in sorted(d.glob("*.json"))]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def resolve(query: str, profiles: Optional[List[Profile]] = None) -> Profile:
    """Resolve 'D-Hauss', 'dhauss', or a slug to exactly one profile.

    Raises ProfileError when nothing matches or more than one profile matches;
    a guess between clients is never acceptable.
    """
    profiles = list_all() if profiles is None else profiles
    q = _norm(query)
    if not q:
        raise ProfileError("Empty client name")
    exact, partial = [], []
    for p in profiles:
        names = [p.slug, p.name] + p.aliases
        normed = [_norm(n) for n in names if n]
        if q in normed:
            exact.append(p)
        elif any(q in n or (len(n) >= 4 and n in q) for n in normed):
            partial.append(p)
    matches = exact or partial
    if not matches:
        raise ProfileError(f"No client matches {query!r}. Run /ads:onboard to add one.")
    if len(matches) > 1:
        names = ", ".join(sorted(p.slug for p in matches))
        raise ProfileError(f"{query!r} is ambiguous: {names}. Name the client exactly.")
    return matches[0]


def owner_of(platform: str, account_id, profiles: Optional[List[Profile]] = None) -> List[str]:
    """Slugs of every profile that claims this account (should be 0 or 1)."""
    profiles = list_all() if profiles is None else profiles
    return [p.slug for p in profiles if p.owns(platform, account_id)]


def isolation_problems(profiles: Optional[List[Profile]] = None) -> List[str]:
    """Detect one account listed under two clients - a wrong-account risk."""
    profiles = list_all() if profiles is None else profiles
    seen: Dict[str, str] = {}
    problems = []
    for p in profiles:
        for platform in PLATFORMS:
            for acc in p.account_ids(platform):
                key = f"{platform}:{acc}"
                if key in seen and seen[key] != p.slug:
                    problems.append(f"{key} is listed under both {seen[key]} and {p.slug}")
                seen[key] = p.slug
    return problems

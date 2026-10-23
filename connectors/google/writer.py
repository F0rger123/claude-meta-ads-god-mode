"""Google Ads write layer (the official Google Ads API, via Google's `google-ads` client).

The official Google Ads MCP is read-only, so writes go through here. A plan is
a JSON file Claude writes after reading the account:

    {
      "client": "example-remodeling",
      "customer_id": "1234567890",
      "operations": [
        {"op": "update_budget", "campaign_budget_id": "111", "amount": 60.0},
        {"op": "set_status", "resource": "campaign", "id": "222", "status": "PAUSED"},
        {"op": "add_negative_keywords", "campaign_id": "222",
         "keywords": [{"text": "free", "match_type": "PHRASE"}]},
        {"op": "create_search_campaign", "name": "...", "daily_budget": 50,
         "bidding": {"strategy": "maximize_conversions", "target_cpa": 80},
         "locations": ["1025197"], "proximity": {"lat": 39.96, "lng": -76.73, "radius_miles": 15},
         "languages": ["1000"], "negative_keywords": [...],
         "ad_groups": [{"name": "...", "keywords": [...], "rsa": {...}}]}
      ]
    }

Safety:
  * validate_only=True unless execute=True. validate_only makes Google check
    the whole mutate and change nothing.
  * execute=True requires an open ticket for this client/account/action/entities.
  * create_search_campaign always creates the campaign PAUSED; a status field is rejected.
  * customer_id must belong to the active client profile.
"""

from typing import Dict, List, Optional, Tuple

from godmode import actions as A
from godmode import profiles, session, tickets
from godmode.budget import to_micros

MATCH_TYPES = {"EXACT", "PHRASE", "BROAD"}
STATUSES = {"ENABLED", "PAUSED", "REMOVED"}
STATUS_RESOURCES = {"campaign", "ad_group", "ad_group_ad", "ad_group_criterion"}
BIDDING = {"maximize_conversions", "maximize_clicks", "manual_cpc", "target_cpa"}


class PlanError(Exception):
    pass


def _kw(kws: List[Dict], where: str) -> List[Dict]:
    out = []
    for k in kws or []:
        text = str(k.get("text", "")).strip()
        mt = str(k.get("match_type", "PHRASE")).upper()
        if not text or len(text) > 80:
            raise PlanError(f"{where}: keyword text must be 1-80 characters")
        if mt not in MATCH_TYPES:
            raise PlanError(f"{where}: match_type must be one of {sorted(MATCH_TYPES)}")
        out.append({"text": text, "match_type": mt})
    return out


def _rsa(rsa: Dict, where: str) -> Dict:
    heads = [str(h) for h in rsa.get("headlines", [])]
    descs = [str(d) for d in rsa.get("descriptions", [])]
    if not 3 <= len(heads) <= 15 or any(len(h) > 30 for h in heads):
        raise PlanError(f"{where}: RSA needs 3-15 headlines of at most 30 characters")
    if not 2 <= len(descs) <= 4 or any(len(d) > 90 for d in descs):
        raise PlanError(f"{where}: RSA needs 2-4 descriptions of at most 90 characters")
    url = str(rsa.get("final_url", ""))
    if not url.startswith("https://"):
        raise PlanError(f"{where}: RSA final_url must be an https URL")
    for p in ("path1", "path2"):
        if len(str(rsa.get(p, ""))) > 15:
            raise PlanError(f"{where}: {p} must be at most 15 characters")
    return {"headlines": heads, "descriptions": descs, "final_url": url,
            "path1": rsa.get("path1", ""), "path2": rsa.get("path2", "")}


def normalize(plan: Dict) -> List[Dict]:
    """Validate a plan and return normalized operation specs. Pure; no API calls."""
    ops = plan.get("operations")
    if not ops:
        raise PlanError("plan has no operations")
    specs = []
    for i, op in enumerate(ops):
        kind = op.get("op")
        where = f"operations[{i}] ({kind})"
        if kind == "update_budget":
            amount = float(op["amount"])
            if amount <= 0:
                raise PlanError(f"{where}: amount must be positive")
            specs.append({"op": kind, "campaign_budget_id": str(op["campaign_budget_id"]),
                          "amount": amount, "amount_micros": to_micros(amount)})
        elif kind == "set_status":
            res, status = op.get("resource"), str(op.get("status", "")).upper()
            if res not in STATUS_RESOURCES or status not in STATUSES:
                raise PlanError(f"{where}: resource in {sorted(STATUS_RESOURCES)}, status in {sorted(STATUSES)}")
            spec = {"op": kind, "resource": res, "id": str(op["id"]), "status": status}
            if res in ("ad_group_ad", "ad_group_criterion"):
                spec["ad_group_id"] = str(op["ad_group_id"])
            specs.append(spec)
        elif kind == "add_negative_keywords":
            specs.append({"op": kind, "campaign_id": str(op["campaign_id"]),
                          "keywords": _kw(op.get("keywords"), where)})
        elif kind == "create_search_campaign":
            if "status" in op:
                raise PlanError(f"{where}: do not set status; campaigns are always created PAUSED")
            budget = float(op["daily_budget"])
            if budget <= 0:
                raise PlanError(f"{where}: daily_budget must be positive")
            bidding = dict(op.get("bidding") or {"strategy": "maximize_conversions"})
            if bidding.get("strategy") not in BIDDING:
                raise PlanError(f"{where}: bidding.strategy must be one of {sorted(BIDDING)}")
            if not op.get("locations") and not op.get("proximity"):
                raise PlanError(f"{where}: geographic targeting (locations or proximity) is required")
            groups = []
            for j, g in enumerate(op.get("ad_groups") or []):
                gw = f"{where}.ad_groups[{j}]"
                groups.append({"name": str(g["name"]), "cpc_bid": g.get("cpc_bid"),
                               "keywords": _kw(g.get("keywords"), gw),
                               "rsa": _rsa(g["rsa"], gw) if g.get("rsa") else None})
            if not groups:
                raise PlanError(f"{where}: at least one ad group is required")
            specs.append({"op": kind, "name": str(op["name"]), "daily_budget": budget,
                          "daily_budget_micros": to_micros(budget), "bidding": bidding,
                          "locations": [str(l) for l in op.get("locations", [])],
                          "proximity": op.get("proximity"),
                          "languages": [str(l) for l in op.get("languages", ["1000"])],
                          "negative_keywords": _kw(op.get("negative_keywords"), where),
                          "search_partners": bool(op.get("search_partners", False)),
                          "ad_groups": groups, "status": "PAUSED"})
        else:
            raise PlanError(f"{where}: unknown op")
    return specs


_RISK = [A.DELETE, A.ACTIVATE, A.BUDGET, A.NEGATIVE_KEYWORDS, A.PAUSE, A.CREATE]


def plan_action(specs: List[Dict]) -> str:
    """The single action class a ticket must cover (the riskiest in the plan)."""
    found = set()
    for s in specs:
        if s["op"] == "update_budget":
            found.add(A.BUDGET)
        elif s["op"] == "set_status":
            found.add({"ENABLED": A.ACTIVATE, "PAUSED": A.PAUSE, "REMOVED": A.DELETE}[s["status"]])
        elif s["op"] == "add_negative_keywords":
            found.add(A.NEGATIVE_KEYWORDS)
        else:
            found.add(A.CREATE)
    for a in _RISK:
        if a in found:
            return a
    return A.UNKNOWN_WRITE


def plan_entities(specs: List[Dict]) -> List[str]:
    ids = []
    for s in specs:
        for k in ("campaign_budget_id", "id", "campaign_id"):
            if k in s and s[k] not in ids:
                ids.append(s[k])
    return ids


def check_plan(plan: Dict) -> Tuple[profiles.Profile, str, List[Dict]]:
    active = session.get_active()
    if not active:
        raise PlanError("no active client; run `adsgm use <client>`")
    if plan.get("client") != active:
        raise PlanError(f"plan is for {plan.get('client')!r} but the active client is {active!r}")
    profile = profiles.load(active)
    cid = profiles.normalize_account_id("google", plan.get("customer_id", ""))
    if not profile.owns("google", cid):
        owners = profiles.owner_of("google", cid)
        raise PlanError(f"WRONG ACCOUNT: {cid} is not a Google Ads account of {active}"
                        + (f" (it belongs to {', '.join(owners)})" if owners else ""))
    return profile, cid, normalize(plan)


def verify_ticket(ticket_id: Optional[str], client: str, cid: str, specs: List[Dict]) -> Dict:
    t = tickets.get(ticket_id) if ticket_id else None
    if not t:
        raise PlanError("--execute requires --ticket from `adsgm plan`")
    if t.get("consumed"):
        raise PlanError(f"ticket {ticket_id} was already used")
    if t["client"] != client or t["platform"] != "google" or t["account_id"] != cid:
        raise PlanError(f"ticket {ticket_id} does not match client/platform/account")
    if t["action"] != plan_action(specs):
        raise PlanError(f"ticket covers {t['action']} but plan is {plan_action(specs)}")
    missing = set(plan_entities(specs)) - set(t["entity_ids"])
    if missing:
        raise PlanError(f"ticket does not cover entities {sorted(missing)}")
    if t["decision"]["verdict"] == "blocked":
        raise PlanError("ticket verdict is blocked")
    return t


# ---------------------------------------------------------------- API layer

def _to_mutate_operations(client, cid: str, specs: List[Dict]):
    from google.protobuf import field_mask_pb2  # provided by google-ads

    svc = client.get_service("GoogleAdsService")
    enums = client.enums
    ops = []
    tmp = [0]

    def temp_id() -> int:
        tmp[0] -= 1
        return tmp[0]

    def new_op():
        mo = client.get_type("MutateOperation")
        ops.append(mo)
        return mo

    def neg_keyword_ops(campaign_rn, kws):
        for k in kws:
            c = new_op().campaign_criterion_operation.create
            c.campaign = campaign_rn
            c.negative = True
            c.keyword.text = k["text"]
            c.keyword.match_type = enums.KeywordMatchTypeEnum[k["match_type"]]

    for s in specs:
        if s["op"] == "update_budget":
            mo = new_op()
            b = mo.campaign_budget_operation.update
            b.resource_name = svc.campaign_budget_path(cid, s["campaign_budget_id"])
            b.amount_micros = s["amount_micros"]
            client.copy_from(mo.campaign_budget_operation.update_mask, field_mask_pb2.FieldMask(paths=["amount_micros"]))
        elif s["op"] == "set_status":
            mo = new_op()
            res = s["resource"]
            if res == "campaign":
                obj, path = mo.campaign_operation, svc.campaign_path(cid, s["id"])
                status = enums.CampaignStatusEnum[s["status"]]
            elif res == "ad_group":
                obj, path = mo.ad_group_operation, svc.ad_group_path(cid, s["id"])
                status = enums.AdGroupStatusEnum[s["status"]]
            elif res == "ad_group_ad":
                obj, path = mo.ad_group_ad_operation, svc.ad_group_ad_path(cid, s["ad_group_id"], s["id"])
                status = enums.AdGroupAdStatusEnum[s["status"]]
            else:
                obj, path = mo.ad_group_criterion_operation, svc.ad_group_criterion_path(cid, s["ad_group_id"], s["id"])
                status = enums.AdGroupCriterionStatusEnum[s["status"]]
            obj.update.resource_name = path
            obj.update.status = status
            client.copy_from(obj.update_mask, field_mask_pb2.FieldMask(paths=["status"]))
        elif s["op"] == "add_negative_keywords":
            neg_keyword_ops(svc.campaign_path(cid, s["campaign_id"]), s["keywords"])
        elif s["op"] == "create_search_campaign":
            budget_rn = svc.campaign_budget_path(cid, temp_id())
            b = new_op().campaign_budget_operation.create
            b.resource_name = budget_rn
            b.name = f"{s['name']} budget"
            b.amount_micros = s["daily_budget_micros"]
            b.delivery_method = enums.BudgetDeliveryMethodEnum.STANDARD
            b.explicitly_shared = False

            campaign_rn = svc.campaign_path(cid, temp_id())
            c = new_op().campaign_operation.create
            c.resource_name = campaign_rn
            c.name = s["name"]
            c.advertising_channel_type = enums.AdvertisingChannelTypeEnum.SEARCH
            c.status = enums.CampaignStatusEnum.PAUSED
            c.campaign_budget = budget_rn
            c.network_settings.target_google_search = True
            c.network_settings.target_search_network = s["search_partners"]
            c.network_settings.target_content_network = False
            c.network_settings.target_partner_search_network = False
            # Presence only: people in or regularly in the area, not "interested in" it.
            c.geo_target_type_setting.positive_geo_target_type = enums.PositiveGeoTargetTypeEnum.PRESENCE
            c.contains_eu_political_advertising = (
                enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
            strat = s["bidding"]["strategy"]
            if strat in ("maximize_conversions", "target_cpa"):
                client.copy_from(c.maximize_conversions, client.get_type("MaximizeConversions"))
                if s["bidding"].get("target_cpa"):
                    c.maximize_conversions.target_cpa_micros = to_micros(float(s["bidding"]["target_cpa"]))
            elif strat == "maximize_clicks":
                client.copy_from(c.target_spend, client.get_type("TargetSpend"))
            else:
                client.copy_from(c.manual_cpc, client.get_type("ManualCpc"))

            for geo in s["locations"]:
                cc = new_op().campaign_criterion_operation.create
                cc.campaign = campaign_rn
                cc.location.geo_target_constant = f"geoTargetConstants/{geo}"
            if s["proximity"]:
                p = s["proximity"]
                cc = new_op().campaign_criterion_operation.create
                cc.campaign = campaign_rn
                cc.proximity.geo_point.latitude_in_micro_degrees = int(float(p["lat"]) * 1_000_000)
                cc.proximity.geo_point.longitude_in_micro_degrees = int(float(p["lng"]) * 1_000_000)
                cc.proximity.radius = float(p["radius_miles"])
                cc.proximity.radius_units = enums.ProximityRadiusUnitsEnum.MILES
            for lang in s["languages"]:
                cc = new_op().campaign_criterion_operation.create
                cc.campaign = campaign_rn
                cc.language.language_constant = f"languageConstants/{lang}"
            neg_keyword_ops(campaign_rn, s["negative_keywords"])

            for g in s["ad_groups"]:
                ag_rn = svc.ad_group_path(cid, temp_id())
                ag = new_op().ad_group_operation.create
                ag.resource_name = ag_rn
                ag.name = g["name"]
                ag.campaign = campaign_rn
                ag.type_ = enums.AdGroupTypeEnum.SEARCH_STANDARD
                ag.status = enums.AdGroupStatusEnum.ENABLED  # campaign is PAUSED; one switch activates
                if g.get("cpc_bid"):
                    ag.cpc_bid_micros = to_micros(float(g["cpc_bid"]))
                for k in g["keywords"]:
                    kc = new_op().ad_group_criterion_operation.create
                    kc.ad_group = ag_rn
                    kc.status = enums.AdGroupCriterionStatusEnum.ENABLED
                    kc.keyword.text = k["text"]
                    kc.keyword.match_type = enums.KeywordMatchTypeEnum[k["match_type"]]
                if g.get("rsa"):
                    r = g["rsa"]
                    aga = new_op().ad_group_ad_operation.create
                    aga.ad_group = ag_rn
                    aga.status = enums.AdGroupAdStatusEnum.ENABLED
                    aga.ad.final_urls.append(r["final_url"])
                    for h in r["headlines"]:
                        asset = client.get_type("AdTextAsset")
                        asset.text = h
                        aga.ad.responsive_search_ad.headlines.append(asset)
                    for d in r["descriptions"]:
                        asset = client.get_type("AdTextAsset")
                        asset.text = d
                        aga.ad.responsive_search_ad.descriptions.append(asset)
                    if r["path1"]:
                        aga.ad.responsive_search_ad.path1 = r["path1"]
                    if r["path2"]:
                        aga.ad.responsive_search_ad.path2 = r["path2"]
    return svc, ops


_RESULT_FIELDS = ("campaign_budget_result", "campaign_result", "ad_group_result",
                  "ad_group_criterion_result", "ad_group_ad_result", "campaign_criterion_result")


def apply(plan: Dict, execute: bool = False, ticket_id: Optional[str] = None, client=None) -> Dict:
    """Validate (default) or execute a plan. Returns a report dict."""
    profile, cid, specs = check_plan(plan)
    if execute:
        verify_ticket(ticket_id, profile.slug, cid, specs)
    if client is None:
        try:
            from google.ads.googleads.client import GoogleAdsClient
        except ImportError as exc:
            raise PlanError("google-ads is not installed: pip install google-ads") from exc
        client = GoogleAdsClient.load_from_env()
    svc, ops = _to_mutate_operations(client, cid, specs)
    request = client.get_type("MutateGoogleAdsRequest")
    request.customer_id = cid
    request.mutate_operations.extend(ops)
    request.validate_only = not execute
    request.partial_failure = False
    response = svc.mutate(request=request)
    created = []
    for r in getattr(response, "mutate_operation_responses", []) or []:
        for f in _RESULT_FIELDS:
            rn = getattr(getattr(r, f, None), "resource_name", "")
            if rn:
                created.append(rn)
    if execute and ticket_id:
        tickets.consume(ticket_id)
    return {"client": profile.slug, "customer_id": cid, "validate_only": not execute,
            "operations": len(ops), "action": plan_action(specs), "resources": created}

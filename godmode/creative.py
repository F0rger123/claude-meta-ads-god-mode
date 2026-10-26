"""Graphic ad renderer: brief + client brand -> static ad images.

Local, free and deterministic. No AI image service is called. Templates are
SVG, filled with the client's brand colors, font, logo and supplied photos,
then rendered to PNG with a local headless Edge/Chrome when one is found
(otherwise SVG only). Output stays in ADS_GODMODE_HOME/creatives/<client>/ for
review. Nothing is uploaded: getting an image into an ad goes through the
normal paused-first flow (ads_create_creative / ads_create_ad) with approval.

Brief:
    {"client": "example-remodeling", "concept": "Free design consult",
     "hypothesis": "Offer-first static beats lifestyle photo for cold audiences",
     "formats": ["1x1", "4x5", "9x16", "1.91x1"],
     "variants": [
       {"id": "A", "template": "offer-card", "headline": "Your new kitchen, planned free",
        "subhead": "In-home design consult across York County", "badge": "FREE",
        "cta": "Book my consult"},
       {"id": "B", "template": "photo-overlay", "headline": "...", "cta": "...", "image": "kitchen.jpg"},
       {"id": "C", "template": "quote", "headline": "They finished on time.", "subhead": "- Sarah, Dover PA"},
       {"id": "D", "template": "split", "headline": "Same kitchen. 6 weeks.", "image": "before.jpg",
        "image2": "after.jpg", "cta": "See more projects"}]}
"""

import base64
import html
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from . import paths, profiles

FORMATS = {"1x1": (1080, 1080), "4x5": (1080, 1350), "9x16": (1080, 1920), "1.91x1": (1200, 628)}
TEMPLATES = ("offer-card", "photo-overlay", "quote", "split")
DEFAULT_BRAND = {"colors": {"primary": "#1f2937", "secondary": "#f3f4f6", "accent": "#f59e0b"},
                 "font_family": "Inter, 'Segoe UI', Helvetica, Arial, sans-serif", "logo": ""}


class CreativeError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def _hex(c: str) -> tuple:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lum(c: str) -> float:
    def ch(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (_hex(c))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ink(bg: str, preferred: Optional[str] = None) -> str:
    """Readable text color on bg: the brand text color if it passes 4.5:1, else black/white."""
    if preferred and contrast(preferred, bg) >= 4.5:
        return preferred
    return "#111827" if contrast("#111827", bg) >= contrast("#ffffff", bg) else "#ffffff"


def wrap(text: str, width_px: float, size: float, max_lines: int) -> List[str]:
    """Greedy wrap by estimated glyph width (0.55em average)."""
    per_line = max(4, int(width_px / (size * 0.55)))
    words, lines, cur = (text or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= per_line:
            cur = f"{cur} {w}".strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;:") + "..."
    return lines


def fit(text: str, width_px: float, start: int, minimum: int, max_lines: int):
    """Largest font size (step 4) whose wrap fits in max_lines without truncation."""
    size = start
    while size > minimum:
        if len(wrap(text, width_px, size, 99)) <= max_lines:
            break
        size -= 4
    return size, wrap(text, width_px, size, max_lines)


def fit_box(text: str, width_px: float, height_px: float, start: int, minimum: int, max_lines: int, lh: float = 1.15):
    """Largest size whose wrapped text fits both the width and a height budget."""
    size = start
    while size > minimum:
        lines = wrap(text, width_px, size, 99)
        if len(lines) <= max_lines and size + size * lh * (len(lines) - 1) <= height_px:
            break
        size -= 2
    return size, wrap(text, width_px, size, max_lines)


def _block_h(size: int, n: int, lh: float = 1.15) -> float:
    return size + size * lh * (n - 1)


def _text(lines, x, y, size, color, font, weight=700, anchor="start", lh=1.15):
    esc = html.escape
    spans = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else round(size * lh)}">{esc(l)}</tspan>'
                    for i, l in enumerate(lines))
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{esc(font)}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{spans}</text>')


def _data_uri(path: str) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        raise CreativeError(f"image not found: {path}")
    if p.stat().st_size > 8 * 1024 * 1024:
        raise CreativeError(f"image over 8 MB: {path}")
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    if mime not in ("image/jpeg", "image/png", "image/webp"):
        raise CreativeError(f"unsupported image type {mime}: {path}")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def _button(label, cx, y, size, bg, font):
    w = max(220, int(len(label) * size * 0.6) + size * 2)
    h = int(size * 2.3)
    x = cx - w / 2
    fg = ink(bg)
    return (f'<rect x="{x:.0f}" y="{y}" width="{w}" height="{h}" rx="{h / 2:.0f}" fill="{bg}"/>'
            + _text([label], cx, y + h / 2 + size * 0.36, size, fg, font, 700, "middle"))


# ---------------------------------------------------------------- templates

def _layout(fmt: str):
    w, h = FORMATS[fmt]
    pad = int(w * 0.08)
    top, bottom = pad, h - pad
    if fmt == "9x16":  # keep clear of Stories/Reels UI: top ~14%, bottom ~20%
        top, bottom = int(h * 0.14), int(h * 0.80)
    return w, h, pad, top, bottom


def render_svg(variant: Dict, fmt: str, brand: Dict, business: str) -> str:
    w, h, pad, top, bottom = _layout(fmt)
    colors = {**DEFAULT_BRAND["colors"], **(brand.get("colors") or {})}
    font = brand.get("font_family") or DEFAULT_BRAND["font_family"]
    prim, sec, acc = colors["primary"], colors["secondary"], colors["accent"]
    t = variant.get("template", "offer-card")
    inner = w - 2 * pad
    wide = fmt == "1.91x1"
    head_start = int(w * (0.07 if wide else 0.095))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    logo = brand.get("logo")
    footer = (f'<image href="{_data_uri(logo)}" x="{pad}" y="{bottom - 70}" height="70" width="{inner / 2:.0f}" '
              f'preserveAspectRatio="xMinYMid meet"/>' if logo else None)

    tall = fmt in ("4x5", "9x16")
    foot_size = int(w * (0.018 if wide else 0.024))
    content_bottom = bottom - foot_size * (3.2 if wide else 2.2)  # leave room for the footer line

    if t == "offer-card":
        fg = ink(prim, colors.get("text"))
        parts.append(f'<rect width="{w}" height="{h}" fill="{prim}"/>')
        parts.append(f'<circle cx="{w * 0.92:.0f}" cy="{top + 40}" r="{w * 0.28:.0f}" fill="{acc}" opacity="0.18"/>')
        col = inner * (0.58 if wide else 1)
        cs = int(w * (0.022 if wide else 0.034))
        btn_h = int(cs * 2.3) if variant.get("cta") and not wide else 0
        bs = int(w * (0.022 if wide else 0.03))
        badge_h = (int(bs * 2) + int(bs * 1.4)) if variant.get("badge") else 0
        avail = content_bottom - top - badge_h - (btn_h + cs * 2 if btn_h else 0)
        start = int(w * (0.06 if wide else 0.13 if fmt == "9x16" else 0.1))
        size, lines = fit_box(variant["headline"], col, avail * (0.72 if variant.get("subhead") else 0.95),
                              start, 30, 4)
        ss = max(22, int(size * 0.42))
        sl = wrap(variant.get("subhead", ""), col, ss, 3) if variant.get("subhead") else []
        block = badge_h + _block_h(size, len(lines)) + (size * 0.7 + _block_h(ss, len(sl)) if sl else 0) \
            + (cs * 2 + btn_h if btn_h else 0)
        y = top + max(0, (content_bottom - top - block) * (0.42 if tall else 0.3))
        if variant.get("badge"):
            bw = int(len(variant["badge"]) * bs * 0.75) + bs * 2
            parts.append(f'<rect x="{pad}" y="{y:.0f}" width="{bw}" height="{int(bs * 2)}" rx="{bs}" fill="{acc}"/>')
            parts.append(_text([variant["badge"].upper()], pad + bw / 2, y + bs * 1.36, bs, ink(acc), font, 800, "middle"))
            y += badge_h
        parts.append(_text(lines, pad, f"{y + size:.0f}", size, fg, font, 800))
        y += _block_h(size, len(lines))
        if sl:
            y += size * 0.7
            parts.append(_text(sl, pad, f"{y + ss:.0f}", ss, fg, font, 500))
            y += _block_h(ss, len(sl))
        if variant.get("cta"):
            if wide:
                bw_ = max(220, int(len(variant["cta"]) * cs * 0.6) + cs * 2)
                parts.append(_button(variant["cta"], w - pad - bw_ / 2, int(h / 2 - cs * 1.15), cs, acc, font))
            else:
                bw_ = max(220, int(len(variant["cta"]) * cs * 0.6) + cs * 2)
                parts.append(_button(variant["cta"], pad + bw_ / 2, int(y + cs * 2), cs, acc, font))
        parts.append(footer or _text([business], pad, bottom, foot_size, fg, font, 600))

    elif t == "photo-overlay":
        if not variant.get("image"):
            raise CreativeError(f"variant {variant.get('id')}: photo-overlay needs 'image'")
        parts.append(f'<image href="{_data_uri(variant["image"])}" x="0" y="0" width="{w}" height="{h}" '
                     f'preserveAspectRatio="xMidYMid slice"/>')
        parts.append(f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0.35" stop-color="#000" stop-opacity="0"/>'
                     f'<stop offset="1" stop-color="#000" stop-opacity="0.82"/></linearGradient></defs>'
                     f'<rect width="{w}" height="{h}" fill="url(#g)"/>')
        cs = int(w * (0.024 if wide else 0.032))
        size, lines = fit_box(variant["headline"], inner * (0.7 if wide else 1), (bottom - top) * 0.4,
                              int(w * (0.06 if wide else 0.11 if fmt == "9x16" else 0.085)), 30, 3)
        btn_h = int(cs * 2.3) if variant.get("cta") else 0
        block = size + int(size * 1.15) * (len(lines) - 1)
        y0 = bottom - btn_h - int(size * 0.8) - block
        parts.append(_text(lines, pad, y0 + size, size, "#ffffff", font, 800))
        if variant.get("cta"):
            parts.append(_button(variant["cta"], pad + 150 if wide else w / 2, bottom - btn_h, cs, acc, font))
        if footer:
            parts.append(footer.replace(f'y="{bottom - 70}"', f'y="{top}"'))

    elif t == "quote":
        fg = ink(sec, colors.get("text"))
        parts.append(f'<rect width="{w}" height="{h}" fill="{sec}"/>')
        qm = int(min(w, h) * (0.22 if not wide else 0.3))
        start = int(w * (0.05 if wide else 0.1 if fmt == "9x16" else 0.075))
        avail = content_bottom - top - qm * 0.6
        size, lines = fit_box(variant["headline"], inner, avail * 0.7, start, 28, 5)
        star_s = int(size * 0.6)
        au_s = max(22, int(size * 0.45))
        block = qm * 0.6 + _block_h(size, len(lines)) + size * 0.8 + star_s + (au_s * 1.6 if variant.get("subhead") else 0)
        y = top + max(0, (content_bottom - top - block) * (0.42 if tall else 0.3))
        parts.append(_text(["\u201c"], pad - qm * 0.04, f"{y + qm * 0.78:.0f}", qm, acc, "Georgia, serif", 700))
        y += qm * 0.6
        parts.append(_text(lines, pad, f"{y + size:.0f}", size, fg, font, 700))
        y += _block_h(size, len(lines)) + size * 0.8
        parts.append(_text(["\u2605" * int(variant.get("stars", 5))], pad, f"{y + star_s:.0f}", star_s, acc, font, 700))
        y += star_s
        if variant.get("subhead"):
            parts.append(_text([variant["subhead"]], pad, f"{y + au_s * 1.5:.0f}", au_s, fg, font, 500))
        parts.append(footer or _text([business], pad, bottom, foot_size, fg, font, 600))

    elif t == "split":
        if not (variant.get("image") and variant.get("image2")):
            raise CreativeError(f"variant {variant.get('id')}: split needs 'image' and 'image2'")
        band = int(h * (0.2 if not wide else 0.24))
        parts.append(f'<rect width="{w}" height="{h}" fill="{prim}"/>')
        ih = h - band
        for i, (img, label) in enumerate(((variant["image"], variant.get("label1", "BEFORE")),
                                          (variant["image2"], variant.get("label2", "AFTER")))):
            x = i * w / 2
            parts.append(f'<svg x="{x:.0f}" y="{band}" width="{w / 2:.0f}" height="{ih}"><image href="{_data_uri(img)}" '
                         f'width="{w / 2:.0f}" height="{ih}" preserveAspectRatio="xMidYMid slice"/></svg>')
            ls = int(w * 0.026)
            parts.append(f'<rect x="{x + 24:.0f}" y="{band + 24}" width="{int(len(label) * ls * 0.8 + ls * 1.6)}" height="{int(ls * 1.9)}" rx="6" fill="#000" opacity="0.6"/>')
            parts.append(_text([label], x + 24 + ls * 0.8, band + 24 + ls * 1.32, ls, "#fff", font, 800))
        parts.append(f'<rect x="{w / 2 - 3:.0f}" y="{band}" width="6" height="{ih}" fill="{acc}"/>')
        fg = ink(prim, colors.get("text"))
        size, lines = fit_box(variant["headline"], inner, band * 0.72, int(w * (0.045 if wide else 0.06)), 22, 2)
        parts.append(_text(lines, w / 2, band / 2 + size * 0.35 - (size * 0.58 * (len(lines) - 1)), size, fg, font, 800, "middle"))
        if variant.get("cta"):
            cs = int(w * 0.028)
            parts.append(_button(variant["cta"], w / 2, h - int(cs * 2.3) - int(h * (0.22 if fmt == "9x16" else 0.04)), cs, acc, font))
    else:
        raise CreativeError(f"unknown template {t!r}; one of {TEMPLATES}")
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- checks

def check_variant(variant: Dict, profile: profiles.Profile) -> Dict:
    """Errors block rendering; warnings are reported."""
    errors, warnings = [], []
    if not variant.get("headline"):
        errors.append("headline is required")
    if variant.get("template", "offer-card") not in TEMPLATES:
        errors.append(f"template must be one of {TEMPLATES}")
    text = " ".join(str(variant.get(k, "")) for k in ("headline", "subhead", "badge", "cta")).lower()
    for claim in profile.data.get("business", {}).get("prohibited_claims", []):
        core = re.sub(r"\s*\(.*?\)", "", claim).lower().strip()
        if core and core in text:
            errors.append(f"uses a prohibited claim: {claim!r}")
    if len(variant.get("headline", "")) > 60:
        warnings.append("headline over 60 characters - consider shortening for small placements")
    words = len(text.split())
    if words > 30:
        warnings.append(f"{words} words of on-image text - text-heavy images tend to deliver less efficiently (HEURISTIC)")
    if not variant.get("cta"):
        warnings.append("no CTA on the image (the ad's CTA button still applies)")
    return {"errors": errors, "warnings": warnings}


# ---------------------------------------------------------------- PNG + output

def find_browser() -> Optional[str]:
    env = os.environ.get("ADS_GODMODE_BROWSER")
    if env and Path(env).exists():
        return env
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def svg_to_png(svg_path: Path, png_path: Path, size, browser: str) -> bool:
    """Screenshot the SVG with a headless browser. Uses a short temp dir (Windows path limits)."""
    w, h = size
    with tempfile.TemporaryDirectory(prefix="gm") as td:
        page = Path(td) / "a.html"
        shutil.copy(svg_path, Path(td) / "a.svg")
        page.write_text(f'<html><body style="margin:0"><img src="a.svg" width="{w}" height="{h}"></body></html>',
                        encoding="utf-8")
        out = Path(td) / "a.png"
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
               f"--window-size={w},{h}", f"--screenshot={out}", page.as_uri()]
        try:
            subprocess.run(cmd, capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            return False
        if out.exists() and out.stat().st_size > 0:
            shutil.copy(out, png_path)
            return True
    return False


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "concept"


def render_brief(brief: Dict, png: bool = True, out_dir: Optional[str] = None, today: Optional[date] = None) -> Dict:
    profile = profiles.load(brief.get("client", ""))
    brand = {**DEFAULT_BRAND, **(profile.data.get("brand") or {})}
    brand["colors"] = {**DEFAULT_BRAND["colors"], **((profile.data.get("brand") or {}).get("colors") or {})}
    formats = brief.get("formats") or ["1x1", "4x5", "9x16"]
    bad = [f for f in formats if f not in FORMATS]
    if bad:
        raise CreativeError(f"unknown formats {bad}; use {list(FORMATS)}")
    variants = brief.get("variants") or []
    if not variants:
        raise CreativeError("brief has no variants")
    day = (today or date.today()).isoformat()
    out = Path(out_dir) if out_dir else paths.home() / "creatives" / profile.slug / f"{day}-{_slug(brief.get('concept', 'concept'))}"
    out.mkdir(parents=True, exist_ok=True)
    browser = find_browser() if png else None
    results = []
    for v in variants:
        chk = check_variant(v, profile)
        entry = {"id": v.get("id"), "template": v.get("template", "offer-card"), **chk, "files": []}
        if not chk["errors"]:
            for f in formats:
                svg = render_svg(v, f, brand, profile.name)
                sp = out / f"{_slug(str(v.get('id', 'v')))}_{f.replace('.', '_')}.svg"
                sp.write_text(svg, encoding="utf-8")
                item = {"format": f, "size": FORMATS[f], "svg": str(sp)}
                if browser:
                    pp = sp.with_suffix(".png")
                    if svg_to_png(sp, pp, FORMATS[f], browser):
                        item["png"] = str(pp)
                entry["files"].append(item)
        results.append(entry)
    manifest = {"client": profile.slug, "concept": brief.get("concept"), "hypothesis": brief.get("hypothesis"),
                "generated": day, "png_renderer": browser or None, "variants": results,
                "next": "Review the images. To use one, upload it and create the ad PAUSED; activation needs approval."}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out / "index.html").write_text(contact_sheet(manifest), encoding="utf-8")
    manifest["dir"] = str(out)
    return manifest


def contact_sheet(m: Dict) -> str:
    e = html.escape
    cards = []
    for v in m["variants"]:
        imgs = "".join(f'<figure><img src="{e(Path(f.get("png") or f["svg"]).name)}" alt="{e(f["format"])}">'
                       f'<figcaption>{e(f["format"])} · {f["size"][0]}x{f["size"][1]}</figcaption></figure>'
                       for f in v["files"])
        notes = "".join(f"<li class=err>{e(x)}</li>" for x in v["errors"]) + "".join(f"<li>{e(x)}</li>" for x in v["warnings"])
        cards.append(f'<section><h2>Variant {e(str(v["id"]))} <small>{e(v["template"])}</small></h2><ul>{notes}</ul><div class=row>{imgs}</div></section>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(m.get('concept') or 'Creatives')}</title><style>
:root{{--bg:#f5f7fb;--fg:#111827;--muted:#6b7280}}@media (prefers-color-scheme:dark){{:root{{--bg:#0b1020;--fg:#e6ecff;--muted:#9fb0d9}}}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font-family:'Segoe UI',Inter,Arial,sans-serif}}
.row{{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}}figure{{margin:0}}img{{max-width:280px;max-height:420px;border-radius:8px;box-shadow:0 2px 12px #0003}}
figcaption,small,p{{color:var(--muted);font-size:13px}}li.err{{color:#dc2626}}</style></head><body>
<h1>{e(m.get('concept') or '')}</h1><p>{e(m['client'])} · {e(m['generated'])} · hypothesis: {e(m.get('hypothesis') or '-')}</p>
{''.join(cards)}<p>{e(m['next'])}</p></body></html>"""

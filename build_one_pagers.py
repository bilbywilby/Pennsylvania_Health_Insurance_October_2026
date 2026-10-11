#!/usr/bin/env python3
"""
build_one_pagers.py - builds nine one-page Pennsylvania rating-area snapshots (plan year 2027).

Reads  : data/pa_ra_dataset.json   (figures transcribed from PID / Pennie primary pages, accessed 2026-10-09)
Writes : one_pagers/PA_RA<n>_2027_Market_Snapshot_Oct2026.pdf   (exactly one page each, verified after build)
         data/derived_area_metrics.json                     (every derived number printed on the pages)

Descriptive cross-sectional synthesis only: no pooling, no heterogeneity statistics.
Every derived figure is recomputed from the dataset on each run. The run aborts (non-zero exit) if
  - the 67-county map is not a clean partition,
  - any carrier footprint names a county that is not in the map,
  - the statewide weights fail to reproduce PID's published averages,
  - carrier-by-area lists disagree with the September 8 area reports or with PID's own stated rating areas,
  - any page needs more than one page or smaller type than the readability floor.

Usage:  python3 build_one_pagers.py            # validate + build
        python3 build_one_pagers.py --check    # validate + derive only (no PDFs)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "pa_ra_dataset.json"
DERIVED = ROOT / "data" / "derived_area_metrics.json"
OUT = ROOT / "one_pagers"

MIN_FONT = 6.2   # readability floor for body text (points)
ALLOWED_EXTRA = set("\u00b7\u2013\u2014\u2022\u00d7\u2020\u2021")  # characters present in WinAnsi


# --------------------------------------------------------------------------- data + validation
def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def wavg(items, vkey, wkey):
    den = sum(i[wkey] for i in items)
    return sum(i[vkey] * i[wkey] for i in items) / den if den else None


def prepare(ds):
    cmap = {}
    for a, cs in ds["areas"].items():
        for c in cs:
            if c in cmap:
                raise SystemExit(f"FAIL duplicate county mapping: {c}")
            cmap[c] = a
    if len(cmap) != 67 or set(ds["areas"]) != {str(i) for i in range(1, 10)}:
        raise SystemExit(f"FAIL county map: {len(cmap)} counties, areas {sorted(ds['areas'])}")
    for e in ds["individual"]:
        e["cset"] = set(e["counties"])
    for e in ds["small_group"]:
        e["cset"] = set(cmap) if e["counties"] == "ALL" else set(e["counties"])
    for e in ds["individual"] + ds["small_group"]:
        bad = e["cset"] - set(cmap)
        if bad:
            raise SystemExit(f"FAIL {e['id']} names unknown counties: {sorted(bad)}")
    bad = set(ds["terminations_oe2026"]["top20_pct"]) - set(cmap)
    if bad or len(ds["terminations_oe2026"]["top20_pct"]) != 20:
        raise SystemExit(f"FAIL termination list: {sorted(bad)}")
    return cmap


def validate(ds, cmap):
    log = []
    st = ds["statewide"]
    ind, sg = ds["individual"], ds["small_group"]

    def check(label, got, want, tol):
        ok = abs(got - want) <= tol
        log.append(f"[{'OK' if ok else 'FAIL'}] {label}: computed {got:.3f} vs published {want} (tol {tol})")
        if not ok:
            raise SystemExit("\n".join(log))

    check("individual shares 2026 sum", sum(e["share26"] for e in ind), 100.0, 0.1)
    check("small-group shares 2026 sum", sum(e["share26"] for e in sg), 100.0, 0.1)
    check("PID individual 2027 avg approved", wavg(ind, "app27", "share26"), st["pid_individual_2027_avg_approved"], 0.05)
    check("PID small-group 2027 avg approved", wavg(sg, "app27", "share26"), st["pid_small_group_2027_avg_approved"], 0.05)
    check("reported individual 2027 avg requested", wavg(ind, "req27", "share26"), st["reported_individual_2027_avg_requested"], 0.1)
    check("reported small-group 2027 avg requested", wavg(sg, "req27", "share26"), st["reported_small_group_2027_avg_requested"], 0.1)
    h = ds["individual_2026_only"]
    rows26 = [{"app26": e["app26"], "share25": e["share25"]} for e in ind if "app26" in e]
    rows26.append({"app26": h["app26"], "share25": h["share25"]})
    check("individual 2025 shares sum", sum(r["share25"] for r in rows26), 100.0, 0.1)
    check("PID individual 2026 avg approved", wavg(rows26, "app26", "share25"), st["pid_individual_2026_avg_approved"], 0.05)

    # carrier-by-area lists: derived from county footprints vs September 8 reports
    legacy = ds["validation"]["legacy_area_entities_sep8_reports"]
    for a in sorted(ds["areas"]):
        acs = set(ds["areas"][a])
        derived = sorted(e["id"] for e in ind if e["cset"] & acs)
        want = sorted(legacy[a])
        ok = derived == want
        log.append(f"[{'OK' if ok else 'FAIL'}] area {a} filer list matches Sep 8 report ({len(derived)} filers)")
        if not ok:
            raise SystemExit("\n".join(log) + f"\n derived={derived}\n report={want}")

    # PID's own stated rating areas for carriers (independent check on the county-to-area map)
    for key, pool in (("pid_stated_areas_individual_2027_request_release", ind),
                      ("pid_stated_areas_small_group_2027_request_release", sg)):
        for eid, want in ds["validation"][key].items():
            e = next(x for x in pool if x["id"] == eid)
            got = sorted({int(cmap[c]) for c in e["cset"]})
            ok = got == sorted(want)
            log.append(f"[{'OK' if ok else 'FAIL'}] PID-stated rating areas for {eid} ({'ind' if pool is ind else 'sg'}): {got}")
            if not ok:
                raise SystemExit("\n".join(log))
    return log


# --------------------------------------------------------------------------- derived metrics
def derive(ds, cmap):
    st = ds["statewide"]
    ind, sg = ds["individual"], ds["small_group"]
    term = ds["terminations_oe2026"]["top20_pct"]
    out = {}
    for a, cs in sorted(ds["areas"].items(), key=lambda kv: int(kv[0])):
        acs = set(cs)
        ents = []
        for e in ind:
            ov = e["cset"] & acs
            if ov:
                r = dict(e)
                r["cty"] = len(ov)
                if "app26" in e:
                    r["cmp2"] = ((1 + e["app26"] / 100) * (1 + e["app27"] / 100) - 1) * 100
                r["delta"] = e["app27"] - e["req27"] if e["req27"] else None
                ents.append(r)
        for r in ents:
            r.pop("cset", None)
        priced = [r for r in ents if r["share26"] > 0]
        mix = wavg(priced, "app27", "share26")
        per_cty = {}
        for c in cs:
            tot = [e for e in ind if c in e["cset"]]
            per_cty[c] = {"listed": len(tot), "on_pennie": sum(1 for e in tot if e["on_pennie"])}
        sgents = []
        for e in sg:
            ov = e["cset"] & acs
            if ov:
                r = dict(e)
                r.pop("cset", None)
                sgents.append(r)
        t = {c: term[c] for c in cs if c in term}
        out[a] = {
            "counties": cs,
            "n_counties": len(cs),
            "individual_filers": ents,
            "n_listed": len(ents),
            "n_on_pennie": sum(1 for r in ents if r["on_pennie"]),
            "mix_approved": mix,
            "mix_requested": wavg(priced, "req27", "share26"),
            "per_county": per_cty,
            "min_on_pennie": min(v["on_pennie"] for v in per_cty.values()),
            "max_on_pennie": max(v["on_pennie"] for v in per_cty.values()),
            "thin_counties": [c for c, v in per_cty.items() if v["on_pennie"] <= 2],
            "sg_filers": sgents,
            "sg_mix_approved": wavg(sgents, "app27", "share26"),
            "terminations_top20": t,
        }
    order = sorted(out, key=lambda a: -out[a]["mix_approved"])
    for rank, a in enumerate(order, 1):
        out[a]["rank_mix_1_is_highest"] = rank
    return out


# --------------------------------------------------------------------------- rendering
def render(ds, derived, only_check=False):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from pypdf import PdfReader

    NAVY, BLUE, RED = colors.HexColor("#1F3A5F"), colors.HexColor("#6FA8DC"), colors.HexColor("#E08C84")
    GRAY, LIGHT, INK = colors.HexColor("#6B7785"), colors.HexColor("#F2F5F9"), colors.HexColor("#1B1F24")
    GREEN, DRED = colors.HexColor("#2F7D4F"), colors.HexColor("#B5382F")

    st = ds["statewide"]
    S = ds["sources"]
    STATE_IND, STATE_SG = st["pid_individual_2027_avg_approved"], st["pid_small_group_2027_avg_approved"]
    W, PAGE_H = 552.0, 792.0
    TOP, BOT = 30.0, 30.0
    AVAIL = PAGE_H - TOP - BOT

    def sp(x, d=2):
        return f"{x:+.{d}f}%"

    def chk(s):
        for ch in s:
            if ord(ch) > 127 and ch not in ALLOWED_EXTRA:
                raise SystemExit(f"FAIL non-WinAnsi character {ch!r} in: {s[:60]}")
        return s

    def P(text, style):
        return Paragraph(chk(text), style)

    def styles(fs):
        base = dict(fontName="Helvetica", fontSize=fs, leading=fs * 1.22, textColor=INK)
        return {
            "title": ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=fs + 7.5, leading=(fs + 7.5) * 1.1, textColor=NAVY),
            "sub": ParagraphStyle("s", **{**base, "fontSize": fs, "textColor": GRAY}),
            "body": ParagraphStyle("b", **base),
            "small": ParagraphStyle("sm", **{**base, "fontSize": fs - 0.9, "leading": (fs - 0.9) * 1.2}),
            "bul": ParagraphStyle("bu", **{**base, "leftIndent": 7, "firstLineIndent": -7, "spaceAfter": 1.6}),
            "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=fs + 1, leading=(fs + 1) * 1.2, textColor=NAVY),
            "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=fs - 0.8, leading=(fs - 0.8) * 1.15, textColor=colors.white, alignment=TA_CENTER),
            "td": ParagraphStyle("td", **{**base, "fontSize": fs - 0.2, "leading": (fs - 0.2) * 1.15}),
            "tdc": ParagraphStyle("tdc", **{**base, "fontSize": fs - 0.2, "leading": (fs - 0.2) * 1.15, "alignment": TA_CENTER}),
            "tdr": ParagraphStyle("tdr", **{**base, "fontSize": fs - 0.2, "leading": (fs - 0.2) * 1.15, "alignment": TA_RIGHT}),
            "kv": ParagraphStyle("kv", fontName="Helvetica-Bold", fontSize=fs + 3.2, leading=(fs + 3.2) * 1.1, textColor=NAVY, alignment=TA_CENTER),
            "kc": ParagraphStyle("kc", fontName="Helvetica", fontSize=fs - 1.2, leading=(fs - 1.2) * 1.15, textColor=GRAY, alignment=TA_CENTER),
            "ref": ParagraphStyle("r", fontName="Helvetica", fontSize=max(fs - 1.7, 5.0), leading=max(fs - 1.7, 5.0) * 1.18,
                                  textColor=INK, leftIndent=7, firstLineIndent=-7, spaceAfter=0.8),
        }

    def bar_cell(app, req, bar_w, h, fs, vmax=44.0):
        d = Drawing(bar_w + 34, h)
        if app == 0 and req == 0:
            d.add(String(2, h * 0.28, "new plan, 0.00%", fontName="Helvetica-Oblique", fontSize=fs - 0.4, fillColor=GRAY))
            return d
        xs = STATE_IND / vmax * bar_w
        d.add(Line(xs, 0, xs, h, strokeColor=GRAY, strokeWidth=0.5, strokeDashArray=[1.4, 1.4]))
        d.add(Rect(0, h * 0.2, max(app, 0) / vmax * bar_w, h * 0.6, fillColor=(RED if app > STATE_IND else BLUE), strokeColor=None))
        xr = req / vmax * bar_w
        d.add(Line(xr, h * 0.05, xr, h * 0.95, strokeColor=INK, strokeWidth=1.1))
        d.add(String(bar_w + 4, h * 0.27, sp(app), fontName="Helvetica-Bold", fontSize=fs - 0.2, fillColor=INK))
        return d

    def area_chart(a, w, h, fs):
        d = Drawing(w, h)
        label_w, val_w = 20, 34
        bw = w - label_w - val_w
        vmax = 22.0
        rowh = (h - 12) / 9.0
        for i in range(1, 10):
            y = h - 12 - i * rowh
            v = derived[str(i)]["mix_approved"]
            cur = str(i) == a
            d.add(String(0, y + rowh * 0.22, f"RA{i}", fontName="Helvetica-Bold" if cur else "Helvetica", fontSize=fs - 0.6,
                         fillColor=NAVY if cur else GRAY))
            d.add(Rect(label_w, y + rowh * 0.12, v / vmax * bw, rowh * 0.72, fillColor=NAVY if cur else colors.HexColor("#C5CDD6"), strokeColor=None))
            d.add(String(w, y + rowh * 0.22, sp(v, 1), fontName="Helvetica-Bold" if cur else "Helvetica",
                         fontSize=fs - 0.6, fillColor=INK, textAnchor="end"))
        xs = label_w + STATE_IND / vmax * bw
        d.add(Line(xs, 0, xs, h - 12, strokeColor=DRED, strokeWidth=0.8, strokeDashArray=[2, 1.5]))
        d.add(String(xs - 2, h - 9, f"PID state avg {STATE_IND:.2f}%", fontName="Helvetica", fontSize=fs - 1.2, fillColor=DRED, textAnchor="end"))
        return d

    def cite_ref(keys, fs):
        items = [P(chk(S[k]["apa"] + " " + S[k]["url"]), styles(fs)["ref"]) for k in keys]
        return items

    def story(a, fs):
        m = derived[a]
        sty = styles(fs)
        cs = m["counties"]
        N = m["n_counties"]
        ents = sorted(m["individual_filers"], key=lambda r: (-r["share26"], r["id"]))
        sgm = m["sg_filers"]
        flow = []

        flow.append(P(f"Rating Area {a} - 2027 Market Snapshot", sty["title"]))
        flow.append(P("Cross-sectional synthesis of PID-approved 2027 ACA rates, carrier footprints and Pennie terminations. Version 1.0, October 2026; data as of 2026-10-09.", sty["sub"]))
        flow.append(Spacer(1, 2.5))
        flow.append(P(f"<b>Counties ({N}):</b> {', '.join(cs)} (CMS, 2024).", sty["body"]))
        flow.append(Spacer(1, 4))

        lo = min(ents, key=lambda r: r["app27"] if r["share26"] > 0 else 999)
        hi = max(ents, key=lambda r: r["app27"])
        n_term = len(m["terminations_top20"])
        kp = [
            (f"{m['n_listed']} / {m['n_on_pennie']}", "PID-listed filers / sold on Pennie"),
            (sp(m["mix_approved"], 1), f"carrier-mix approved 2027 (state {sp(STATE_IND)})"),
            (f"{sp(lo['app27'])} to {sp(hi['app27'])}", "approved range across filers"),
            (f"{len(m['thin_counties'])} of {N}", "counties with 2 or fewer on-Pennie filers"),
            (f"{n_term} of {N}", "counties in Pennie OE-2026 top-20 terminations"),
        ]
        kt = Table([[[P(v, sty["kv"]), P(c, sty["kc"])] for v, c in kp]], colWidths=[W / 5.0] * 5)
        kt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("LINEAFTER", (0, 0), (-2, -1), 0.6, colors.white),
                                ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                                ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
        flow.append(kt)
        flow.append(Spacer(1, 5))

        flow.append(P("Individual market: every PID-listed filer serving the area (PID, 2026a, 2026d)", sty["h"]))
        flow.append(Spacer(1, 1.5))
        hdr = ["Filer", "Pennie", "Cty*", "2026 approved", "2027 request", "2027 approved (bar; tick = request; dashed = state avg)", "vs request (pts)", "2026-27 compounded", "2026 share"]
        rows = [[P(x, sty["th"]) for x in hdr]]
        rowh = fs * 1.25 + 3.2
        bar_w = 142 - 36
        for r in ents:
            d = bar_cell(r["app27"], r["req27"], bar_w, rowh - 1.5, fs)
            new = "app26" not in r
            delta = "n/a" if r["delta"] is None else f"{r['delta']:+.2f}"
            colr = "#2F7D4F" if (r["delta"] or 0) < 0 else ("#B5382F" if (r["delta"] or 0) > 0 else "#1B1F24")
            rows.append([
                P(r["short"], sty["td"]),
                P("Yes" if r["on_pennie"] else "<b>No</b>", sty["tdc"]),
                P(f"{r['cty']}/{N}", sty["tdc"]),
                P("new" if new else sp(r["app26"]), sty["tdr"]),
                P("n/a" if new else sp(r["req27"]), sty["tdr"]),
                d,
                P(f"<font color='{colr}'>{delta}</font>", sty["tdr"]),
                P("new" if new else sp(r["cmp2"], 1), sty["tdr"]),
                P("new" if new else f"{r['share26']:.2f}%", sty["tdr"]),
            ])
        # pennie / request columns need shorter widths; bar column widest
        cw = [128, 30, 26, 40, 40, 142, 40, 54, 52]
        assert abs(sum(cw) - W) < 0.5, sum(cw)
        t = Table(rows, colWidths=cw, repeatRows=1)
        ts = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 0.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.8),
              ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
              ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#D5DBE2"))]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                ts.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
        t.setStyle(TableStyle(ts))
        flow.append(t)
        flow.append(Spacer(1, 1.2))
        flow.append(P("*Cty = area counties the filer serves / counties in the area. Request and approved values are PID average rate changes across a filer's plans, before tax credits. "
                      "Compounded = (1 + 2026 approved) x (1 + 2027 approved) - 1. Share = PID-reported statewide market share, prior year.", sty["small"]))
        flow.append(Spacer(1, 5))

        # mid band: cross-area chart + findings
        cap = max(m["per_county"].items(), key=lambda kv: (kv[1]["on_pennie"], kv[0]))
        fewest = [c for c, v in m["per_county"].items() if v["on_pennie"] == m["min_on_pennie"]]
        thin = m["thin_counties"]
        thin_txt = f" ({', '.join(thin)})" if 0 < len(thin) <= 7 else ""
        fewest_txt = ""
        if len(fewest) <= 4:
            fewest_txt = f" Fewest: {', '.join(fewest)} ({m['min_on_pennie']})."
        f1 = (f"<b>Competition.</b> {m['n_listed']} PID-listed filers serve the area ({m['n_on_pennie']} sell on Pennie). On-Pennie filers per county run "
              f"{m['min_on_pennie']} to {m['max_on_pennie']}; {len(thin)} of {N} counties have two or fewer{thin_txt}.{fewest_txt} (PID, 2026b)")
        diff = m["mix_approved"] - STATE_IND
        f2 = (f"<b>Price.</b> Carrier-mix approved increase is {sp(m['mix_approved'], 1)}, {diff:+.1f} pts vs. the {sp(STATE_IND)} statewide average "
              f"(rank {m['rank_mix_1_is_highest']} of 9 areas; 1 = highest). Lowest approved: {lo['short']} {sp(lo['app27'])}; highest: {hi['short']} {sp(hi['app27'])}.")
        req_ents = [r for r in ents if r["req27"]]
        cuts = [r for r in req_ents if r["delta"] < 0]
        ups = [r for r in req_ents if r["delta"] > 0]
        big = min(req_ents, key=lambda r: r["delta"])
        f3 = (f"<b>PID action.</b> PID trimmed {len(cuts)} of {len(req_ents)} requests here (largest cut: {big['short']}, {big['delta']:+.2f} pts)")
        if ups:
            f3 += "; it approved above the request for " + ", ".join(f"{r['short']} ({r['delta']:+.2f})" for r in ups)
        f3 += "."
        top3 = [r for r in ents if "cmp2" in r][:3]
        hi2 = max((r for r in ents if "cmp2" in r), key=lambda r: r["cmp2"])
        f4 = ("<b>Two-year view.</b> Compounded 2026-27 approved increases for the largest filers: "
              + "; ".join(f"{r['short']} {sp(r['cmp2'], 1)}" for r in top3) + f". Highest in area: {hi2['short']} {sp(hi2['cmp2'], 1)}.")
        offp = [r for r in ents if not r["on_pennie"]]
        f5 = None
        if offp:
            names = []
            for r in offp:
                names.append(r["short"] if "app26" not in r else f"{r['short']} ({sp(r['app27'])})")
            f5 = ("<b>Off-Pennie.</b> " + "; ".join(names) + (" is" if len(offp) == 1 else " are")
                  + " not sold on Pennie; premium tax credits apply only to Pennie plans.")
        tt = m["terminations_top20"]
        if tt:
            lst = ", ".join(f"{c} {v}%" for c, v in sorted(tt.items(), key=lambda kv: (-kv[1], kv[0])))
            f6 = (f"<b>Terminations.</b> {len(tt)} of {N} counties are on Pennie's top-20 list of OE-2026 terminations (through 2/1/2026): {lst}. "
                  "Other counties here are at or below the 19% list floor (Pennie, 2026a).")
        else:
            f6 = ("<b>Terminations.</b> No county in this area is on Pennie's top-20 list of OE-2026 terminations (through 2/1/2026); "
                  "all are at or below the 19% list floor (Pennie, 2026a).")
        finds = [P("&bull; " + f, sty["bul"]) for f in [f1, f2, f3, f4, f5, f6] if f]
        left = [P("Carrier-mix approved 2027 increase, all nine areas (proxy; see note)", sty["small"]), area_chart(a, 218, 104, fs)]
        mid = Table([[left, finds]], colWidths=[226, W - 226])
        mid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 6),
                                 ("RIGHTPADDING", (1, 0), (1, 0), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        flow.append(mid)
        flow.append(Spacer(1, 4))

        # small group + county detail
        sgs = sorted(sgm, key=lambda r: -r["share26"])
        sglo = min(sgm, key=lambda r: r["app27"])
        sghi = max(sgm, key=lambda r: r["app27"])
        sg_txt = (f"<b>Small group, 2027 approved (PID, 2026a, 2026c).</b> {len(sgm)} filers serve the area; carrier-mix {sp(m['sg_mix_approved'], 1)} "
                  f"(state {sp(STATE_SG)}); range {sglo['short']} {sp(sglo['app27'])} to {sghi['short']} {sp(sghi['app27'])}. Largest by statewide share: "
                  + "; ".join(f"{r['short']} {sp(r['app27'])} ({r['share26']:.1f}%)" for r in sgs[:3]) + ".")
        cty_txt = ("<b>On-Pennie / listed individual filers by county (PID, 2026b).</b> "
                   + "; ".join(f"{c} {v['on_pennie']}/{v['listed']}" for c, v in m["per_county"].items()) + ".")
        box = Table([[[P(sg_txt, sty["body"])], [P(cty_txt, sty["body"])]]], colWidths=[W / 2.0] * 2)
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                                 ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                                 ("LINEAFTER", (0, 0), (0, 0), 0.6, colors.white)]))
        flow.append(box)
        flow.append(Spacer(1, 4))

        pe = st["pennie_enrollment"]
        oe = st["open_enrollment_2027"]
        ctx = (f"<b>Statewide context.</b> PID approved 2027 averages of {sp(STATE_IND)} (individual; requested {ds['_chk']['ind27req']:+.2f}%, computed from PID, 2026a) and "
               f"{sp(STATE_SG)} (small group) (PID, 2026e). Pennie enrollment: {pe['2025_peak']:,} (2025 peak), {pe['2026-01-31_oe_close']:,} (OE close, 1/31/26), "
               f"{pe['2026-03-24']:,} (3/24/26) (Pennie, 2026b; PHLP, 2026). Open enrollment for 2027: Nov. 1, 2026 to Jan. 15, 2027; enroll by Dec. 15 for Jan. 1 coverage (PHLP, 2026). "
               "Confirm dates at pennie.com or 1-844-844-8040.")
        flow.append(P(ctx, sty["body"]))
        flow.append(Spacer(1, 2.5))

        extra = ""
        if ups:
            extra = (" PID's reasons for approving above the request are not summarized here [UNVERIFIED].")
        notes = ("<b>Evidence tiers.</b> VERIFIED to primary pages accessed 2026-10-09: rates, shares, county footprints (PID); termination rates (Pennie). "
                 "DERIVED here: carrier-mix average, compounding, per-county counts, ranks. <b>Method.</b> Carrier-mix = sum(statewide prior-year share x approved %) / sum(share) over filers serving "
                 "at least one area county. Area enrollment is not published, so this is a proxy; the same weights reproduce PID's statewide averages (individual "
                 f"{ds['_chk']['ind27']:.2f} vs {STATE_IND}; small group {ds['_chk']['sg27']:.2f} vs {STATE_SG}; 2026 individual {ds['_chk']['ind26']:.2f} vs {st['pid_individual_2026_avg_approved']}). "
                 "Area filer lists match both the September 8 area reports and PID's stated rating areas (PID, 2026f). An average rate change is not what each consumer pays. "
                 "Descriptive only: no pooling." + extra)
        flow.append(P(notes, sty["small"]))
        flow.append(Spacer(1, 3))

        keys = ["PID2026a", "PID2026b", "PID2026c", "PID2026d", "PID2026e", "PID2026f", "PENNIE2026a", "PENNIE2026b", "PHLP2026", "CMS2024"]
        refs = cite_ref(keys, fs)
        half = 5
        rt = Table([[refs[:half], refs[half:]]], colWidths=[W / 2.0] * 2)
        rt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 6),
                                ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("LINEABOVE", (0, 0), (-1, 0), 0.5, GRAY)]))
        flow.append(P("References", sty["h"]))
        flow.append(rt)
        return flow

    def height(flow):
        return sum(f.wrap(W, 10_000)[1] for f in flow)

    def draw_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - 12, 612, 12, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 6.5)
        canvas.drawString(30, PAGE_H - 8.6, "EZ_INSURANCE  |  PENNSYLVANIA HEALTH INSURANCE PUBLIC INFORMATION CAMPAIGN")
        canvas.setFillColor(GRAY)
        canvas.setFont("Helvetica", 6)
        canvas.drawString(30, 16, f"Pennsylvania Health Insurance Audit, October 2026 | Rating Area {doc._ra} | v1.0 | Built from data/pa_ra_dataset.json by build_one_pagers.py | Informational only; not legal, medical or financial advice.")
        canvas.restoreState()

    results = []
    OUT.mkdir(exist_ok=True)
    def fit(a):
        fs = 8.2
        while True:
            h = height(story(a, fs))
            if h <= AVAIL - 20 or fs <= MIN_FONT:
                return fs
            fs = round(fs - 0.1, 2)

    UNIFORM = min(fit(a) for a in derived)   # one body size across all nine pages
    while True:
        results, ok = [], True
        for a in sorted(derived, key=int):
            flow = story(a, UNIFORM)
            h = height(flow)
            path = OUT / f"PA_RA{a}_2027_Market_Snapshot_Oct2026.pdf"
            doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=30, rightMargin=30, topMargin=TOP, bottomMargin=BOT,
                                    title=f"Pennsylvania Rating Area {a}: 2027 Market Snapshot", author="Ez_Insurance PA Health Insurance Public Information Campaign",
                                    subject="Descriptive cross-sectional synthesis of PID-approved 2027 ACA rates")
            doc._ra = a
            doc.build(flow, onFirstPage=draw_page, onLaterPages=draw_page)
            pages = len(PdfReader(str(path)).pages)
            if pages != 1:
                ok = False
                break
            results.append((a, UNIFORM, h, pages))
        if ok:
            break
        UNIFORM = round(UNIFORM - 0.1, 2)
        if UNIFORM < MIN_FONT:
            raise SystemExit(f"FAIL: pages do not fit one sheet at the {MIN_FONT}pt floor")
    print(f"[FIT] uniform body font {UNIFORM}pt; all pages verified single-page")
    for a, fs, h, pages in results:
        print(f"[BUILT] PA_RA{a}_2027_Market_Snapshot_Oct2026.pdf: content {h:.0f}/{AVAIL:.0f}pt, pages {pages}")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate and derive only")
    args = ap.parse_args()

    ds = load()
    cmap = prepare(ds)
    log = validate(ds, cmap)
    print("\n".join(log))
    ind, sg = ds["individual"], ds["small_group"]
    h = ds["individual_2026_only"]
    rows26 = [{"app26": e["app26"], "share25": e["share25"]} for e in ind if "app26" in e] + [{"app26": h["app26"], "share25": h["share25"]}]
    ds["_chk"] = {"ind27": wavg(ind, "app27", "share26"), "sg27": wavg(sg, "app27", "share26"), "ind27req": wavg(ind, "req27", "share26"), "ind26": wavg(rows26, "app26", "share25")}
    derived = derive(ds, cmap)
    DERIVED.write_text(json.dumps({"_checks": ds["_chk"], "areas": derived}, indent=1) + "\n", encoding="utf-8")
    print(f"[OK] wrote {DERIVED.relative_to(ROOT)}")
    if not args.check:
        render(ds, derived)
    print("DONE")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code not in (None, 0):
            print(e.code if isinstance(e.code, str) else "", file=sys.stderr)
        raise

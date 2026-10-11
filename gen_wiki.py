#!/usr/bin/env python3
"""Generate wiki Markdown pages from the validated dataset (one-off, run in the build sandbox)."""
import json
from pathlib import Path

BASE = Path("/home/claude/work/pa_ra_onepagers")
OUT = Path("/home/claude/work/wiki")
OUT.mkdir(exist_ok=True)
ds = json.loads((BASE / "data/pa_ra_dataset.json").read_text())
dv = json.loads((BASE / "data/derived_area_metrics.json").read_text())
A, CHK = dv["areas"], dv["_checks"]
ind, sg = ds["individual"], ds["small_group"]
S = ds["statewide"]


def sp(x, d=2):
    return f"{x:+.{d}f}%"


def cmp2(e):
    return ((1 + e["app26"] / 100) * (1 + e["app27"] / 100) - 1) * 100


P = {}

# ---------------------------------------------------------------- Home
P["Home"] = f"""# Pennsylvania Health Insurance Audit: Plan Year 2027

Public reference on Pennsylvania's ACA individual and small-group markets for plan year 2027. Version 1.0, October 10, 2026.

**How to read this wiki:** every figure carries an evidence tier (see [Methodology and Verification](Methodology-and-Verification)). Anything we could not trace to a primary source is marked UNVERIFIED or left out. Known errors in earlier project files are listed in [Corrections and Open Items](Corrections-and-Open-Items).

## At a glance (VERIFIED: PID press release, Sept. 18, 2026)
- Individual market: average approved increase **{sp(15.97)}** (requested {sp(17.14)}).
- Small group: average approved increase **{sp(10.28)}** (requested {sp(11.49)}).
- PID denied **$94.7 million** in premium increases it called unjustified.
- An average is not what each consumer pays. Age, county, income, household size and subsidies change the bill, and some people may see a decrease (PID, 2026e).

## Open enrollment for 2027 (VERIFIED, corroborated)
November 1, 2026 to January 15, 2027. Enroll by **December 15, 2026** for coverage starting January 1, 2027. Confirm at pennie.com or 1-844-844-8040 (PHLP, 2026; PID, 2026e).

## Pages
1. [Statewide Rate Actions](PY2027-Statewide-Rate-Actions): every carrier, requested vs. approved, two-year compounding.
2. [Rating Area Profiles](Rating-Area-Profiles): all nine areas, counties, competition, price, terminations.
3. [Pennie Enrollment and Open Enrollment](Pennie-Enrollment-and-Open-Enrollment)
4. [Consumer Help and Appeals](Consumer-Help-and-Appeals)
5. [Citation Registry](Citation-Registry): what is verified, what failed.
6. [Corrections and Open Items](Corrections-and-Open-Items)
7. [Methodology and Verification](Methodology-and-Verification)
8. [Sources and Reproducibility](Sources-and-Reproducibility)

*Informational only. Not legal, medical or financial advice.*
"""

# ---------------------------------------------------------------- Methodology
P["Methodology-and-Verification"] = f"""# Methodology and Verification

This is a **descriptive cross-sectional synthesis**: counts, percentage changes, ranges and weighted averages. It does not pool studies or estimate heterogeneity.

## Evidence tiers
| Tier | Meaning | Publishable as fact? |
| :--- | :--- | :---: |
| VERIFIED | Read on a primary page (PID, Pennie, CMS) with an access date, or corroborated by two independent sources | Yes |
| DERIVED | Computed here from VERIFIED inputs; method stated | Yes, labeled |
| UNVERIFIED | Plausible but not traced to a primary source | No; bracket or omit |
| NOT FOUND | Searched for, not located as of the date given | Say "not found as of [date]" |

## Inputs
- 2027 requested and approved rates, 2026 market shares, Pennie availability, county footprints: PID's ACA rate-filing pages (PID, 2026a, 2026b, 2026c).
- 2026 approved rates and 2025 shares: PID's archived 2026 filings (PID, 2026d).
- Statewide averages and carrier reasons for above-request approvals: PID press release (PID, 2026e).
- County to rating area: CMS crosswalk (CMS, 2024), cross-checked against the rating areas PID itself names for 12 carrier filings (PID, 2026f).
- County terminations: Pennie's published top-20 list through Feb. 1, 2026 (Pennie, 2026a).

## Derived measures
- **Carrier-mix approved increase** for an area = sum(statewide prior-year market share x approved %) / sum(share), over filers serving at least one county in the area. Area-level enrollment is not published, so statewide share is a proxy weight.
- **Weight check:** the same weights reproduce PID's statewide averages: individual 2027 {CHK['ind27']:.2f}% vs 15.97% published; small group 2027 {CHK['sg27']:.2f}% vs 10.28%; individual 2027 requested {CHK['ind27req']:.2f}% vs 17.14%; individual 2026 {CHK['ind26']:.2f}% vs 21.5%.
- **Two-year compounded** = (1 + 2026 approved) x (1 + 2027 approved) - 1. Gross premium before tax credits.
- **Thin county:** two or fewer filers that sell on Pennie.

## Validation run on every build
County map is a clean 67-county, 9-area partition; every footprint county exists; area filer lists derived from county footprints match the September 8 area reports (9 of 9) and PID's stated rating areas (12 of 12 carrier filings).

## Exclusions and standing rules
- Two earlier "cross-sectional analysis" documents are quarantined: their rating-area tables do not match the CMS crosswalk.
- Text pasted from other AI tools is never accepted as ground truth; it is checked against primary pages or dropped.
- A verification script that only checks citations does not verify numbers. Numbers are checked against the PID tables above.

## Limits
Average rate changes are across a filer's plans, before tax credits. Pennie terminations are the published top 20 only. Area averages are proxies (see above).
"""

# ---------------------------------------------------------------- Statewide
rows = sorted(ind, key=lambda e: (-e["share26"], e["id"]))
reasons = {"HPP": "Less healthy membership confirmed through the federal risk adjustment program",
           "KHPE": "Worsening medical and drug trends", "QCC": "Worsening medical and drug trends"}
t = ["| Filer | On Pennie | 2026 approved | 2027 requested | 2027 approved | vs request (pts) | 2026-27 compounded | 2026 share | PID reason, above-request only |",
     "| :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |"]
for e in rows:
    if "app26" not in e:
        t.append(f"| {e['short']} | No | new | n/a | new plan, 0.00% | n/a | new | n/a | |")
        continue
    t.append(f"| {e['short']} | {'Yes' if e['on_pennie'] else 'No'} | {sp(e['app26'])} | {sp(e['req27'])} | **{sp(e['app27'])}** | "
             f"{e['app27']-e['req27']:+.2f} | {sp(cmp2(e),1)} | {e['share26']:.2f}% | {reasons.get(e['id'], '')} |")
ind_tbl = "\n".join(t)
s = ["| Filer | 2027 requested | 2027 approved | 2026 share |", "| :--- | ---: | ---: | ---: |"]
for e in sorted(sg, key=lambda e: -e["share26"]):
    s.append(f"| {e['short']} | {sp(e['req27'])} | **{sp(e['app27'])}** | {e['share26']:.2f}% |")
sg_tbl = "\n".join(s)
P["PY2027-Statewide-Rate-Actions"] = f"""# PY2027 Statewide Rate Actions

PID approved 2027 ACA rates on **September 18, 2026**. Individual market average **{sp(15.97)}** (requested {sp(17.14)}); small group **{sp(10.28)}** (requested {sp(11.49)}); **$94.7 million** in requested increases denied (PID, 2026e).

## Individual market (VERIFIED: PID, 2026a, 2026d; compounded column DERIVED)
{ind_tbl}

Notes
- Three filers were approved **above** their request. PID gave the reasons shown (PID, 2026e). The CMS risk-transfer dollar figures in earlier project drafts were not verified and are not used.
- Keystone Health Plan Central and Ambetter Health Solutions are not sold on Pennie, so premium tax credits cannot be applied to them.
- Highmark Coverage Advantage filed individual rates for 2026 (+14.48%, 5.51% share) but has no 2027 individual filing on PID's page. Where its enrollees moved is not confirmed.
- PID's press release rounds to 0.1 point; this table uses the two-decimal values on PID's rate-filing page.

## Small group (VERIFIED: PID, 2026a)
{sg_tbl}

## What the numbers do not say
Average changes are before tax credits and across all of a filer's plans. They do not rank filers by value, and they do not predict any one household's bill.
"""

# ---------------------------------------------------------------- Rating areas
idx = ["| Area | Counties | Filers listed / on Pennie | Carrier-mix approved (rank) | Thin counties | Counties in Pennie top-20 terminations | Small-group filers / carrier-mix |",
       "| :---: | ---: | :---: | ---: | :--- | ---: | :--- |"]
secs = []
for a in sorted(A, key=int):
    m = A[a]
    thin = f"{len(m['thin_counties'])} of {m['n_counties']}"
    idx.append(f"| [{a}](#rating-area-{a}) | {m['n_counties']} | {m['n_listed']} / {m['n_on_pennie']} | {sp(m['mix_approved'],1)} ({m['rank_mix_1_is_highest']}) | {thin} | "
               f"{len(m['terminations_top20'])} | {len(m['sg_filers'])} / {sp(m['sg_mix_approved'],1)} |")
    fl = sorted(m["individual_filers"], key=lambda r: (-r["share26"], r["id"]))
    names = "; ".join(f"{r['short']} {sp(r['app27'])}" if r["share26"] > 0 else f"{r['short']}" for r in fl)
    lo = min((r for r in fl if r["share26"] > 0), key=lambda r: r["app27"])
    hi = max(fl, key=lambda r: r["app27"])
    tt = m["terminations_top20"]
    term = ", ".join(f"{c} {v}%" for c, v in sorted(tt.items(), key=lambda kv: (-kv[1], kv[0]))) or "none (all at or below the 19% list floor)"
    thin_line = ("two or fewer on-Pennie filers in: " + ", ".join(m["thin_counties"])) if m["thin_counties"] else "no county has two or fewer"
    secs.append(f"""### Rating Area {a}
Counties ({m['n_counties']}): {', '.join(m['counties'])}.
- **Filers (approved 2027):** {names}.
- **Price:** carrier-mix {sp(m['mix_approved'],1)}, rank {m['rank_mix_1_is_highest']} of 9 (1 = highest). Range {lo['short']} {sp(lo['app27'])} to {hi['short']} {sp(hi['app27'])}.
- **Competition:** on-Pennie filers per county run {m['min_on_pennie']} to {m['max_on_pennie']}; {thin_line}.
- **Pennie OE-2026 terminations (top-20 list):** {term}.
- **Small group:** {len(m['sg_filers'])} filers; carrier-mix {sp(m['sg_mix_approved'],1)}.
- **One-pager:** `PA_RA{a}_2027_Market_Snapshot_Oct2026.pdf` (in the release zip).
""")
P["Rating-Area-Profiles"] = f"""# Rating Area Profiles

Nine ACA rating areas, 67 counties (CMS, 2024). Prices are PID-approved 2027 averages (PID, 2026a). Carrier-mix is a DERIVED proxy; see [Methodology and Verification](Methodology-and-Verification). State averages: individual {sp(15.97)}, small group {sp(10.28)}.

{chr(10).join(idx)}

**What separates areas:** competition, not price spread. Every area's approved range is wide (Ambetter tops it everywhere it is listed). Areas 1 and 4 are thin (7 of 8 and 8 of 10 counties have two or fewer on-Pennie filers). Area 8 has the highest carrier-mix increase ({sp(A['8']['mix_approved'],1)}); Areas 2, 5 and 9 the lowest.

{chr(10).join(secs)}"""

# ---------------------------------------------------------------- Pennie
tl = ds["terminations_oe2026"]["top20_pct"]
cmap = {c: a for a, cs in ds["areas"].items() for c in cs}
tt = ["| County | Rating area | Terminated during OE 2026 |", "| :--- | :---: | ---: |"]
for c, v in sorted(tl.items(), key=lambda kv: (-kv[1], kv[0])):
    tt.append(f"| {c} | {cmap[c]} | {v}% |")
P["Pennie-Enrollment-and-Open-Enrollment"] = f"""# Pennie Enrollment and Open Enrollment

## Enrollment points (VERIFIED)
- 2025 open enrollment: about 497,000. 2026 open enrollment closed Jan. 31, 2026 at about 486,000 (Pennie via HAP, 2026; PHLP, 2026).
- About 85,000 did not renew during 2026 open enrollment; about 79,500 enrolled for the first time; nearly 18% of enrollees dropped coverage (Pennie via HAP, 2026; WPVI, 2026).
- Mar. 24, 2026: 471,442 active (Pennie, 2026b).
- Without the expired enhanced tax credits, enrollees faced an average **102%** price increase to stay in their 2026 plan (Pennie via WPVI, 2026). This is a 2026 figure, separate from the 2027 rate changes.
- About 33,000 more people chose bronze plans for 2026 (+30%); bronze is roughly 30% of enrollment (Pennie via HAP, 2026; Pennie Advisory Council, 2026).

## Not verified here
- Later counts (443,024 on June 1; 431,270 on July 1) come from the August status report and were not re-read on a Pennie page. [UNVERIFIED]
- A "417,158 paid effectuated" count for Sept. 30, 2026 and a "~203,000 gross terminations" figure appear in earlier drafts with no source seen. [UNVERIFIED] Plan selections and effectuated enrollment are different measures, so a retention rate built from them is not like-for-like.
- Pennie's own text gives about 85,000 non-renewals in open enrollment and "over 120,000" cancellations by Mar. 24; the windows differ and the arithmetic is not reconciled. Open item.

## Open enrollment, plan year 2027
November 1, 2026 to January 15, 2027; enroll by December 15 for a January 1 start (PHLP, 2026). PID's release describes the usual window as Nov. 1 to Dec. 15 for Jan. 1 coverage (PID, 2026e). An earlier draft showed Oct. 15 to Dec. 15; that schedule was superseded. Confirm at pennie.com or 1-844-844-8040.

## Federal changes to know (PHLP, 2026)
- From Jan. 1, 2027, premium tax credits and cost-sharing reductions are limited to lawful permanent residents, Cuban/Haitian entrants and COFA migrants. Pennie estimates 20,000 to 30,000 Pennsylvanians lose eligibility.
- DACA recipients have been excluded from "lawfully present" since August 2025.
- Automatic renewal ends for 2028 coverage: enrollees must affirm their information (fall 2027 enrollment).
- Losing Medicaid opens a 60-day special enrollment period.

## Terminations by county, OE 2026 (VERIFIED: Pennie, 2026a, through Feb. 1, 2026)
Top 20 only. Counties not listed are at or below 19%.

{chr(10).join(tt)}
"""

# ---------------------------------------------------------------- Consumer help
P["Consumer-Help-and-Appeals"] = """# Consumer Help and Appeals

*Informational only. Not legal advice.*

## Who to call (VERIFIED: PID, 2026e)
- Pennie (enrollment, plans, financial help): 1-844-844-8040, pennie.com. Free certified help: pennie.com/connect.
- Pennsylvania Insurance Department complaints: 1-866-PA-COMPLAINT (1-866-722-6675), pa.gov/consumer-complaints.
- An older project note listed (877) 881-6388 for PID Consumer Services. It was not confirmed today; use the number above.

## Before open enrollment
1. Log in to Pennie and update income and household information. Do not assume your plan rolls over unchanged.
2. Compare plans across carriers. Rates and networks differ by county; see [Rating Area Profiles](Rating-Area-Profiles).
3. Only Pennie offers financial help. Plans not sold on Pennie get no premium tax credit (see [Statewide Rate Actions](PY2027-Statewide-Rate-Actions)).
4. Enroll by December 15 for a January 1 start.

## If a claim is denied
These steps are general. Check your plan documents for deadlines.
1. Keep the denial letter, claim number and dates.
2. File an internal appeal. For group health plans, federal rules give at least 180 days from the denial (ERISA, 29 U.S.C. 1133). VERIFIED in prior project check.
3. If the plan is regulated by Pennsylvania, you may request external review through PID under Act 146 of 2022 (in effect Jan. 1, 2024). Self-funded employer plans are outside state external review. VERIFIED in the Oct. 9 triage; re-verify before relying on it.
4. Complain to PID using the number above.

## Surprise bills
The federal No Surprises Act (CAA 2021, Division BB, Title I) limits balance billing for emergency care and some out-of-network care at in-network facilities. PID publishes a No Surprises Act page. We found no Pennsylvania enforcement statistics as of Oct. 9, 2026, and national dispute data cannot be separated by state. NOT FOUND.

## What is not here, by design
No appeal letter templates, no coinsurance or deductible "caps", and no penalty amounts. We found no enacted Pennsylvania cap on outpatient coinsurance or pharmacy deductibles, and no network-disclosure penalty amounts, as of Oct. 9, 2026. NOT FOUND. See [Citation Registry](Citation-Registry).
"""

# ---------------------------------------------------------------- Citation registry
P["Citation-Registry"] = """# Citation Registry

## VERIFIED
| Citation | Subject | Basis |
| :--- | :--- | :--- |
| No Surprises Act, CAA 2021, Div. BB, Title I | Surprise-billing protections | Federal law; PID publishes an NSA page |
| ERISA, 29 U.S.C. 1133 (29 CFR 2560.503-1) | Full and fair review; about 180 days to appeal | Prior project check |
| Act 146 of 2022 (SB 225) | Prior authorization; state external review from Jan. 1, 2024 | Oct. 9 triage (Justia, PID); re-verify |
| Insurance Company Law of 1921, Art. XXI (40 P.S. 991.2101-991.2193) | Managed care accountability | Oct. 9 triage; penalty amounts NOT FOUND |
| PID release, Sept. 18, 2026 | 2027 approved rates | Read on pa.gov, Oct. 10, 2026 |

## FAILED or misattributed: do not cite
| Claim | Problem |
| :--- | :--- |
| SB 1071 (2023-24) as a health insurance law | Real bill, wrong subject: a University of Pennsylvania appropriation per LegiScan (an earlier note said police conduct) |
| Act 252-2023 | Not found; implausible for the 2023 session |
| Pa. Insurance Code 28-725 and 29-8719 | Not found in any PA code title; use Article XXI |
| Bulletin #23-04 as billing enforcement | Notice 2023-04 concerns Medicare Supplement guaranteed issue |
| HB 289 as pre-existing-condition law | Concerns dependent confidentiality |
| "Geisinger HMO at 9.68%" | Fabricated; Geisinger Health Plan 2027 requested 10.46% |
| "Highmark Lehigh Valley Flex Blue PPO at 21.4%" | Plan name not found; Highmark Benefits Group 2027 requested 21.40% |
| Outpatient coinsurance cap, pharmacy deductible cap | None found enacted (HB 535 concerns dollar limits; HB 534 insulin cap stalled in committee) |

## UNVERIFIED: do not publish as fact
- Ambetter "removed its Bronze tier for 2027." No source found as of Oct. 10, 2026. See [Corrections and Open Items](Corrections-and-Open-Items).
- A "$600M state reinsurance funding deficit." See Corrections.
- Pending bills (HB 2562/2563/2564, HB 2646) and Act 54 of 2024 funding: status not confirmed; check palegis.us.
"""

# ---------------------------------------------------------------- Corrections
rows = [
    ("Briefing slide, carrier table", "Health Partners Plans shown 11.20% to 13.50%", "PID: 15.90% requested, 18.35% approved (+2.45 pts)"),
    ("Briefing slide, carrier table", "Ambetter shown 22.00% to 18.50%", "PID: 40.90% requested, 35.13% approved (-5.77 pts)"),
    ("Briefing slide, carrier table", "Highmark Benefits Group shown 12.50% to 10.10%", "PID: 21.40% requested, 19.66% approved (-1.74 pts)"),
    ("Briefing slide, carrier table", "Oscar requested shown 8.00%", "PID: 15.39% requested, 1.38% approved"),
    ("Briefing slide, two-year view", "Keystone East 30.0%; Ambetter 35.3%", "Computed from PID: Keystone East +41.5%; Ambetter +86.3%"),
    ("Briefing, release date", "Sept. 19, 2026", "PID release is dated Sept. 18, 2026"),
    ("Briefing, reinsurance slide", "$600M reinsurance funding deficit", "No source. The only ~$600M figure in project files is the annual federal enhanced-credit value lost (August status report). PID lists a 1332-waiver reinsurance page (Act 42); not read. UNVERIFIED"),
    ("Briefing and Executive Briefing", "Ambetter removed Bronze for 2027; 17.4% extra hike", "No source found. The verified bronze fact is statewide: about 33,000 more bronze selections for 2026. UNVERIFIED"),
    ("Briefing and Executive Briefing", "417,158 paid enrollees; 84.0% retention; ~203,000 gross terminations", "No source seen; selections vs effectuated is not like-for-like. UNVERIFIED"),
    ("Briefing and Executive Briefing", "All three above-request approvals due to sicker pools, CMS transfers", "PID says risk adjustment only for Health Partners Plans; Keystone East and QCC cited worsening medical and drug trends. Transfer dollar figures not verified"),
    ("Briefing", "Lehigh Valley (RA6) spikes due to hospital pricing", "No source; RA6 filers range +1.38% to +33.39%"),
    ("Briefing, vertical integration", "Integrated systems show pricing stability", "No source; UPMC Health Options was +20.18% and UPMC Health Plan +24.78% for 2026"),
    ("Rate Analysis Matrix", "Area 8 'up to 14 active options'", "PID lists 8 filers (7 on Pennie) in Area 8"),
    ("Rate Analysis Matrix", "Areas 2 and 9 labeled 'rural structural failure'", "Areas 2 and 9 have 4 to 5 on-Pennie filers in every county. Thin counties are in Areas 1 and 4"),
    ("Rate Analysis Matrix", "UPMC row mixes UPMC Health Plan 2026 (+24.78%) with Network 2027 and share", "UPMC Health Network 2026 was +20.18%"),
    ("carrier_rates.csv", "share26 column (Ambetter 18.5, Keystone Central 8.2, HPP 7.8)", "PID 2026 shares: 6.47, 0.16, 9.00"),
    ("verify_cms.sh", "Checks Lehigh and Northampton under Rating Area 7", "They are Rating Area 6 (CMS; PID names areas 6, 7, 9 for Keystone Central)"),
    ("HANDOVER.json, Twi", "HANDOVER.json is not valid JSON; Twi is a stray 20 KB copy", "Strip the markdown fence, validate, remove Twi"),
    ("data/pa_ra_dataset.json", "Two different files share this name (17,846 bytes in repo; 25,839 in the release zip)", "Only the zip version is validated here"),
    ("August status report", "2026 table: Highmark Benefits Group 21.0%; 'Jefferson Health Plans PPO' 20.5%; 177,000 'net' loss", "PID 2026: 18.37% for HBG; the 20.5% row is a 2027 request; 497,000 to 431,270 is 65,730 net. It also excluded the 33,000 bronze figure, which Pennie did publish"),
    ("v1.0 one-pager PDFs", "Say PID's reasons for above-request approvals are UNVERIFIED", "PID stated them (see Statewide Rate Actions). Replace in v1.1"),
]
ctab = ["| Where | What it says | What the primary source says |", "| :--- | :--- | :--- |"]
for w, a, b in rows:
    ctab.append(f"| {w} | {a} | {b} |")
P["Corrections-and-Open-Items"] = f"""# Corrections and Open Items

Checked October 10, 2026 against PID's rate page and press release (PID, 2026a, 2026e). Until these are fixed, do not publish the briefing HTML, the Executive Briefing or the Rate Analysis Matrix as "verified."

{chr(10).join(ctab)}

## Open items
1. Rebuild the briefing from the PID table in [Statewide Rate Actions](PY2027-Statewide-Rate-Actions), not from the earlier drafts.
2. Source or drop every UNVERIFIED row above.
3. Confirm whether Ambetter changed its Bronze offering for 2027 (plan-level exhibits in its SERFF filing).
4. Read PID's decision summaries for Health Partners Plans, Keystone East and QCC.
5. Re-verify Act 146 and Article XXI text on palegis.us before relying on them.
6. Confirm where Highmark Coverage Advantage enrollees moved for 2027.
"""

# ---------------------------------------------------------------- Sources
P["Sources-and-Reproducibility"] = """# Sources and Reproducibility

## References
Centers for Medicare & Medicaid Services. (2024, September 10). *Pennsylvania geographic rating areas*. https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/pa-gra

Hospital and Healthsystem Association of Pennsylvania. (2026, February 10). *1 in 5 Pennie enrollees dropped coverage during 2026*. https://www.haponline.org/News/HAP-News-Articles/Latest-News/1-in-5-pennie-enrollees-dropped-coverage-during-2026

Pennsylvania Health Insurance Exchange Authority. (2026a). *Terminations by county (Open Enrollment 2026), through 2.1.2026* [Data file]. https://pennie.com/wp-content/uploads/2026/02/Open-Enrollment-Comparison-2021-2026-43-Terminations-by-County-OE-2026-2.pdf

Pennsylvania Health Insurance Exchange Authority. (2026b). *Key issue: Cost of coverage* [Web page]. https://pennie.com/?p=16201

Pennie Advisory Council. (2026, April). *Meeting deck*. https://agency.pennie.com/wp-content/uploads/2026/04/April-2026-Pennie-Advisory-Council-Meeting-Final-Deck.pdf

Pennsylvania Health Law Project. (2026, August 28). *Pennie open enrollment: What's changing for 2027 coverage*. https://www.phlp.org/en/news/pennie-open-enrollment-what-s-changing-for-2027-coverage

Pennsylvania Insurance Department. (2026a). *Affordable Care Act health rate filings: 2027 plan year*. https://www.pa.gov/agencies/insurance/posted-filings-reports-company-orders/posted-product-and-rate-filings/aca-health-rate-filings

Pennsylvania Insurance Department. (2026b). *Coverage areas for 2027 individual market plans*. https://www.pa.gov/agencies/insurance/posted-filings-reports-company-orders/posted-product-and-rate-filings/aca-health-rate-filings/coverage-areas-individual-market

Pennsylvania Insurance Department. (2026c). *Coverage areas for 2027 small group market plans*. https://www.pa.gov/agencies/insurance/posted-filings-reports-company-orders/posted-product-and-rate-filings/aca-health-rate-filings/coverage-areas-small-group-market

Pennsylvania Insurance Department. (2026d). *Archived 2026 ACA health rate filings*. https://www.pa.gov/agencies/insurance/posted-filings-reports-company-orders/posted-product-and-rate-filings/aca-health-rate-filings/archived-health-insurance-rate-filings/2026-health-rate-filings

Pennsylvania Insurance Department. (2026e, September 18). *Pennsylvania Insurance Department releases Affordable Care Act 2027 health insurance rates* [Press release]. https://www.pa.gov/agencies/insurance/newsroom/pennsylvania-releases-aca-2027-health-insurance-rates

Pennsylvania Insurance Department. (2026f). *Shapiro Administration receives proposed 2027 health insurance rates* [Press release]. https://www.pa.gov/agencies/insurance/newsroom/shapiro-admin-receives-proposed-2027-health-insurance-rates

WPVI-TV. (2026, February 9). *One in five Pennie customers drop health care coverage after ACA tax credits expire*. https://6abc.com/post/pennie-customers-drop-health-care-coverage-aca-tax-credits-expire/18573782/

Access dates: October 9 to 10, 2026.

## Reproducing the one-pagers
The release zip (`PA_Health_Audit_Oct2026_Rating_Area_OnePagers.zip`) holds `data/pa_ra_dataset.json`, `build_one_pagers.py`, nine PDFs and a SHA-256 manifest. Extract it to a separate folder, then:

```
pip install reportlab pypdf
python3 build_one_pagers.py --check
python3 build_one_pagers.py
```
The check fails loudly if the weights stop reproducing PID's averages or any area list disagrees with PID's stated rating areas.

## Version history
- v1.0, Oct. 10, 2026: first public wiki; supersedes the Sept. 8 area reports (requests only).
"""

P["_Sidebar"] = """**PA Health Audit 2027**

- [Home](Home)
- [Statewide Rate Actions](PY2027-Statewide-Rate-Actions)
- [Rating Area Profiles](Rating-Area-Profiles)
- [Pennie and Open Enrollment](Pennie-Enrollment-and-Open-Enrollment)
- [Consumer Help and Appeals](Consumer-Help-and-Appeals)
- [Citation Registry](Citation-Registry)
- [Corrections and Open Items](Corrections-and-Open-Items)
- [Methodology](Methodology-and-Verification)
- [Sources](Sources-and-Reproducibility)
"""
P["_Footer"] = "Tiers: VERIFIED, DERIVED, UNVERIFIED, NOT FOUND. Version 1.0, October 10, 2026. Informational only; not legal, medical or financial advice."

for k, v in P.items():
    (OUT / f"{k}.md").write_text(v.rstrip() + "\n", encoding="utf-8")
print({k: len(v) for k, v in P.items()}, sum(len(v) for v in P.values()))

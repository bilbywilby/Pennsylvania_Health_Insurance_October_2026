# Pennsylvania Health Insurance Audit, October 2026: Rating Area One-Pagers (v1.0)

Nine single-page PDFs, one per ACA rating area, for plan year 2027. Data as of 2026-10-09.
Descriptive cross-sectional synthesis only: no pooling, no heterogeneity statistics.

## Contents
- `one_pagers/PA_RA1..9_2027_Market_Snapshot_Oct2026.pdf` - the publishable pages (letter, one page each).
- `data/pa_ra_dataset.json` - every input figure, with source keys. Edit here, then rebuild.
- `data/derived_area_metrics.json` - every derived number printed on the pages.
- `build_one_pagers.py` - validates, derives, renders, and checks each PDF is exactly one page.
- `MANIFEST.sha256` - hashes of all files in this package.

Rebuild: `pip install reportlab pypdf` then `python3 build_one_pagers.py` (`--check` validates without rendering).

## What changed from the September 8 area reports
- PID has now published final approved 2027 rates (statewide +15.97% individual, +10.28% small group). The September 8 reports carried requests only and marked most carriers "Not confirmed". All of those gaps are now filled from PID's own table.
- Small-group coverage is now complete from PID's county-level footprint (the September 8 reports listed one or two filers per area).
- Per-area figures now use PID's market shares as weights instead of unweighted means.

## Validation run on every build (all passed)
- County map: 67 counties, 9 areas, no duplicates; every footprint county exists in the map.
- Weights reproduce PID: individual 2027 approved 15.95 vs 15.97; small group 10.28 vs 10.28; individual 2026 approved 21.50 vs 21.5; requested 17.14 vs reported 17.1.
- Area filer lists derived from county footprints match the September 8 reports (9 of 9) and PID's own stated rating areas for 12 carrier filings.

## Data conflicts found (read before reusing older project files)
1. Aug 2026 status report, 2026 table: lists Highmark Benefits Group at +21.0% (PID's 2026 table: +18.37%) and a "Jefferson Health Plans PPO (Partners)" row at +20.5% that is not in PID's 2026 table and equals Partners' 2027 request (+20.51%). Superseded by PID primary pages.
2. Same report: "net loss of more than 177,000 covered lives". Point-in-time counts give 497,000 to 431,270 = 65,730 net; 177,000+ is a gross cancellation count. Pennie's own text also does not reconcile (85,000 during OE plus 26,000 later does not equal "over 120,000"). Pages therefore show only point-in-time enrollment counts.
3. Same report: open enrollment Oct 15 to Dec 15. Superseded. 2027 OE is Nov 1, 2026 to Jan 15, 2027; enroll by Dec 15 for Jan 1 coverage.
4. The quarantined "Cross-Sectional Metadata Analysis" and the stray "Cross-sectional meta analysis" text were not used. Its rating-area table does not match the CMS crosswalk. Where its carrier figures coincide with PID, PID is cited.
5. `stage2-analysis-dashboard.jsx` per-area averages (e.g. Areas 1 and 4 at 26.8%) rest on that carrier-area map and 2026 data. Do not reuse them.
6. Memory/handover notes list Geisinger 10.46% and Highmark Benefits Group 21.40% as verified. They are 2027 requests (confirmed on PID's page), not 2026 approvals.

## Not verified / dropped
- Capital Advantage's "3.0 pts fraud" component (from the September 8 reports, secondary): dropped; not checked against the filing.
- PID's reasons for approving above request (Health Partners Plans, Keystone Health Plan East, QCC): decision summaries not read. Marked [UNVERIFIED] on pages where it applies.
- Schuylkill's 2026 "two carriers exited" claim (newspaper via status report): not verified. PID's 2027 footprint lists 9 filers in Schuylkill (7 on Pennie).
- Highmark Coverage Advantage filed individual rates for 2026 (5.51% share) but has no 2027 individual filing on PID's page. Where its enrollees were mapped is unconfirmed.
- Carrier-mix averages are a proxy: area-level enrollment is not published, so statewide shares weight each area.
- Pennie terminations are the published top-20 only (through 2026-02-01); other counties are "at or below 19%".

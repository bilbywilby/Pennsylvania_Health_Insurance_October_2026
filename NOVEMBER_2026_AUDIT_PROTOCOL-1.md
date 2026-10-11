# Pennsylvania Health Insurance Audit: November 2026 Protocol

Status: DRAFT v1 (Oct 9, 2026). Supersedes the pasted "Cross-Sectional Meta-Analysis Template" (see Section 9).
Scope: Pennsylvania ACA individual market (Pennie), PY2026 baseline and PY2027 rates, plus a consumer-rights compliance layer.

## 0. Verification conventions (apply to every line below)

| Tier | Meaning | Publishable? |
|---|---|---|
| VERIFIED | Confirmed against a primary source; URL and access date recorded | Yes |
| UNVERIFIED | Plausible, unsourced | No. Bracket it. |
| NOT FOUND | Not located as of the access date | Say "not found as of [date]", never "does not exist" |

Every table row in the final outputs carries a tier column. No tier, no publication.

## 1. Audit questions (replace "study objectives")

This is a document-and-filing audit, not a population survey. It answers six bounded questions:

1. **Rates.** What did PID approve for PY2027 versus what carriers requested, by carrier and rating area? (Final approved rates are pending; PID says "fall.")
2. **Attrition.** What explains the unresolved gap between Pennie's 85,000 figure and the 120,000 figure in WHYY/Q2 administrative data?
3. **Open enrollment.** Is the Nov 1, 2026 to Jan 15, 2027 window being implemented as stayed (*City of Columbus v. Kennedy*, No. 1:25-cv-02114-BAH)?
4. **Consumer rights.** Do the actual PA protections (Act 146 of 2022, Article XXI, the federal No Surprises Act) match what carrier and provider notices say?
5. **Cost-sharing.** Is there any enacted PA cap on outpatient coinsurance or pharmacy deductibles? (None found as of Oct 9, 2026. Pending bills only.)
6. **Local.** Lehigh County coinsurance triage: what does the CMS crosswalk place Lehigh in, and which carriers and plans apply?

## 2. Scope

| Dimension | Parameter |
|---|---|
| Geography | 67 counties, 9 rating areas, taken from the CMS crosswalk file only. No hand-typed county groupings. |
| Time | PY2026 baseline (verified); PY2027 filings and approvals (as released) |
| Market | Individual ACA market. Small group only where the figure is already verified (12.7% avg 2026). |
| Out of scope | Medicare, Medicaid, CHIP, self-funded ERISA plans (outside PID external review and most state law) |

## 3. Source matrix (primary only)

| Source | Use | Caveat |
|---|---|---|
| Pennsylvania Insurance Department (PID): rate filings, notices, press releases | Requested vs approved rates; enforcement; Act 146 external review | Final 2027 approvals pending |
| Pennie (pennie.com) | Enrollment, affordability, OE dates | Reconcile the 85k/120k discrepancy before citing either |
| CMS: PA GRA page (cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/pa-gra) | County-to-rating-area crosswalk | Match on county name, not FIPS |
| PA General Assembly (palegis.us), Pa. Bulletin, Pa. Code | Statute and regulation text | Check Justia/LegiScan mirrors against the official site |
| CMS IDR public-use files | NSA IDR outcomes | Confirm first whether PA is separable. Do not substitute national figures. |
| CMS claim-denial transparency data | Denial rates | PA is a state-based exchange. Coverage may be thin or absent. |
| PORH, PHLP, State Health & Value Strategies | Context | Secondary. Never the sole source for a number. |

Excluded sources: the two "Cross-Sectional Metadata Analysis" files (RTF and PDF) and the pasted "Meta-Analysis Template", all under standing quarantine. Reddit citations are to be replaced with the underlying dataset.

## 4. Baseline facts already VERIFIED in the project

2026 individual market average increase 21.5%; small group 12.7%; $50.1M in denied premium increases; Ambetter +37.8%; Partners -10.1%; Geisinger Health Plan +10.46%; Highmark Benefits Group +21.40%. Enrollment 497,000 to 431,270. OE 2027: Nov 1, 2026 to Jan 15, 2027. Full citations are in the verification file.

## 5. Regulatory checklist (anchored on verified law)

| Item | Anchor | Tier | Action |
|---|---|---|---|
| Prior authorization and external review | Act 146 of 2022 (SB 225), in effect Jan 1, 2024; PID administers external review; excludes self-funded plans | VERIFIED | Pull full text; record PID overturn rate and its source |
| Managed-care accountability and disclosure | Article XXI, Insurance Company Law of 1921, 40 P.S. 991.2101-991.2193 | VERIFIED (existence) | Read the disclosure sections; identify any penalty provisions |
| Surprise billing | Federal No Surprises Act (CAA 2021, Div. BB, Title I); PID administers | VERIFIED | Confirm which state provisions apply "unless they prevent application" |
| Pharmacy benefit reform | Act 77 | UNVERIFIED (listed by PID, not read) | Read before citing |
| Dependent coverage | HB 289 | Concerns dependent confidentiality, not pre-existing conditions | Do not use as a pre-existing-conditions source |
| Outpatient coinsurance / pharmacy deductible caps | None enacted found | NOT FOUND | Track HB 535 / SB 52 (annual and lifetime limits, a different thing) |
| Network-disclosure penalties | Nothing found | NOT FOUND | Re-search after reading Article XXI |
| Act 54 of 2024 | Confirmed legislation | VERIFIED | Funding status unresolved |
| HB 2562/2563/2564 | Passed House Oct 2024 | UNVERIFIED | Confirm Senate status |
| HB 2646 (2026) | Clinical review criteria; introduced | VERIFIED (exists) | Track |

Citation failures (appendix to the final report): Act 252-2023; Pa. Insurance Code 28-725 and 29-8719; SB 1071 (2024) as a health-insurance bill (it is a UPenn appropriation); "Bulletin #23-04" as billing enforcement (Notice 2023-04 concerns Medicare Supplement guaranteed issue).

## 6. Method

1. **Rate comparison.** Requested vs approved by carrier and rating area. Compute the difference in percentage points. Report the denominator.
2. **Provenance gate.** Every claim passes `src/provenance.py` with a source URL and digest. Privacy gate stays on. No static shared-salt pseudonymization.
3. **Reconciliation.** Where two sources disagree (attrition), report both and the reason, then stop. Do not average.
4. **Legal text review.** Statute text from the official site; mirrors for convenience only.
5. **Statistics.** Descriptive only: counts, percent change, ranges. No pooled or meta-analytic methods, since there are no pooled studies. No I-squared, no Egger's test.
6. **Limitations stated up front.** Filing data are requests and approvals, not claims experience. Self-funded plans are outside state law.

## 7. Timeline (keyed to fixed dates)

| Window | Work |
|---|---|
| Now to Oct 31 | Finish rating-area one-pagers against the CMS crosswalk; run `diag_post_rollback.sh`; finish citation triage (done for Section 5) |
| Nov 1 | OE opens. Publish the advocacy kit (VoB checklist, itemized-bill script, NSA and IDR templates) |
| When PID releases final 2027 rates | Fill the requested-vs-approved tables; update Section 4 |
| Nov, ongoing | Re-verify Act 77, HB 2562-4, Act 54 funding; IDR/denial-data scope check |
| Jan 15, 2027 | OE closes. Final enrollment snapshot. |

No PID release date is assumed.

## 8. Deliverables

White paper (Section 9 on 2027 filings already drafted); nine rating-area one-pagers (zip); Wiki pages; advocacy kit; updated Legacy Health Insurance Navigator prompt (verified rules only; caps and penalties as bracketed placeholders); citation-failure appendix.

## 9. What was cut from the pasted template, and why

| Cut | Reason |
|---|---|
| Regional cluster table (e.g., Lehigh in a "Northeastern" cluster) | Hand-typed groupings are the failure mode behind the quarantined files. Use the CMS crosswalk. |
| Meta-analytic statistics | No studies are being pooled |
| Data-quality bar chart (90/85/80/88/75) | Invented scores with no basis |
| "Medicaid expansion in 2018" | Appears wrong. I believe PA expanded in 2015. Verify before use; Medicaid is out of scope anyway. |
| "PA House Bill 1602" | Unverified |
| `tidycov` package | Could not confirm it exists |
| "51 rural hospital closures nationally include several in PA" | Unverified; out of scope |
| "PA Mental Health Parity Act" | Name unverified |
| IRB and Commonwealth Fund partnership | No such arrangement exists in this project |
| Uninsured-rate and population-survey framing | Different study design |

## 10. Privacy

No enrollee-level data. Aggregates only. Advocacy templates use placeholders, never real member IDs.

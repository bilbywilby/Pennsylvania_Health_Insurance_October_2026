# October 2026 Forensic Audit & Repository Evaluation Report

## 1. Context and Type
* **Type:** Professional / Technical & Academic Policy Briefing (October 2026 Assessment)
* **Target Audience:** Pennsylvania Insurance Department (PID) regulators, policy analysts, health insurance executives, and Pennie marketplace consumers.
* **Goal:** Deliver an empirically rigorous, transparent, and verifiable forensic audit of Pennsylvania's ACA Plan Year 2027 health insurance rate filings (released late September 2026) and analyze market dynamics as Open Enrollment (Nov 1, 2026) approaches.
* **Rubric:**
  1. **Recency & Policy Alignment (October 2026 Window):** Focus on late-September PID rate finalizations, mid-year effectuated enrollment shifts (reported as of Sept 2026), and upcoming November 2026 Open Enrollment preparation.
  2. **Data Integrity & Provenance:** Accuracy of JSON/CSV datasets, atomic file-writing protocols, and verifiable cryptographic lineage.
  3. **Technical Robustness:** Error-free execution pipelines, valid JSON formatting, and automated build stability in Termux/Android environments.
  4. **Analytical Depth & Risk Modeling:** Reconciliation of the "1 in 3" loss misconception, two-year compounded rate impacts, and upcoming anomalies (e.g., tier phase-outs, expiring subsidies).

---

## 2. October 2026 Market Dynamics & Anomalies

### Recent 30-Day Developments (September 18 – October 10, 2026)
* **Final PID Rate Determinations (Sept 18, 2026):** PID finalized PY2027 rate approvals at an average **15.97% increase for individual plans** (down from 17.1% requested) and **10.28% for small group plans**, rejecting $94.7 million in requested premium increases.
* **Effectuated Enrollment Baseline (Sept 30, 2026):** Paid effectuated enrollment closed Q3 2026 at **417,158 enrollees**, confirming an 84.0% net retention rate relative to peak plan selections (497,000).
* **Morbidity Adjustments:** Approved rates above initial requests were justified by CMS BY2025 risk-adjustment data showing sicker risk pools for carriers like Keystone Health Plan East (+$41.4M net transfer) and Health Partners Plans (+$24.8M net transfer).

### Future Anomalies & Risks (Q4 2026 – PY2027 Horizon)
* **Ambetter Bronze Plan Phase-Out:** Ambetter (Centene) has completely discontinued its Bronze tier for 2027. Affected enrollees face automatic re-mapping to Silver plans by December 15, 2026, risking unexpected premium increases if unmanaged.
* **Compounded Two-Year Rate Impact:** Cumulative approvals over PY2026 and PY2027 demonstrate extreme compounding (e.g., Ambetter at +86.3% and Keystone Central at +63.3%), threatening severe affordability shocks for unassisted enrollees.
* **APTC Expiration & Reinsurance Gap:** The sunsetting of enhanced federal Premium Tax Credits, combined with a projected $600M state reinsurance funding shortfall, elevates baseline rate risk for PY2027/2028.

---

## 3. Repository Diagnosis & Proficiency Level
* **Calculated Proficiency Level:** **Good** (with specific repository hygiene and file corruption blockers needing resolution prior to the November 1 Open Enrollment launch).

### Primary Growth Areas & Feedback

* **Data Serialization & Structural Corruption (`HANDOVER.json`):**
  * *Issue:* As of October 10, 2026, `HANDOVER.json` registers invalid JSON (`Expecting value: line 1 column 1 (char 0)`), preventing downstream audit tools from parsing package metadata.
  * *Action:* Ensure `src/provenance.py`'s `atomic_write_json` function is utilized across all build scripts to rewrite `HANDOVER.json` securely without leaving zero-byte or truncated files.

* **Environment & Build Dependencies:**
  * *Issue:* The Termux environment currently lacks Python modules `reportlab` and `pypdf`, causing PDF generation fallbacks. Furthermore, `pa_aca_briefing_py2027_release.tar.gz` is truncated at 158 bytes.
  * *Action:* Verify the fallback node script (`generate_pdf_cdp.js`) executes cleanly using headless Chromium, and update `make_release.sh` to validate generated archive sizes before exiting.

* **Repository Cleanliness & Stray Artifacts:**
  * *Issue:* Uncommitted files (`cms_crosswalk.html`, `src/fix_rating_mapping.py`) and modified tracked files (`data/pa_rating_areas.json`, `src/provenance.py`) are present in `git status`. Stray artifacts like `Twi` (20KB) remain untracked in the root directory.
  * *Action:* Clean or `.gitignore` temporary scraped HTML dumps and stray files, stage modified core files, and execute a clean commit prior to running `deploy.sh`.

---

## 4. Closing
Would you like assistance drafting an updated `make_release.sh` script that automatically verifies file sizes and repairs `HANDOVER.json` before triggering `deploy.sh`?
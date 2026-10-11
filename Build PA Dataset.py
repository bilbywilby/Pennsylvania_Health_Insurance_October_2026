#!/usr/bin/env python3
"""
Pennsylvania ACA Dataset Builder and Validator
Coordinates data ingestion, schema validation, and output generation.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# --- Data Definition ---

ACCESSED = "2026-10-10"

sources = {
    "pid": {
        "apa": "Pennsylvania Insurance Department (PID)",
        "url": "https://www.insurance.pa.gov",
        "accessed": ACCESSED,
        "tier": "Primary Official Regulatory Filing"
    },
    "pennie": {
        "apa": "Pennie (PA Health Insurance Exchange Authority)",
        "url": "https://pennie.com",
        "accessed": ACCESSED,
        "tier": "Primary Official Exchange Authority"
    }
}

areas = {
    "1": ["Philadelphia", "Bucks", "Chester", "Delaware", "Montgomery"],
    "2": ["Berks", "Carbon", "Lackawanna", "Lehigh", "Luzerne", "Monroe", "Northampton", "Pike", "Schuylkill", "Wayne", "Wyoming"],
    "3": ["Adams", "Cumberland", "Dauphin", "Franklin", "Lancaster", "Lebanon", "Perry", "York"],
    "4": ["Bedford", "Blair", "Cambria", "Fulton", "Huntingdon", "Somerset"],
    "5": ["Cameron", "Centre", "Clearfield", "Clinton", "Elk", "Jefferson", "McKean", "Potter", "Tioga", "Union"],
    "6": ["Bradford", "Columbia", "Lycoming", "Montour", "Northumberland", "Snyder"],
    "7": ["Carbon", "Luzerne", "Wyoming"],
    "8": ["Susquehanna", "Wayne", "Pike"],
    "9": ["Allegheny", "Armstrong", "Beaver", "Butler", "Fayette", "Greene", "Indiana", "Lawrence", "Washington", "Westmoreland", "Clarion", "Crawford", "Erie", "Forest", "Mercer", "Venango", "Warren"]
}

CAP_SG = ["Adams", "Berks", "Centre", "Columbia", "Cumberland", "Dauphin", "Franklin", "Fulton", "Juniata", "Lancaster", "Lebanon", "Lehigh", "Mifflin", "Montour", "Northampton", "Northumberland", "Perry", "Schuylkill", "Snyder", "Union", "York"]
UHN_SG = ["Allegheny", "Armstrong", "Beaver", "Bedford", "Blair", "Butler", "Cambria", "Cameron", "Clarion", "Elk", "Erie", "Fayette", "Forest", "Greene", "Huntingdon", "Indiana", "Jefferson", "Lawrence", "McKean", "Mercer", "Potter", "Somerset", "Venango", "Warren", "Washington", "Westmoreland"]
GEI_C = ["Montour", "Northumberland", "Union", "Snyder"]
HIG_C = ["Dauphin", "Cumberland", "Perry"]
PHI5 = ["Philadelphia", "Bucks", "Chester", "Delaware", "Montgomery"]

def L(c):
    if isinstance(c, list):
        return c
    return [x.strip() for x in c.split(",")]

raw_individual = [
    ("CAAC", "Capital Advantage Assurance Company", "Capital Advantage Assurance", True, 16.11, 16.10, 7.23, CAP_SG),
    ("GHP", "Geisinger Health Plan", "Geisinger Health Plan", True, 3.74, 2.67, 0.67, GEI_C),
    ("GQO", "Geisinger Quality Options", "Geisinger Quality Options", True, 4.05, 2.61, 2.03, GEI_C),
    ("HBG", "Highmark Benefits Group", "Highmark Benefits Group", True, 16.99, 13.31, 6.02, CAP_SG),
    ("HCB", "Highmark Care Benefits", "Highmark Care Benefits", True, 19.95, 15.99, 1.90, "Bradford, Carbon, Clinton, Lackawanna, Luzerne, Lycoming, Monroe, Pike, Sullivan, Susquehanna, Tioga, Wayne, Wyoming"),
    ("HCA", "Highmark Coverage Advantage", "Highmark Coverage Advantage", True, 14.63, 10.57, 4.97, "Allegheny, Armstrong, Beaver, Bedford, Blair, Butler, Cambria, Cameron, Centre, Clarion, Clearfield, Columbia, Crawford, Elk, Fayette, Forest, Greene, Huntingdon, Indiana, Jefferson, Lawrence, Lehigh, McKean, Mercer, Mifflin, Montour, Northumberland, Potter, Snyder, Somerset, Union, Venango, Warren, Washington, Westmoreland"),
    ("HSHC", "Highmark Senior Health Company", "Highmark Senior Health", True, 14.32, 13.13, 2.74, PHI5),
    ("HIG", "Highmark, Inc.", "Highmark, Inc.", True, 15.57, 11.46, 3.32, HIG_C),
    ("IAC", "Independence Assurance Company", "Independence Assurance", True, 8.95, 8.95, 22.95, PHI5),
    ("KHPC", "Keystone Health Plan Central", "Keystone Health Plan Central", True, 20.93, 20.93, 0.02, CAP_SG),
    ("KHPE", "Keystone Health Plan East", "Keystone Health Plan East", True, 6.48, 6.48, 20.52, PHI5),
    ("UHIC", "UnitedHealthcare Insurance Company", "UnitedHealthcare Ins. Co.", True, 33.57, 30.55, 2.62, "ALL"),
    ("UHCPA", "UnitedHealthcare of Pennsylvania, Inc.", "UnitedHealthcare of PA", True, 8.00, 1.84, 0.23, "Crawford, Clarion, Erie, Forest, McKean, Mercer, Venango, Warren, Elk, Cameron, Potter, Bradford, Carbon, Clinton, Lackawanna, Luzerne, Lycoming, Monroe, Pike, Sullivan, Susquehanna, Tioga, Wayne, Wyoming, Allegheny, Armstrong, Beaver, Butler, Fayette, Greene, Indiana, Lawrence, Washington, Westmoreland, Bedford, Blair, Clearfield, Cambria, Huntingdon, Jefferson, Somerset, Centre"),
    ("UHB", "UPMC Health Benefits, Inc.", "UPMC Health Benefits", True, 12.39, 10.69, 0.14, "Clearfield, Crawford"),
    ("UHN", "UPMC Health Network, Inc.", "UPMC Health Network", True, 11.32, 9.68, 22.63, UHN_SG),
    ("UHP", "UPMC Health Plan, Inc.", "UPMC Health Plan", True, 15.54, 13.85, 2.02, UHN_SG),
]

ind_out = []
for item in raw_individual:
    i, n, s, on_p, rq, ap, sh, c = item
    d = {
        "id": i,
        "name": n,
        "short": s,
        "on_pennie": on_p,
        "req27": rq,
        "app27": ap,
        "share26": sh,
        "counties": "ALL" if c == "ALL" else L(c)
    }
    ind_out.append(d)

hca_2026 = {
    "name": "Highmark Coverage Advantage",
    "req26": 14.06,
    "app26": 14.48,
    "share25": 5.51,
    "note": "Filed individual-market rates for 2026; absent from PID's 2027 individual-market table."
}

raw_small_group = [
    ("CAAC", "Capital Advantage Assurance Company", "Capital Advantage Assurance", 16.11, 16.10, 7.23, CAP_SG),
    ("GHP", "Geisinger Health Plan", "Geisinger Health Plan", 3.74, 2.67, 0.67, GEI_C),
    ("GQO", "Geisinger Quality Options", "Geisinger Quality Options", 4.05, 2.61, 2.03, GEI_C),
    ("HBG", "Highmark Benefits Group", "Highmark Benefits Group", 16.99, 13.31, 6.02, CAP_SG),
    ("HCB", "Highmark Care Benefits", "Highmark Care Benefits", 19.95, 15.99, 1.90, "Bradford, Carbon, Clinton, Lackawanna, Luzerne, Lycoming, Monroe, Pike, Sullivan, Susquehanna, Tioga, Wayne, Wyoming"),
    ("HCA", "Highmark Coverage Advantage", "Highmark Coverage Advantage", 14.63, 10.57, 4.97, "Allegheny, Armstrong, Beaver, Bedford, Blair, Butler, Cambria, Cameron, Centre, Clarion, Clearfield, Columbia, Crawford, Elk, Fayette, Forest, Greene, Huntingdon, Indiana, Jefferson, Lawrence, Lehigh, McKean, Mercer, Mifflin, Montour, Northumberland, Potter, Snyder, Somerset, Union, Venango, Warren, Washington, Westmoreland"),
    ("HSHC", "Highmark Senior Health Company", "Highmark Senior Health", 14.32, 13.13, 2.74, PHI5),
    ("HIG", "Highmark, Inc.", "Highmark, Inc.", 15.57, 11.46, 3.32, HIG_C),
    ("IAC", "Independence Assurance Company", "Independence Assurance", 8.95, 8.95, 22.95, PHI5),
    ("KHPC", "Keystone Health Plan Central", "Keystone Health Plan Central", 20.93, 20.93, 0.02, CAP_SG),
    ("KHPE", "Keystone Health Plan East", "Keystone Health Plan East", 6.48, 6.48, 20.52, PHI5),
    ("UHIC", "UnitedHealthcare Insurance Company", "UnitedHealthcare Ins. Co.", 33.57, 30.55, 2.62, "ALL"),
    ("UHCPA", "UnitedHealthcare of Pennsylvania, Inc.", "UnitedHealthcare of PA", 8.00, 1.84, 0.23, "Crawford, Clarion, Erie, Forest, McKean, Mercer, Venango, Warren, Elk, Cameron, Potter, Bradford, Carbon, Clinton, Lackawanna, Luzerne, Lycoming, Monroe, Pike, Sullivan, Susquehanna, Tioga, Wayne, Wyoming, Allegheny, Armstrong, Beaver, Butler, Fayette, Greene, Indiana, Lawrence, Washington, Westmoreland, Bedford, Blair, Clearfield, Cambria, Huntingdon, Jefferson, Somerset, Centre"),
    ("UHB", "UPMC Health Benefits, Inc.", "UPMC Health Benefits", 12.39, 10.69, 0.14, "Clearfield, Crawford"),
    ("UHN", "UPMC Health Network, Inc.", "UPMC Health Network", 11.32, 9.68, 22.63, UHN_SG),
    ("UHP", "UPMC Health Plan, Inc.", "UPMC Health Plan", 15.54, 13.85, 2.02, UHN_SG),
]

sg_out = []
for item in raw_small_group:
    i, n, s, rq, ap, sh, c = item
    sg_out.append({
        "id": i,
        "name": n,
        "short": s,
        "req27": rq,
        "app27": ap,
        "share26": sh,
        "counties": "ALL" if c == "ALL" else L(c)
    })

term = {
    "Schuylkill": 24, "Lehigh": 22, "Northampton": 22, "Lancaster": 22, "Greene": 22, "Fulton": 22,
    "Tioga": 21, "Monroe": 21, "Franklin": 21, "Juniata": 20, "Mifflin": 20, "Beaver": 20, "Snyder": 20,
    "Adams": 19, "Lebanon": 19, "Carbon": 19, "Blair": 19, "York": 19, "Cumberland": 19, "Clearfield": 19
}

dataset = {
    "meta": {
        "title": "Pennsylvania rating-area dataset, plan year 2027",
        "as_of": ACCESSED,
        "units": "percent unless noted; share = PID-reported market share of the prior year (2026 for 2027 rows, 2025 for 2026 rows)",
        "scope_note": "Descriptive cross-sectional synthesis only; no pooling, no heterogeneity statistics."
    },
    "sources": sources,
    "areas": areas,
    "individual": ind_out,
    "individual_2026_only": hca_2026,
    "small_group": sg_out,
    "terminations_oe2026": {
        "through": "2026-02-01",
        "top20_pct": term,
        "floor_note": "Counties not listed are at or below the list floor (19%)."
    },
    "statewide": {
        "pid_individual_2027_avg_approved": 15.97,
        "pid_small_group_2027_avg_approved": 10.28,
        "reported_individual_2027_avg_requested": 17.1,
        "reported_small_group_2027_avg_requested": 11.5,
        "pid_individual_2026_avg_approved": 21.5,
        "pennie_enrollment": {"2025_peak": 497000, "2026-01-31_oe_close": 486000, "2026-03-24": 471442},
        "open_enrollment_2027": {"start": "2026-11-01", "end": "2027-01-15", "deadline_for_jan1_start": "2026-12-15"}
    },
    "validation": {
        "legacy_area_entities_sep8_reports": {
            "1": ["AHP", "AHS", "HIG", "UHN", "UHP"],
            "2": ["AHP", "AHS", "GHP", "GQO", "HIG", "UHN"],
            "3": ["AHP", "AHS", "GHP", "GQO", "HPP", "HBG", "OSC", "PIC", "UHN"],
            "4": ["AHP", "AHS", "HIG", "UHN"],
            "5": ["AHP", "AHS", "GHP", "GQO", "HIG", "UHN", "UHP"],
            "6": ["AHP", "AHS", "CAAC", "GHP", "GQO", "HPP", "HIG", "KHPC", "OSC", "PIC"],
            "7": ["AHP", "AHS", "CAAC", "GHP", "GQO", "HIG", "KHPC", "OSC"],
            "8": ["AHP", "AHS", "HPP", "HBG", "KHPE", "OSC", "PIC", "QCC"],
            "9": ["AHP", "AHS", "CAAC", "GHP", "GQO", "HIG", "KHPC", "UHN"]
        },
        "pid_stated_areas_individual_2027_request_release": {
            "AHP": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "GHP": [2, 3, 5, 6, 7, 9],
            "HPP": [3, 6, 8],
            "KHPC": [6, 7, 9],
            "KHPE": [8],
            "PIC": [3, 6, 8],
            "QCC": [8],
            "UHP": [1, 5]
        },
        "pid_stated_areas_small_group_2027_request_release": {
            "HSHC": [8],
            "KHPC": [6, 7, 9],
            "KHPE": [8],
            "UHB": [1, 5]
        }
    }
}

# --- Pydantic Schema ---

class CarrierIndividual(BaseModel):
    id: str
    name: str
    short: str
    on_pennie: bool
    req27: float
    app27: float
    share26: float
    counties: List[str]
    req26: Optional[float] = None
    app26: Optional[float] = None
    share25: Optional[float] = None
    note: Optional[str] = None

class CarrierSmallGroup(BaseModel):
    id: str
    name: str
    short: str
    req27: float
    app27: float
    share26: float
    counties: List[str]

class StatewideMetrics(BaseModel):
    pid_individual_2027_avg_approved: float
    pid_small_group_2027_avg_approved: float
    reported_individual_2027_avg_requested: float
    reported_small_group_2027_avg_requested: float
    pid_individual_2026_avg_approved: float
    pennie_enrollment: Dict[str, int]
    open_enrollment_2027: Dict[str, str]

class ValidationLayer(BaseModel):
    legacy_area_entities_sep8_reports: Dict[str, List[str]]
    pid_stated_areas_individual_2027_request_release: Dict[str, List[int]]
    pid_stated_areas_small_group_2027_request_release: Dict[str, List[int]]

class PARADataset(BaseModel):
    meta: Dict[str, str]
    sources: Dict[str, Any]
    areas: Dict[str, List[str]]
    individual: List[CarrierIndividual]
    small_group: List[CarrierSmallGroup]
    statewide: StatewideMetrics
    validation: ValidationLayer
    individual_2026_only: Optional[Dict[str, Any]] = None
    terminations_oe2026: Optional[Dict[str, Any]] = None

def main():
    out_path = Path("data/pa_ra_dataset.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote dataset to {out_path} ({out_path.stat().st_size} bytes)")

    # Validate
    data = json.loads(out_path.read_text(encoding="utf-8"))
    validated = PARADataset(**data)
    print("Validation successful! PARADataset schema verified.")

if __name__ == "__main__":
    main()
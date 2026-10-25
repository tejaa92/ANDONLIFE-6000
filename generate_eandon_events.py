#!/usr/bin/env python3
"""ANDONLIFE-6000: a fully synthetic andon event-lifecycle dataset.

Every record is synthetic. The schema (event categories, lifecycle states,
trigger sources) follows the documented structure of enterprise digital
andon systems: operators raise events manually (kiosk, tablet, HMI) or
machines raise them automatically when monitored conditions/rules fire
(PLC-rule trigger). Timing outcomes are simulated by the documented
functions below (category base times, trigger multipliers, archetype
effects, lognormal noise). The automated share of events rises across the
12 synthetic months as a disclosed modeling choice representing automation
rollout after an API release. No real program data is used anywhere.
Seed 7, Python standard library only.
"""
import csv, json, random, hashlib

random.seed(7)

CATEGORIES = {  # name: (share, base_ack_min, base_resolve_min, base_downtime_min or None)
    "equipment_downtime": (0.30, 6.0, 95.0, 85.0),
    "material_shortage":  (0.16, 8.0, 70.0, None),
    "process_deviation":  (0.14, 9.0, 80.0, None),
    "quality":            (0.13, 10.0, 110.0, None),
    "manpower":           (0.10, 7.0, 45.0, None),
    "station_starvation": (0.09, 5.0, 55.0, None),
    "safety":             (0.08, 3.0, 60.0, None),
}
ARCHETYPES = ["assembly", "machining", "fabrication", "paint_finish"]
ARCH_EFFECT = {"assembly": 1.00, "machining": 1.10, "fabrication": 0.95, "paint_finish": 1.05}
MANUAL_SOURCES = ["kiosk", "tablet", "hmi"]
FACILITIES = [f"F{i:02d}" for i in range(1, 41)]
FAC_ARCH = {f: ARCHETYPES[i % 4] for i, f in enumerate(FACILITIES)}
FAC_SIZE = {f: random.uniform(0.8, 1.3) for f in FACILITIES}

def pick_category():
    r = random.random(); acc = 0.0
    for name, (share, *_rest) in CATEGORIES.items():
        acc += share
        if r <= acc: return name
    return "safety"

def lognorm(median, sigma=0.55):
    return max(0.5, random.lognormvariate(__import__("math").log(median), sigma))

rows = []
N = 6000
for i in range(1, N + 1):
    month = random.randint(1, 12)
    # automated share rises 6% (month 1) to 46% (month 12): disclosed modeling choice
    p_auto = 0.06 + (month - 1) * (0.40 / 11.0)
    trigger = "automated_plc_rule" if random.random() < p_auto else random.choice(MANUAL_SOURCES)
    fac = random.choice(FACILITIES)
    arch = FAC_ARCH[fac]
    cat = pick_category()
    _share, base_ack, base_res, base_down = CATEGORIES[cat]
    trig_ack_mult = 0.45 if trigger == "automated_plc_rule" else 1.0
    trig_res_mult = 0.80 if trigger == "automated_plc_rule" else 1.0
    eff = ARCH_EFFECT[arch] * FAC_SIZE[fac]
    ack = lognorm(base_ack * trig_ack_mult * eff)
    resolve = lognorm(base_res * trig_res_mult * eff)
    close_lag = lognorm(18.0)
    escalated = 1 if (resolve > 120 or cat == "safety" and random.random() < 0.35 or random.random() < 0.08) else 0
    esc_level = 0
    if escalated:
        esc_level = 2 if resolve > 240 else 1
    downtime = round(lognorm(base_down * eff), 1) if base_down else 0.0
    rows.append({
        "event_id": f"EV{i:05d}",
        "facility_id": fac,
        "facility_archetype": arch,
        "month": month,
        "shift": random.choice([1, 2, 3]),
        "category": cat,
        "trigger_source": trigger,
        "ack_minutes": round(ack, 1),
        "resolve_minutes": round(resolve, 1),
        "close_minutes": round(resolve + close_lag, 1),
        "escalated": escalated,
        "escalation_level": esc_level,
        "downtime_minutes": downtime,
        "final_state": "closed",
    })

import os
base = os.path.dirname(os.path.abspath(__file__))
with open(f"{base}/andonlife6000_events.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(f"{base}/andonlife6000_events.json", "w") as fh:
    json.dump(rows, fh, indent=1)
digest = hashlib.sha256(open(f"{base}/andonlife6000_events.csv","rb").read()).hexdigest()
print("rows:", len(rows), "| csv sha256:", digest)
auto = [r for r in rows if r["trigger_source"] == "automated_plc_rule"]
man = [r for r in rows if r["trigger_source"] != "automated_plc_rule"]
import statistics as st
print("automated share:", round(len(auto)/len(rows), 3))
print("mean ack  auto vs manual:", round(st.mean(r['ack_minutes'] for r in auto),1), round(st.mean(r['ack_minutes'] for r in man),1))
print("mean resolve auto vs manual:", round(st.mean(r['resolve_minutes'] for r in auto),1), round(st.mean(r['resolve_minutes'] for r in man),1))
print("escalation rate:", round(sum(r['escalated'] for r in rows)/len(rows), 3))
print("categories:", {c: sum(1 for r in rows if r['category']==c) for c in CATEGORIES})

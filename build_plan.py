#!/usr/bin/env python3
"""Generate public/plan.json: a draft periodized plan from 2 Nov 2026 to the Ironman on 22 Aug 2027.

Athlete profile: strong runner (1:29 half, 3:16 marathon), 6-10 h/week now, trains 6 days (Mon rest).
This is a starting draft; the Sunday recap adjusts it week by week.
"""
import json
from datetime import date, timedelta

START = date(2026, 11, 2)            # Monday
HALF = date(2027, 6, 27)             # Sunday, 70.3
IRON = date(2027, 8, 22)             # Sunday, Ironman

# (name, first Monday, last Monday, start hours, end hours, swim/bike/run split)
PHASES = [
    ("Base 1",            date(2026, 11, 2),  date(2026, 12, 21), 7.0, 9.0,  (0.27, 0.33, 0.40)),
    ("Base 2",            date(2026, 12, 28), date(2027, 2, 15),  9.0, 10.5, (0.23, 0.39, 0.38)),
    ("Build 1",           date(2027, 2, 22),  date(2027, 4, 12),  10.5, 12.5, (0.19, 0.44, 0.37)),
    ("Build 2 (70.3)",    date(2027, 4, 19),  date(2027, 6, 7),   12.5, 13.5, (0.17, 0.47, 0.36)),
    ("70.3 Taper",        date(2027, 6, 14),  date(2027, 6, 14),  8.5, 8.5,   (0.17, 0.47, 0.36)),
    ("70.3 Race Week",    date(2027, 6, 21),  date(2027, 6, 21),  5.0, 5.0,   (0.17, 0.47, 0.36)),
    ("Recovery",          date(2027, 6, 28),  date(2027, 6, 28),  5.0, 5.0,   (0.25, 0.35, 0.40)),
    ("Ironman Peak",      date(2027, 7, 5),   date(2027, 7, 19),  13.5, 15.0, (0.15, 0.50, 0.35)),
    ("Peak Recovery",     date(2027, 7, 26),  date(2027, 7, 26),  10.5, 10.5, (0.16, 0.48, 0.36)),
    ("Ironman Taper",     date(2027, 8, 2),   date(2027, 8, 9),   10.0, 7.0,  (0.17, 0.48, 0.35)),
    ("Ironman Race Week", date(2027, 8, 16),  date(2027, 8, 16),  4.5, 4.5,   (0.20, 0.45, 0.35)),
]

RECOVERY_EVERY = 4   # every 4th week inside Base/Build is a 70% week
RECOVERY_PHASES = {"Base 1", "Base 2", "Build 1", "Build 2 (70.3)"}

FOCUS = {
    "Base 1":  dict(swim="Technique drills + easy aerobic", bike="Easy endurance (Zwift Z2)", run="Easy aerobic, strides", q="Steady aerobic + strides"),
    "Base 2":  dict(swim="Aerobic sets, pull buoy", bike="Sweet-spot intervals", run="Easy aerobic", q="Tempo (marathon effort)"),
    "Build 1": dict(swim="CSS threshold sets", bike="Threshold intervals", run="Easy aerobic", q="Threshold intervals"),
    "Build 2 (70.3)": dict(swim="Race-pace sets, open water if possible", bike="70.3-pace blocks", run="Easy aerobic", q="Half-marathon-pace intervals"),
    "70.3 Taper": dict(swim="Short race-pace", bike="Short sharpening", run="Easy + strides", q="Short race-pace"),
    "70.3 Race Week": dict(swim="Short opener", bike="Short opener", run="Easy shakeout", q="Short opener"),
    "Recovery": dict(swim="Easy", bike="Easy spin", run="Easy", q="Easy with strides"),
    "Ironman Peak": dict(swim="Endurance + race pace", bike="Ironman-pace blocks", run="Easy aerobic", q="Marathon-pace blocks"),
    "Peak Recovery": dict(swim="Easy aerobic", bike="Easy endurance", run="Easy aerobic", q="Steady"),
    "Ironman Taper": dict(swim="Short race-pace", bike="Short sharpening", run="Easy + strides", q="Short race-pace"),
    "Ironman Race Week": dict(swim="Short opener", bike="Short opener", run="Easy shakeout", q="Short opener"),
}

def round5(x):
    return max(20, int(round(x / 5.0)) * 5)

def phase_for(monday):
    for ph in PHASES:
        if ph[1] <= monday <= ph[2]:
            return ph
    return None

def week_hours(ph, monday, idx_in_phase, n_in_phase):
    name, _, _, h0, h1, _ = ph
    h = h0 if n_in_phase <= 1 else h0 + (h1 - h0) * idx_in_phase / (n_in_phase - 1)
    return h

def build():
    weeks, sessions = [], []
    monday = START
    base_counter = 0
    while monday <= IRON - timedelta(days=6):
        ph = phase_for(monday)
        if ph is None:
            monday += timedelta(days=7)
            continue
        name = ph[0]
        n = (ph[2] - ph[1]).days // 7 + 1
        i = (monday - ph[1]).days // 7
        hours = week_hours(ph, monday, i, n)
        is_recovery = False
        if name in RECOVERY_PHASES:
            base_counter += 1
            if base_counter % RECOVERY_EVERY == 0:
                hours *= 0.7
                is_recovery = True
        elif name not in RECOVERY_PHASES:
            base_counter = 0 if name == "Recovery" else base_counter
        swim_f, bike_f, run_f = ph[5]
        swim, bike, run = hours * 60 * swim_f, hours * 60 * bike_f, hours * 60 * run_f
        f = FOCUS[name]
        in_build = name in ("Build 1", "Build 2 (70.3)", "Ironman Peak")
        race = HALF if monday <= HALF <= monday + timedelta(days=6) else (IRON if monday <= IRON <= monday + timedelta(days=6) else None)
        tag = f"{name}" + (" · recovery week" if is_recovery else "")
        day = lambda k: monday + timedelta(days=k)
        S = []

        def add(k, sport, title, mins, intensity):
            S.append(dict(date=day(k).isoformat(), sport=sport, title=title, minutes=round5(mins), intensity=intensity))

        # Mon = rest
        add(1, "swim", f"Swim A: {f['swim']}", swim * 0.40, "easy" if name in ("Base 1", "Recovery") else "moderate")
        add(1, "run", "Easy run", run * (0.20 if in_build else 0.25), "easy")
        add(2, "bike", f"Bike: {f['bike']}", bike * 0.30, "hard" if name not in ("Base 1", "Recovery") else "easy")
        add(3, "run", f"Run: {f['q']}", run * (0.25 if in_build else 0.30), "hard" if name not in ("Recovery", "Peak Recovery") else "easy")
        add(3, "swim", "Swim C: short technique", swim * 0.25, "easy")
        add(4, "swim", f"Swim B: {f['swim']}", swim * 0.35, "moderate")
        add(4, "bike", "Easy spin", bike * 0.15, "easy")
        add(5, "bike", "Long ride" + (" + brick run" if in_build else ""), bike * 0.55, "moderate")
        if in_build:
            add(5, "run", "Brick run off the bike", run * 0.15, "moderate")
        add(6, "run", "Long run", run * (0.40 if in_build else 0.45), "moderate")

        if race:
            # Race week: replace Sunday with the race, make Saturday a short opener, drop the long ride/run
            S = [s for s in S if s["date"] not in (day(5).isoformat(), day(6).isoformat())]
            add(5, "bike", "Opener: 30' easy with 3 x 1' race pace", 40, "easy")
            add(5, "run", "Opener: 10' easy + strides", 20, "easy")
            label = "RACE: Half Ironman (70.3)" if race == HALF else "RACE: IRONMAN"
            S.append(dict(date=day(6).isoformat(), sport="race", title=label, minutes=330 if race == HALF else 690, intensity="race"))
            tag = name

        weeks.append(dict(start=monday.isoformat(), phase=name, label=tag, planned_hours=round(hours, 1), recovery=is_recovery))
        sessions.extend(S)
        monday += timedelta(days=7)
    return weeks, sessions

if __name__ == "__main__":
    weeks, sessions = build()
    plan = dict(
        generated=date(2026, 11, 1).isoformat(),
        races=[
            dict(date=HALF.isoformat(), name="Half Ironman (70.3)", priority="B"),
            dict(date=IRON.isoformat(), name="IRONMAN", priority="A"),
        ],
        weeks=weeks,
        sessions=sessions,
    )
    with open("public/plan.json", "w") as fh:
        json.dump(plan, fh, indent=1)
    print(f"{len(weeks)} weeks, {len(sessions)} sessions")
    for w in weeks:
        tot = sum(s["minutes"] for s in sessions if w["start"] <= s["date"] < (date.fromisoformat(w["start"]) + timedelta(days=7)).isoformat() and s["sport"] != "race")
        print(w["start"], f'{w["label"]:<34} target {w["planned_hours"]:>5}h  scheduled {tot/60:>5.1f}h')

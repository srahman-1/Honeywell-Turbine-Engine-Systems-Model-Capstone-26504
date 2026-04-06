import csv
import json

CSV_FILE = "turbofan_trade_study_results.csv"

data = []

with open(CSV_FILE, "r") as file:
    reader = csv.DictReader(file)

    print("\nDEBUG HEADERS:", reader.fieldnames)

    for row in reader:
        data.append(row)

# weights (from your trade study doc)
weights = {
    "thrust": 7,
    "sfc": 10,
    "eff": 8,
    "design": 7,
    "integration": 5,
    "manufacturing": 5,
    "material": 6,
    "diameter": 6
}

def score_thrust(t):
    return 9 if t > 240 else 7 if t > 200 else 5

def score_sfc(s):
    return 9 if s < 0.5 else 7 if s < 0.6 else 5

def score_eff(e):
    return 9 if e > 0.7 else 7 if e > 0.6 else 5

def score_bpr(b):
    return 8 if b == 2 else 6 if b == 3 else 4

def score_diameter(d):
    return 8 if d < 5 else 6 if d <= 5.5 else 2

results = []

for row in data:
    fuel = row.get("Fuel", "Unknown")
    bpr = float(row.get("BPR", 0))
    thrust = float(row.get("Thrust (N)", 0))
    sfc = float(row.get("SFC (kg/(N h))", 0))
    eff = float(row.get("Total Efficiency", 0))

    # FIX BUG (TIP DIAMETER)
    if row.get("Tip Diameter (in)"):
        tip_dia = float(row["Tip Diameter (in)"])
    elif row.get("Tip Diameter"):
        tip_dia = float(row["Tip Diameter"])
    else:
        tip_dia = 2 * 0.06985 * 39.3701

    scores = {
        "thrust": score_thrust(thrust),
        "sfc": score_sfc(sfc),
        "eff": score_eff(eff),
        "design": score_bpr(bpr),
        "integration": score_bpr(bpr),
        "manufacturing": score_bpr(bpr),
        "material": score_bpr(bpr),
        "diameter": score_diameter(tip_dia)
    }

    total = sum(scores[k] * weights[k] for k in weights)

    results.append([
        fuel, bpr, thrust, sfc, eff, tip_dia, total
    ])

# save
with open("trade_matrix_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Fuel","BPR","Thrust","SFC","Efficiency","TipDia","Score"])
    writer.writerows(results)

best = max(results, key=lambda x: x[-1])

with open("best_design.json", "w") as f:
    json.dump({
        "Fuel": best[0],
        "BPR": best[1],
        "Thrust": best[2],
        "SFC": best[3],
        "Efficiency": best[4],
        "Score": best[6]
    }, f, indent=4)

print("\nBest Design:", best)

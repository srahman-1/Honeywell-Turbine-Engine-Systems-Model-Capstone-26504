import csv
import numpy as np
import matplotlib.pyplot as plt
import json

"""
POST PROCESSING FILE
Uses turbofan_trade_study_results.csv from main model
"""


# Load Data

data = []

with open("turbofan_trade_study_results.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # skip header

    for row in reader:
        data.append([
            row[0],                    # Fuel
            float(row[1]),             # BPR
            float(row[2]),             # FPR
            float(row[3]),             # CPR
            float(row[4]),             # Specific Thrust
            float(row[5]),             # f
            float(row[6]),             # SFC (kg/Ns)
            float(row[7]),             # SFC (kg/Nhr)
            float(row[8]),             # eta_T
            float(row[9]),             # eta_P
            float(row[10]),            # eta_0
            float(row[11])             # Thrust
        ])

print("\nLoaded", len(data), "trade study points")


# Requirement Check

print("\n========== REQUIREMENT CHECK ==========")

thrust_min = 150
thrust_max = 250
sfc_limit = 0.65

def requirement_check(thrust, sfc, bpr):
    return (
        thrust_min <= thrust <= thrust_max and
        sfc <= sfc_limit and
        2 <= bpr <= 4
    )

valid_designs = [row for row in data if requirement_check(row[11], row[7], row[1])]

print("Valid designs:", len(valid_designs))


# Weighted Score

print("\n========== SCORING ==========")

def trade_score(thrust, sfc, eta):
    thrust_score = thrust / 250
    sfc_score = 0.65 / sfc if sfc > 0 else 0
    eta_score = eta
    return 0.4*thrust_score + 0.4*sfc_score + 0.2*eta_score

scored = [(trade_score(row[11], row[7], row[10]), row) for row in data]
best = max(scored, key=lambda x: x[0])

print("\nBest Overall Design:")
print("Fuel:", best[1][0])
print("BPR:", best[1][1])
print("FPR:", best[1][2])
print("CPR:", best[1][3])
print("Thrust:", best[1][11])
print("SFC:", best[1][7])
print("Efficiency:", best[1][10])


# Best Feasible Design

print("\n========== BEST FEASIBLE DESIGN ==========")

if len(valid_designs) > 0:
    best_valid = max(valid_designs, key=lambda x: trade_score(x[11], x[7], x[10]))

    print("Fuel:", best_valid[0])
    print("BPR:", best_valid[1])
    print("FPR:", best_valid[2])
    print("CPR:", best_valid[3])
    print("Thrust:", best_valid[11])
    print("SFC:", best_valid[7])
    print("Efficiency:", best_valid[10])
else:
    print("No feasible designs")


# Save Decision (for review continuity)

decision = {
    "Fuel": best[1][0],
    "BPR": best[1][1],
    "FPR": best[1][2],
    "CPR": best[1][3],
    "Thrust": best[1][11],
    "SFC": best[1][7],
    "Efficiency": best[1][10]
}

with open("design_decision.json", "w") as f:
    json.dump(decision, f, indent=4)

print("\nSaved design_decision.json")


# Plot (Jet A only)

jetA = [row for row in data if row[0] == "Jet A" and row[3] == 6]

plt.figure()
for fpr in sorted(set([row[2] for row in jetA])):
    x = [row[1] for row in jetA if row[2] == fpr]
    y = [row[11] for row in jetA if row[2] == fpr]
    plt.plot(x, y, label=f"FPR={fpr:.2f}")

plt.xlabel("BPR")
plt.ylabel("Thrust")
plt.title("Thrust vs BPR (Jet A, CPR=6)")
plt.grid()
plt.legend()
plt.show()

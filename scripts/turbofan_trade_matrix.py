import csv
import json

"""
WEIGHTED TRADE MATRIX FILE
Reads turbofan_trade_study_results.csv and scores concepts
"""

data = []

with open("turbofan_trade_study_results.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)

weights = {
    "thrust_capability": 7,
    "specific_fuel_consumption": 10,
    "propulsive_efficiency": 8,
    "design_effort": 7,
    "integration_risk": 5,
    "manufacturing_complexity": 5,
    "material_system_impact": 6,
    "fan_diameter_compliance": 6
}

def score_thrust(thrust):
    if thrust >= 240:
        return 9
    if thrust >= 220:
        return 8
    if thrust >= 200:
        return 7
    if thrust >= 180:
        return 6
    return 4

def score_sfc(sfc_hr):
    if sfc_hr <= 0.50:
        return 9
    if sfc_hr <= 0.55:
        return 8
    if sfc_hr <= 0.60:
        return 7
    if sfc_hr <= 0.65:
        return 6
    return 3

def score_eta(eta):
    if eta >= 0.75:
        return 9
    if eta >= 0.65:
        return 8
    if eta >= 0.55:
        return 7
    if eta >= 0.45:
        return 6
    return 4

def score_design_effort(bpr):
    if bpr == 2.0:
        return 8
    if bpr == 3.0:
        return 6
    if bpr == 4.0:
        return 4
    return 5

def score_integration_risk(bpr):
    if bpr == 2.0:
        return 7
    if bpr == 3.0:
        return 5
    if bpr == 4.0:
        return 3
    return 5

def score_manufacturing(bpr):
    if bpr == 2.0:
        return 8
    if bpr == 3.0:
        return 7
    if bpr == 4.0:
        return 6
    return 6

def score_material_impact(bpr):
    if bpr == 2.0:
        return 7
    if bpr == 3.0:
        return 6
    if bpr == 4.0:
        return 4
    return 5

def score_fan_diameter(tip_dia):
    if tip_dia <= 5.0:
        return 8
    if tip_dia <= 5.25:
        return 7
    if tip_dia <= 5.5:
        return 6
    return 2

scored_rows = []

for row in data:
    fuel = row["Fuel"]
    bpr = float(row["BPR"])
    thrust = float(row["Thrust (N)"])
    sfc_hr = float(row["SFC (kg/(N h))"])
    eta = float(row["Total Efficiency"])
    tip_dia = float(row["Tip Diameter (in)"])

    scores = {
        "thrust_capability": score_thrust(thrust),
        "specific_fuel_consumption": score_sfc(sfc_hr),
        "propulsive_efficiency": score_eta(eta),
        "design_effort": score_design_effort(bpr),
        "integration_risk": score_integration_risk(bpr),
        "manufacturing_complexity": score_manufacturing(bpr),
        "material_system_impact": score_material_impact(bpr),
        "fan_diameter_compliance": score_fan_diameter(tip_dia)
    }

    total = sum(scores[k] * weights[k] for k in weights)

    scored_rows.append([
        fuel, bpr, row["FPR"], row["CPR"], thrust, sfc_hr, eta, tip_dia,
        scores["thrust_capability"],
        scores["specific_fuel_consumption"],
        scores["propulsive_efficiency"],
        scores["design_effort"],
        scores["integration_risk"],
        scores["manufacturing_complexity"],
        scores["material_system_impact"],
        scores["fan_diameter_compliance"],
        total
    ])

with open("turbofan_trade_matrix_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Fuel", "BPR", "FPR", "CPR", "Thrust (N)", "SFC (kg/(N h))",
        "Total Efficiency", "Tip Diameter (in)",
        "Score_Thrust", "Score_SFC", "Score_Eta", "Score_DesignEffort",
        "Score_IntegrationRisk", "Score_Manufacturing",
        "Score_MaterialImpact", "Score_FanDiameter", "Weighted_Total"
    ])
    writer.writerows(scored_rows)

best = max(scored_rows, key=lambda x: x[-1])

decision = {
    "Fuel": best[0],
    "BPR": best[1],
    "FPR": best[2],
    "CPR": best[3],
    "Thrust_N": best[4],
    "SFC_kg_per_N_hr": best[5],
    "Total_Efficiency": best[6],
    "Weighted_Total": best[-1]
}

with open("best_trade_decision.json", "w") as file:
    json.dump(decision, file, indent=4)

print("Trade matrix results saved as turbofan_trade_matrix_results.csv")
print("Best trade decision saved as best_trade_decision.json")
print("Best design:", decision)

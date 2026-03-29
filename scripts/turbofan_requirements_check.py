import csv

"""
REQUIREMENTS CHECK FILE
Reads turbofan_trade_study_results.csv and checks requirements
"""

data = []

with open("turbofan_trade_study_results.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)

results = []

for row in data:
    fuel = row["Fuel"]
    bpr = float(row["BPR"])
    fpr = float(row["FPR"])
    cpr = float(row["CPR"])
    opr = float(row["OPR"])
    sfc_hr = float(row["SFC (kg/(N h))"])
    thrust = float(row["Thrust (N)"])
    mdot_corr = float(row["Corrected Mass Flow (kg/s)"])
    tip_dia = float(row["Tip Diameter (in)"])
    htr = float(row["HTR"])

    checks = {
        "SR-4_Thrust_150_to_250_N": 150 <= thrust <= 250,
        "SR-5_SFC_less_than_0_65": sfc_hr < 0.65,
        "SR-7_BPR_2_to_4": 2.0 <= bpr <= 4.0,
        "SR-8_OPR_6_to_10": 6.0 <= opr <= 10.0,
        "SR-14_FPR_1_3_to_1_6": 1.3 <= fpr <= 1.6,
        "SR-15_Corrected_Mass_Flow_0_8_to_1_5": 0.8 <= mdot_corr <= 1.5,
        "SR-16_Fan_Diameter_less_than_5_5_in": tip_dia <= 5.5,
        "SR-16_HTR_0_35_to_0_50": 0.35 <= htr <= 0.50,
    }

    overall_pass = all(checks.values())

    results.append([
        fuel, bpr, fpr, cpr, opr, thrust, sfc_hr, mdot_corr, tip_dia, htr,
        checks["SR-4_Thrust_150_to_250_N"],
        checks["SR-5_SFC_less_than_0_65"],
        checks["SR-7_BPR_2_to_4"],
        checks["SR-8_OPR_6_to_10"],
        checks["SR-14_FPR_1_3_to_1_6"],
        checks["SR-15_Corrected_Mass_Flow_0_8_to_1_5"],
        checks["SR-16_Fan_Diameter_less_than_5_5_in"],
        checks["SR-16_HTR_0_35_to_0_50"],
        overall_pass
    ])

with open("turbofan_requirements_check.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Fuel", "BPR", "FPR", "CPR", "OPR", "Thrust (N)", "SFC (kg/(N h))",
        "Corrected Mass Flow (kg/s)", "Tip Diameter (in)", "HTR",
        "SR-4 Pass", "SR-5 Pass", "SR-7 Pass", "SR-8 Pass",
        "SR-14 Pass", "SR-15 Pass", "SR-16 Diameter Pass", "SR-16 HTR Pass",
        "Overall Pass"
    ])
    writer.writerows(results)

valid = [row for row in results if row[-1] is True]

print("Requirements check file saved as turbofan_requirements_check.csv")
print("Total valid designs:", len(valid))

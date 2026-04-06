import csv

CSV_FILE = "turbofan_trade_study_results.csv"

data = []

with open(CSV_FILE, "r") as file:
    reader = csv.DictReader(file)

    print("\nDEBUG HEADERS:", reader.fieldnames)

    for row in reader:
        data.append(row)

results = []

for row in data:
    fuel = row.get("Fuel", "Unknown")

    bpr = float(row.get("BPR", 0))
    fpr = float(row.get("FPR", 0))
    cpr = float(row.get("CPR", 0))

    # FIX BUG 2 (OPR)
    opr = float(row.get("OPR", cpr))

    sfc_hr = float(row.get("SFC (kg/(N h))", 0))
    thrust = float(row.get("Thrust (N)", 0))
    mdot = float(row.get("Corrected Mass Flow (kg/s)", 0))

    # FIX BUG 1 (TIP DIAMETER)
    if row.get("Tip Diameter (in)"):
        tip_dia = float(row["Tip Diameter (in)"])
    elif row.get("Tip Diameter"):
        tip_dia = float(row["Tip Diameter"])
    else:
        # fallback (from your model)
        tip_dia = 2 * 0.06985 * 39.3701

    htr = float(row.get("HTR", 0.35))

    checks = {
        "Thrust": 150 <= thrust <= 250,
        "SFC": sfc_hr < 0.65,
        "BPR": 2 <= bpr <= 4,
        "OPR": 6 <= opr <= 10,
        "FPR": 1.3 <= fpr <= 1.6,
        "MassFlow": 0.8 <= mdot <= 1.5,
        "Diameter": tip_dia <= 5.5,
        "HTR": 0.35 <= htr <= 0.5
    }

    overall = all(checks.values())

    results.append([
        fuel, bpr, fpr, cpr, opr, thrust, sfc_hr, mdot, tip_dia, htr,
        *checks.values(), overall
    ])

with open("requirements_check.csv", "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Fuel","BPR","FPR","CPR","OPR","Thrust","SFC","MassFlow","TipDia","HTR",
        "ThrustPass","SFCPass","BPRPass","OPRPass","FPRPass","MassFlowPass","DiaPass","HTRPass","Overall"
    ])

    writer.writerows(results)

print("\nRequirements check complete.")
print("Valid designs:", sum(1 for r in results if r[-1]))

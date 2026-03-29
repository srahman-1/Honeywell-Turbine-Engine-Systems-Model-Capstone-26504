from math import sqrt, pi
import numpy as np
import matplotlib.pyplot as plt
import csv

"""
MAIN TURBOFAN ANALYSIS FILE
Generates trade study CSV for post-processing files
"""

"Input Variables"
mass_flow = 0.8
pi_f = 1.3
V_0 = 27
T_0 = 253
y = 1.4
Cp = 1006
h_PR_list = [42.8 * (10 ** 6), 43.17 * (10 ** 6), 43.33 * (10 ** 6)]
fuel_names = ["Jet A", "JP-8", "Jet A1"]
T_t4 = 1923
pi_c = 6
BPR = 2
density = 1.23
fan_tip_radius = 0.06985
HTR = 0.35
Nacelle_radius = 0.0762
r_shaft = 0.008

"Equations"
R = ((y - 1) / y) * Cp
a_0 = sqrt(y * R * T_0)
M_0 = V_0 / a_0

tau_r = 1 + ((y - 1) / 2) * (M_0 ** 2)
tau_lamb = T_t4 / T_0
tau_c = pi_c ** ((y - 1) / y)
tau_f = pi_f ** ((y - 1) / y)

V_9_a0 = sqrt((2 / (y - 1)) * (tau_lamb - tau_r * (tau_c - 1 + BPR * (tau_f - 1)) - tau_lamb / (tau_r * tau_c)))
V_19_a0 = sqrt((2 / (y - 1)) * (tau_r * tau_f - 1))

F_m0 = (a_0 / (1 + BPR)) * (V_9_a0 - M_0 + BPR * (V_19_a0 - M_0))

eta_T = 1 - 1 / (tau_r * tau_c)
eta_P = 2 * M_0 * ((V_9_a0 - M_0 + BPR * (V_19_a0 - M_0)) / (V_9_a0 ** 2 - M_0 ** 2 + BPR * (V_19_a0 ** 2 - M_0 ** 2)))
eta_0 = eta_T * eta_P

"Mass Flow Calculation based on geometry"
fan_inlet_area = pi * (fan_tip_radius ** 2) * (1 - HTR ** 2)
geometry_total_mass_flow = density * V_0 * fan_inlet_area
geometry_fan_mass_flow = (BPR * geometry_total_mass_flow) / (1 + BPR)
geometry_core_mass_flow = geometry_total_mass_flow - geometry_fan_mass_flow

"Mass Flow Calculation based on mass flow"
fan_mass_flow = (BPR * mass_flow) / (1 + BPR)
core_mass_flow = mass_flow - fan_mass_flow

"Uninstalled Thrust based on geometry and mass flow"
F_0_geometry = F_m0 * geometry_total_mass_flow
F_0_mass_flow = F_m0 * mass_flow

"Splitter Radius"
splitter_radius = sqrt((fan_tip_radius ** 2 + BPR * (r_shaft ** 2)) / (BPR + 1))

"Area of core"
A_21 = pi * (splitter_radius ** 2 - r_shaft ** 2)

"Area and Velocity at station 13"
A_13 = pi * (Nacelle_radius ** 2 - splitter_radius ** 2)
V_13_geometry_mass_flow = geometry_fan_mass_flow / (density * A_13)
V_13_mass_flow = fan_mass_flow / (density * A_13)

"Area and Velocity at bypass nozzle exit, station 19"
V_19 = V_19_a0 * a_0
A_19_geometry_velocity = (V_13_geometry_mass_flow * A_13) / V_19
A_19_vcmf = (V_13_mass_flow * A_13) / V_19
M_19 = V_19 / a_0

"Bypass Exit Radius"
r_bypass_nozzle_geometry = sqrt((A_19_geometry_velocity / pi) + splitter_radius ** 2)
r_bypass_nozzle = sqrt((A_19_vcmf / pi) + splitter_radius ** 2)

print("========== SINGLE POINT RESULTS ==========")
for i in range(len(h_PR_list)):
    h_PR = h_PR_list[i]
    fuel_name = fuel_names[i]

    f = ((Cp * T_0) / h_PR) * (tau_lamb - tau_r * tau_c)
    SFC = f / ((1 + BPR) * F_m0)

    print("\nFuel:", fuel_name)
    print("Specific Thrust (N/(kg/s)):", f"{F_m0:.5f}")
    print("Fuel to Air Ratio:", f"{f:.7f}")
    print("SFC (kg/(N s)):", f"{SFC:.8f}")
    print("SFC (kg/(N h)):", f"{SFC * 3600:.5f}")
    print("Total Efficiency:", f"{eta_0:.5f}")
    print("Thrust based on mass flow (N):", f"{F_0_mass_flow:.5f}")
    print("Bypass Nozzle Radius (m):", f"{r_bypass_nozzle:.5f}")

"Trade Study"
BPR_range = np.arange(2.0, 4.01, 0.25)
FPR_range = np.arange(1.3, 1.61, 0.05)
pi_c_range = np.arange(6, 11, 1)

trade_results = []

for fuel_index in range(len(h_PR_list)):
    h_PR = h_PR_list[fuel_index]
    fuel_name = fuel_names[fuel_index]

    for BPR_trade in BPR_range:
        for pi_f_trade in FPR_range:
            for pi_c_trade in pi_c_range:
                R_trade = ((y - 1) / y) * Cp
                a_0_trade = sqrt(y * R_trade * T_0)
                M_0_trade = V_0 / a_0_trade

                tau_r_trade = 1 + ((y - 1) / 2) * (M_0_trade ** 2)
                tau_lamb_trade = T_t4 / T_0
                tau_c_trade = pi_c_trade ** ((y - 1) / y)
                tau_f_trade = pi_f_trade ** ((y - 1) / y)

                core_term_trade = (2 / (y - 1)) * (
                    tau_lamb_trade - tau_r_trade * (tau_c_trade - 1 + BPR_trade * (tau_f_trade - 1))
                    - tau_lamb_trade / (tau_r_trade * tau_c_trade)
                )
                bypass_term_trade = (2 / (y - 1)) * (tau_r_trade * tau_f_trade - 1)

                if core_term_trade <= 0 or bypass_term_trade <= 0:
                    continue

                V_9_a0_trade = sqrt(core_term_trade)
                V_19_a0_trade = sqrt(bypass_term_trade)

                F_m0_trade = (a_0_trade / (1 + BPR_trade)) * (
                    V_9_a0_trade - M_0_trade + BPR_trade * (V_19_a0_trade - M_0_trade)
                )
                f_trade = ((Cp * T_0) / h_PR) * (tau_lamb_trade - tau_r_trade * tau_c_trade)
                SFC_trade = f_trade / ((1 + BPR_trade) * F_m0_trade)

                eta_T_trade = 1 - 1 / (tau_r_trade * tau_c_trade)
                eta_P_trade = 2 * M_0_trade * (
                    (V_9_a0_trade - M_0_trade + BPR_trade * (V_19_a0_trade - M_0_trade)) /
                    (V_9_a0_trade ** 2 - M_0_trade ** 2 + BPR_trade * (V_19_a0_trade ** 2 - M_0_trade ** 2))
                )
                eta_0_trade = eta_T_trade * eta_P_trade

                F_0_mass_flow_trade = F_m0_trade * mass_flow
                tip_diameter_in = 2 * fan_tip_radius * 39.3701
                OPR_trade = pi_c_trade

                trade_results.append([
                    fuel_name, BPR_trade, pi_f_trade, pi_c_trade, OPR_trade,
                    F_m0_trade, f_trade, SFC_trade, SFC_trade * 3600,
                    eta_T_trade, eta_P_trade, eta_0_trade, F_0_mass_flow_trade,
                    mass_flow, tip_diameter_in, HTR
                ])

with open("turbofan_trade_study_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Fuel", "BPR", "FPR", "CPR", "OPR",
        "Specific Thrust (N/(kg/s))", "Fuel-Air Ratio",
        "SFC (kg/(N s))", "SFC (kg/(N h))",
        "Thermal Efficiency", "Propulsive Efficiency", "Total Efficiency",
        "Thrust (N)", "Corrected Mass Flow (kg/s)", "Tip Diameter (in)", "HTR"
    ])
    writer.writerows(trade_results)

print("\nTrade study complete. Results saved as turbofan_trade_study_results.csv")

jetA_plot_cases = [row for row in trade_results if row[0] == "Jet A" and row[3] == 6]

plt.figure()
for fpr_val in FPR_range:
    x_vals = [row[1] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    y_vals = [row[12] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    if len(x_vals) > 0:
        plt.plot(x_vals, y_vals, label=f"FPR={fpr_val:.2f}")
plt.xlabel("Bypass Ratio (BPR)")
plt.ylabel("Thrust (N)")
plt.title("Thrust vs BPR for Jet A at CPR = 6")
plt.grid(True)
plt.legend()
plt.show()

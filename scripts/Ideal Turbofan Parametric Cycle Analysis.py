from math import sqrt, pi
import numpy as np
import matplotlib.pyplot as plt
import csv

"""
Assumptions for Ideal Turbofan Parametric Cycle Analysis
P0=P9=P19
T0=T19
Constant Cp value

Given from RFO
Bypass Ratio (BPR) is 2 to 4
Range: 150 to 250 km
Thrust (F): 150 to 250 N
Specific Fuel Consumption (SFC): SFC<=0.65 kg/(N h)
Fan Polytropic Efficiency = 0.85
N=15000 to 45000 RPM, rotational speed
Hub to Tip Ratio (HTR) = 0.35 to 0.5

Fan Pressure Ratio(FPR or pi_f)
Low Heating Value of Fuel(h_PR)
[Jet A, JP-8, Jet A1] = [42.8,43.17,43.33] Mj/kg
T_t4: burner exit temperature
pi_c: compressor pressure ratio
fan tip radius based on 5.5 inch diameter fan, converted to meters
fuel to air ratio:f
y: ratio of specific heats

Outputs: Specific Thrust, fuel to air ratio, SFC, (eta_T: Thermal, eta_P: Propulsive, eta_0: Total) Efficiency
"""

"Input Variables"
mass_flow = 0.8
pi_f = 1.3
V_0 = 27
T_0 = 253
y = 1.4
Cp = 1006
h_PR_list = [42.8*(10**6), 43.17*(10**6), 43.33*(10**6)]
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
splitter_radius = sqrt((fan_tip_radius**2 + BPR*(r_shaft**2)) / (BPR + 1))

"Area of core, Assuming constant hub to tip ratio"
A_21 = pi * (splitter_radius ** 2 - r_shaft**2)

"Area and Velocity(for geometry and mass flow) at station 13"
A_13 = pi * (Nacelle_radius ** 2 - splitter_radius ** 2)
V_13_geometry_mass_flow = geometry_fan_mass_flow / (density * A_13)
V_13_mass_flow = fan_mass_flow / (density * A_13)

"Area and Velocity at bypass nozzle exit, station 19"
V_19 = V_19_a0 * a_0
A_19_geometry_velocity = (V_13_geometry_mass_flow * A_13) / V_19
A_19_vcmf = (V_13_mass_flow * A_13) / V_19
M_19 = V_19 / a_0

"Bypass Exit Radius"
r_bypass_nozzle_geometry = sqrt((A_19_geometry_velocity/pi) + splitter_radius**2)
r_bypass_nozzle = sqrt((A_19_vcmf/pi) + splitter_radius**2)

print("========== SINGLE POINT RESULTS ==========")
for i in range(len(h_PR_list)):
    h_PR = h_PR_list[i]
    fuel_name = fuel_names[i]

    f = ((Cp * T_0) / h_PR) * (tau_lamb - tau_r * tau_c)
    SFC = f / ((1 + BPR) * F_m0)

    Output_values = [R, a_0, M_0, tau_r, tau_lamb, tau_c, tau_f, V_9_a0, V_19_a0, F_m0, f, SFC, eta_T, eta_P, eta_0,
                     fan_inlet_area, geometry_total_mass_flow, geometry_fan_mass_flow, geometry_core_mass_flow,
                     mass_flow, fan_mass_flow, core_mass_flow, F_0_geometry, F_0_mass_flow,
                     splitter_radius, A_21, A_13, V_13_geometry_mass_flow, V_13_mass_flow, V_19,
                     A_19_geometry_velocity, A_19_vcmf]

    formatted_values = [f"{v:.5f}" for v in Output_values]

    labels = ["Specific Gas Constant (J/kg K):",
              "Speed of Sound (m/s):",
              "Mach Number:",
              "Freestream Total/Static temperature ratio:",
              "Burner Enthalpy Ratio:",
              "Compressor Total Temperature Ratio:",
              "Fan Total Temperature Ratio:",
              "Core Velocity/Speed of Sound Ratio:",
              "Bypass Velocity/Speed of Sound:",
              "Specific Thrust (N/(kg/s)):",
              "Fuel to Air Ratio:",
              "Specific Fuel Consumption (kg/(N s)):",
              "Temperature Efficiency:",
              "Propulsive Efficiency:",
              "Total Efficiency:",
              "Fan Inlet Area (m^2):",
              "Geometry Total Mass Flow (kg/s):",
              "Geometry Fan Mass Flow (kg/s):",
              "Geometry Core Mass Flow (kg/s):",
              "Corrected Total Mass Flow (kg/s):",
              "Corrected Fan Mass Flow (kg/s):",
              "Corrected Core Mass Flow (kg/s):",
              "Thrust based on geometry mass flow (N):",
              "Thrust based on mass flow (N):",
              "Splitter Radius (m):",
              "Area of core (m^2):",
              "Area at station 13 (m^2):",
              "Velocity at station 13 geometry mass flow (m/s):",
              "Velocity at station 13 mass flow (m/s):",
              "Velocity at Station 19, Bypass Nozzle Exit (m/s):",
              "Area of Bypass Nozzle Exit (geometry) (m^2):",
              "Area of Bypass Nozzle Exit (mass flow) (m^2):"]

    print("\nFuel:", fuel_name)
    for x, y_val in zip(labels, formatted_values):
        print(x, y_val)
    print('SFC (kg/(N h)):', f"{SFC*3600:.5f}")
    print('Thrust Ratio:', f"{((V_9_a0-M_0)/(V_19_a0-M_0)):.5f}")
    print('Bypass Nozzle Radius, from center line (geometry) (m):', f"{r_bypass_nozzle_geometry:.5f}")
    print('Bypass Nozzle Radius, from center line (mass flow) (m):', f"{r_bypass_nozzle:.5f}")

"Trade Study"
BPR_range = np.arange(2.0, 4.01, 0.25)
FPR_range = np.arange(1.2, 1.61, 0.05)
pi_c_range = np.arange(4, 11, 1)

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

                core_term_trade = (2 / (y - 1)) * (tau_lamb_trade - tau_r_trade * (tau_c_trade - 1 + BPR_trade * (tau_f_trade - 1)) - tau_lamb_trade / (tau_r_trade * tau_c_trade))
                bypass_term_trade = (2 / (y - 1)) * (tau_r_trade * tau_f_trade - 1)

                if core_term_trade < 0 or bypass_term_trade < 0:
                    continue

                V_9_a0_trade = sqrt(core_term_trade)
                V_19_a0_trade = sqrt(bypass_term_trade)

                F_m0_trade = (a_0_trade / (1 + BPR_trade)) * (V_9_a0_trade - M_0_trade + BPR_trade * (V_19_a0_trade - M_0_trade))
                f_trade = ((Cp * T_0) / h_PR) * (tau_lamb_trade - tau_r_trade * tau_c_trade)
                SFC_trade = f_trade / ((1 + BPR_trade) * F_m0_trade)

                eta_T_trade = 1 - 1 / (tau_r_trade * tau_c_trade)
                eta_P_trade = 2 * M_0_trade * ((V_9_a0_trade - M_0_trade + BPR_trade * (V_19_a0_trade - M_0_trade)) / (V_9_a0_trade ** 2 - M_0_trade ** 2 + BPR_trade * (V_19_a0_trade ** 2 - M_0_trade ** 2)))
                eta_0_trade = eta_T_trade * eta_P_trade

                F_0_mass_flow_trade = F_m0_trade * mass_flow

                trade_results.append([fuel_name, BPR_trade, pi_f_trade, pi_c_trade,
                                      F_m0_trade, f_trade, SFC_trade, SFC_trade * 3600,
                                      eta_T_trade, eta_P_trade, eta_0_trade, F_0_mass_flow_trade])

"CSV Export"
with open("turbofan_trade_study_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Fuel", "BPR", "FPR", "CPR", "Specific Thrust (N/(kg/s))",
                     "Fuel-Air Ratio", "SFC (kg/(N s))", "SFC (kg/(N h))",
                     "Thermal Efficiency", "Propulsive Efficiency",
                     "Total Efficiency", "Thrust (N)"])
    writer.writerows(trade_results)

print("\nTrade study complete. Results saved as turbofan_trade_study_results.csv")

"Best Jet A Case"
jetA_cases = [row for row in trade_results if row[0] == "Jet A"]
best_jetA = min(jetA_cases, key=lambda x: x[7])

print("\n========== BEST JET A CASE ==========")
print("Fuel:", best_jetA[0])
print("Best BPR:", best_jetA[1])
print("Best FPR:", best_jetA[2])
print("Best CPR:", best_jetA[3])
print("Specific Thrust (N/(kg/s)):", f"{best_jetA[4]:.5f}")
print("Fuel-Air Ratio:", f"{best_jetA[5]:.7f}")
print("Minimum SFC (kg/(N h)):", f"{best_jetA[7]:.5f}")
print("Thermal Efficiency:", f"{best_jetA[8]:.5f}")
print("Propulsive Efficiency:", f"{best_jetA[9]:.5f}")
print("Total Efficiency:", f"{best_jetA[10]:.5f}")
print("Thrust (N):", f"{best_jetA[11]:.5f}")

"Plots for Jet A at CPR = 6"
jetA_plot_cases = [row for row in trade_results if row[0] == "Jet A" and row[3] == 6]

plt.figure()
for fpr_val in FPR_range:
    x_vals = [row[1] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    y_vals = [row[11] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    plt.plot(x_vals, y_vals, label=f"FPR={fpr_val:.2f}")
plt.xlabel("Bypass Ratio (BPR)")
plt.ylabel("Thrust (N)")
plt.title("Thrust vs BPR for Jet A at CPR = 6")
plt.grid(True)
plt.legend()
plt.show()

plt.figure()
for fpr_val in FPR_range:
    x_vals = [row[1] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    y_vals = [row[7] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    plt.plot(x_vals, y_vals, label=f"FPR={fpr_val:.2f}")
plt.xlabel("Bypass Ratio (BPR)")
plt.ylabel("SFC (kg/(N h))")
plt.title("SFC vs BPR for Jet A at CPR = 6")
plt.grid(True)
plt.legend()
plt.show()

plt.figure()
for fpr_val in FPR_range:
    x_vals = [row[1] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    y_vals = [row[10] for row in jetA_plot_cases if abs(row[2] - fpr_val) < 1e-9]
    plt.plot(x_vals, y_vals, label=f"FPR={fpr_val:.2f}")
plt.xlabel("Bypass Ratio (BPR)")
plt.ylabel("Total Efficiency")
plt.title("Total Efficiency vs BPR for Jet A at CPR = 6")
plt.grid(True)
plt.legend()
plt.show()

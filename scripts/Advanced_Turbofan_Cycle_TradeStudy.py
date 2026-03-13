import numpy as np
import matplotlib.pyplot as plt
import csv
from dataclasses import dataclass


#SI Units Only

# Bartlett - 26504

# ADVANCED TURBOFAN PARAMETRIC CYCLE MODEL
@dataclass
class Params:
    "The efficiency, pressure, cp_t, gamma_t, h_PR, Tt4 values aren't set in stone"
    Consider_Core_Performance = False
    'Weight in kilograms'
    Weight: float = 8

    #Specific heat ratios and constant pressure specific heat for compressor and turbine
    gamma_c: float = 1.4
    gamma_t: float = 1.33
    cp_c: float = 1006.0
    cp_t: float = 1156.0

    # Ambient conditions
    T0: float = 288.15
    P0: float = 101325.0
    V0: float = 35

    # Efficiencies
    eta_burner: float = 0.9
    eta_mechanical: float = 0.95

    #Polytropic Efficiencies
    polytropic_eff_comp: float = 0.8
    polytropic_eff_fan: float = 0.87
    polytropic_eff_turbine: float = 0.85

    #Total Pressure Ratios
    pi_d_max: float = 0.97
    pi_burner: float = 0.95
    pi_nozzle: float = 1.4
    pi_fan_nozzle: float = 1.2
    pi_fan: float = 1.3
    pi_compressor: float = 4

    # Engine assumptions
    mdot_total: float = 0.71

    'Low Heating Value of fuel Jet-A J/kg [(JP-8:43.17, Jet A1:43.33) <-- MJ/kg]'
    h_PR: float = 42.8 * (10 ** 6)

    'Burner exit temperature'
    Tt4: float = 1070.0
    g: float = 9.81


def total_conditions(T, P, M, gamma):
    Tt = T * (1 + (gamma - 1) / 2 * M ** 2)
    Pt = P * (Tt / T) ** (gamma / (gamma - 1))
    return Tt, Pt


def turbofan_cycle(BPR, p: Params):
    # Specific Gas Constants

    R_c: float = ((p.gamma_c - 1) / p.gamma_c) * p.cp_c
    R_t: float = ((p.gamma_t - 1) / p.gamma_t) * p.cp_t
    # Speed of Sound
    a0: float = np.sqrt(p.gamma_c * R_c * p.T0)
    M0 = p.V0 / a0

    'Checks Mach Number and adjusts the freestream efficiency (π_d=π_d_max*n_r)'
    pi_d = p.pi_d_max * (1 if M0 <= 1 else (1 - 0.075 * (M0 - 1) ** 1.35))

    'Freestream total temp and pressure ratios'
    tau_r = (1 + ((p.gamma_c - 1) / 2) * M0 ** 2)
    pi_r: float = tau_r ** (p.gamma_c / (p.gamma_c - 1))

    'Burner enthalpy ratio'
    tau_lambda = (p.cp_t * p.Tt4) / (p.cp_c * p.T0)

    tau_compressor = p.pi_compressor ** ((p.gamma_c - 1) / (p.gamma_c * p.polytropic_eff_comp))
    eta_compressor = (p.pi_compressor ** ((p.gamma_c - 1) / p.gamma_c) - 1) / (tau_compressor - 1)

    tau_fan: float = p.pi_fan ** ((p.gamma_c - 1) / (p.gamma_c * p.polytropic_eff_fan))
    eta_fan: float = (p.pi_fan ** ((p.gamma_c - 1) / p.gamma_c) - 1) / (tau_fan - 1)

    fuel_air_ratio = (tau_lambda - tau_r * tau_compressor) / (((p.eta_burner * p.h_PR) / (p.cp_c * p.T0)) - tau_lambda)

    tau_turbine: float = 1 - (1 / (p.eta_mechanical * (1 + fuel_air_ratio))) * (tau_r / tau_lambda) * (
                tau_compressor - 1 + BPR * (tau_fan - 1))
    pi_turbine: float = tau_turbine ** (p.gamma_t / ((p.gamma_t - 1) * p.polytropic_eff_turbine))
    eta_turbine = (1 - tau_turbine) / (1 - tau_turbine ** (1 / p.polytropic_eff_turbine))

    def exit_pressure_conditions(pi_r, pi_d, pi_fan, pi_fan_nozzle, pi_compressor, pi_turbine):

        P0_P19_cond: float = (((p.gamma_c + 1) / 2) ** (p.gamma_c / (p.gamma_c - 1))) / (
                    pi_r * pi_d * pi_fan * pi_fan_nozzle)
        P0_P9_cond: float = (((p.gamma_t + 1) / 2) ** (p.gamma_t / (p.gamma_t - 1))) / (
                    pi_r * pi_d * pi_compressor * pi_r * p.pi_burner * pi_turbine * p.pi_nozzle)

        return P0_P19_cond, P0_P9_cond

    P0_P19, P0_P9 = exit_pressure_conditions(pi_r, pi_d, p.pi_fan, p.pi_fan_nozzle, p.pi_compressor, pi_turbine)

    'Checks to see if nozzles are choked'
    P19 = (P0_P19 ** -1) * p.P0
    P9 = (P0_P9 ** -1) * p.P0

    if P19 < p.P0 and P9 > p.P0:
        'P19=P0'
        P0_P19 = 1
    elif P9 < p.P0 and P19 > p.P0:
        'P9=P0'
        P0_P9 = 1
    elif P9 < p.P0 and P19 < p.P0:
        'P19=P0 and P9=P0'
        P0_P9 = 1
        P0_P19 = 1

    OPR=p.pi_compressor*pi_d*pi_r

    return P0_P9, P0_P19, a0, M0, pi_d, tau_r, pi_r, tau_lambda, tau_compressor, tau_fan, fuel_air_ratio, tau_turbine, pi_turbine, R_c, R_t, OPR


def Turbofan_Performance(BPR: float, p: Params):

    P0_P9, P0_P19, a0, M0, pi_d, tau_r, pi_r, tau_lambda, tau_compressor, tau_fan, fuel_air_ratio, tau_turbine, pi_turbine, R_c, R_t, OPR = turbofan_cycle(
        BPR, p)

    'Core Characteristics'
    Pt9_P9 = P0_P9 * pi_r * pi_d * p.pi_compressor * p.pi_burner * pi_turbine * p.pi_nozzle
    M9: float = np.sqrt((2 / (p.gamma_t - 1)) * (Pt9_P9 ** ((p.gamma_t - 1) / p.gamma_t) - 1))
    'Static Temp ratio for core exit to ambient'
    T9_T0 = (tau_lambda * tau_turbine * p.cp_c) / ((Pt9_P9 ** ((p.gamma_t - 1) / p.gamma_t)) * p.cp_t)

    V9_a0 = M9 * np.sqrt(((p.gamma_t * R_t) / (p.gamma_c * R_c)) * T9_T0)


    'Bypass Characteristics'
    Pt19_P19 = P0_P19 * pi_r * pi_d * p.pi_fan * p.pi_fan_nozzle
    M19: float = np.sqrt((2 / (p.gamma_c - 1)) * (Pt19_P19 ** ((p.gamma_c - 1) / p.gamma_c) - 1))
    T19_T0 = (tau_r * tau_fan) / (Pt19_P19 ** ((p.gamma_c - 1) / p.gamma_c))
    V19_a0 = M19 * np.sqrt(T19_T0)

    if p.Consider_Core_Performance == False:
        'Specific Thrust'
        Specific_Thrust: float = ((BPR * a0) / (1 + BPR)) * (V19_a0 - M0 + (T19_T0 / V19_a0) * ((1 - P0_P19) / p.gamma_c))

        'Propulsive Efficiency'
        eta_propulsive = (2 * M0 * (BPR * V19_a0 - (1 + BPR) * M0)) / (BPR * (V19_a0 ** 2) - (1 + BPR) * (M0 ** 2))

        'Thermal Efficiency'
        eta_thermal = ((a0 ** 2) * (BPR * (V19_a0 ** 2) - (1 + BPR) * (M0 ** 2))) / (
                              2 * fuel_air_ratio * p.h_PR)

        'Total Efficiency'
        eta_total = eta_propulsive * eta_thermal

    elif p.Consider_Core_Performance == True:
        'Specific Thrust'
        Specific_Thrust: float = (a0 / (1 + BPR)) * (((1 + fuel_air_ratio) * V9_a0 - M0 + (1 + fuel_air_ratio) * (
                (R_t * T9_T0) / (R_c * V9_a0)) * ((1 - P0_P9) / p.gamma_c)) + ((BPR * a0) / (1 + BPR)) * (
                                                             V19_a0 - M0 + (T19_T0 / V19_a0) * (
                                                             (1 - P0_P19) / p.gamma_c)))

        'Propulsive Efficiency'
        eta_propulsive = (2 * M0 * ((1 + fuel_air_ratio) * V9_a0 + BPR * V19_a0 - (1 + BPR) * M0)) / (
                (1 + fuel_air_ratio) * (V9_a0 ** 2) + BPR * (V19_a0 ** 2) - (1 + BPR) * (M0 ** 2))

        'Thermal Efficiency'
        eta_thermal = ((a0 ** 2) * (
                    (1 + fuel_air_ratio) * (V9_a0 ** 2) + BPR * (V19_a0 ** 2) - (1 + BPR) * (M0 ** 2))) / (
                              2 * fuel_air_ratio * p.h_PR)

        'Total Efficiency'
        eta_total = eta_propulsive * eta_thermal


    SFC: float = fuel_air_ratio / ((1 + BPR) * Specific_Thrust)

    # Compressor
    Tt0, Pt0 = total_conditions(p.T0, p.P0, M0, p.gamma_c)
    Tt2: float = Tt0
    Tt3 = tau_compressor * Tt2
    mdot_core = p.mdot_total / (1 + BPR)

    # Turbine power balance
    Wc = mdot_core * p.cp_c * (Tt3 - Tt2)

    'Thrust to weight ratio'
    tw = Specific_Thrust / p.Weight

    V9 = V9_a0 * a0
    V19 = V19_a0 * a0
    return Specific_Thrust, eta_thermal, eta_propulsive, eta_total, M9, M19, V9_a0, V19_a0, Pt9_P9, Pt19_P19, T9_T0, T19_T0, SFC, tw


def main():
    p = Params()

    BPR_range = np.linspace(2.0, 4.0, 20)

    results = []

    for BPR in BPR_range:
        Specific_Thrust, eta_thermal, eta_propulsive, eta_total, M9, M19, V9_a0, V19_a0, Pt9_P9, Pt19_P19, T9_T0, T19_T0, SFC, tw = Turbofan_Performance(
            BPR, p)
        OPR = turbofan_cycle(BPR, p)[15]

        results.append(
            [BPR, OPR, Specific_Thrust, eta_thermal, eta_propulsive, eta_total, M9, M19, V9_a0, V19_a0, Pt9_P9,
             Pt19_P19, T9_T0, T19_T0, SFC, tw])

    # Save CSV
    with open("Advanced_Turbofan_Trade_Results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["BPR", "OPR", "Specific Thrust (N)", "n_thermal", "n_propulsive", "n_total", "M9", "M19", "V9/a0",
             "V19/a0", "Pt9/P9", "Pt19/P19", "T9/T0", "T19/T0", "SFC", "T/W"])
        writer.writerows(results)

    'Plot functions need to be checked due to above changes'
    # Plot Thrust vs BPR
    thrust_avg = []
    for BPR in BPR_range:
        thrust_vals = [r[2] for r in results if abs(r[0] - BPR) < 1e-6]
        thrust_avg.append(np.mean(thrust_vals))

    plt.figure()
    plt.plot(BPR_range, thrust_avg)
    plt.xlabel("Bypass Ratio (BPR)")
    plt.ylabel("Average Thrust (N)")
    plt.title("Thrust vs BPR")
    plt.grid()
    plt.show()

    print("Trade Study Complete.")
    print("Results saved as Advanced_Turbofan_Trade_Results.csv")


if __name__ == "__main__":
    main()

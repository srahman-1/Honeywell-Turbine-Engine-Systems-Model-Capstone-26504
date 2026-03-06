import numpy as np
import matplotlib.pyplot as plt
import csv
from dataclasses import dataclass

# Bartlett - 26504

# ADVANCED TURBOFAN PARAMETRIC CYCLE MODEL

@dataclass
class Params:
    gamma: float = 1.4
    R: float = 287.0
    cp: float = 1004.0

    # Ambient conditions
    T0: float = 288.15
    P0: float = 101325.0
    M0: float = 0.0

    # Efficiencies
    eta_inlet: float = 0.99
    eta_comp: float = 0.88
    eta_turb: float = 0.90
    eta_noz: float = 0.95

    # Engine assumptions
    mdot_core: float = 1.2
    fuel_air_ratio: float = 0.02
    Tt4: float = 1400.0
    g: float = 9.81

def total_conditions(T, P, M, gamma):
    Tt = T * (1 + (gamma - 1) / 2 * M**2)
    Pt = P * (Tt / T) ** (gamma / (gamma - 1))
    return Tt, Pt

def turbofan_cycle(BPR, OPR, p: Params):

    # Inlet
    Tt0, Pt0 = total_conditions(p.T0, p.P0, p.M0, p.gamma)
    Pt2 = Pt0 * p.eta_inlet
    Tt2 = Tt0

    # Compressor
    Pt3 = Pt2 * OPR
    tau_c = OPR ** ((p.gamma - 1) / p.gamma)
    Tt3 = Tt2 * (1 + (tau_c - 1) / p.eta_comp)

    # Turbine power balance
    Wc = p.mdot_core * p.cp * (Tt3 - Tt2)
    delta_T_turb = Wc / (p.mdot_core * p.cp)
    Tt5 = p.Tt4 - delta_T_turb / p.eta_turb

    # Nozzle exit velocity
    Te = 0.9 * Tt5
    Ve = np.sqrt(2 * p.eta_noz * p.cp * (Tt5 - Te))

    mdot_total = p.mdot_core * (1 + BPR)
    thrust = mdot_total * Ve
    tsfc = (p.fuel_air_ratio * p.mdot_core) / thrust
    tw = thrust / (mdot_total * p.g)

    return thrust, tsfc, tw

def main():
    p = Params()

    BPR_range = np.linspace(2.0, 4.0, 20)
    OPR_range = np.linspace(6.0, 10.0, 20)

    results = []

    for BPR in BPR_range:
        for OPR in OPR_range:
            thrust, tsfc, tw = turbofan_cycle(BPR, OPR, p)
            results.append([BPR, OPR, thrust, tsfc, tw])

    # Save CSV
    with open("Advanced_Turbofan_Trade_Results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["BPR", "OPR", "Thrust (N)", "TSFC", "T/W"])
        writer.writerows(results)

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

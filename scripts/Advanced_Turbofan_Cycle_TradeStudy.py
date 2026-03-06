import numpy as np
import matplotlib.pyplot as plt
import csv
from dataclasses import dataclass

#SI Units Only

# Bartlett - 26504

# ADVANCED TURBOFAN PARAMETRIC CYCLE MODEL

@dataclass
class Params:
    Weight:float=8
    #Specific heat ratios and constant pressure specific heat for compressor and turbine
    gamma_c: float = 1.4
    gamma_t: float = 1.33
    cp_c: float = 1006.0
    cp_t: float = 1156.0

    # Ambient conditions
    T0: float = 288.15
    P0: float = 101325.0
    V0: float = 27.78

    # Efficiencies
    'Placeholder values'
    eta_burner:float=1
    eta_mechanical:float=1

    #Polytropic Efficiencies
    'PlaceHolder values'
    polytropic_eff_comp:float=1
    polytropic_eff_fan:float=1
    polytropic_eff_turbine:float=1

    #Total Pressure Ratios
    'Placeholder values'
    pi_d_max:float=1
    pi_burner:float=1
    pi_nozzle:float=1
    pi_fan_nozzle:float=1
    pi_fan:float=1


    # Engine assumptions
    mdot_total: float = 1.2
    'Low Heating Value of fuel Jet-A J/kg [(JP-8:43.17, Jet A1:43.33) <-- MJ/kg]'
    h_PR:float=42.8*(10**6)
    'Burner exit temperature'
    Tt4: float = 1070.0
    g: float = 9.81

def total_conditions(T, P, M, gamma):
    Tt = T * (1 + (gamma - 1) / 2 * M**2)
    Pt = P * (Tt / T) ** (gamma / (gamma - 1))
    return Tt, Pt

def turbofan_cycle(BPR, pi_compressor, p: Params):
    # Specific Gas Constants
    global eta_r
    global P0_P19
    global P0_P9
    R_c = ((p.gamma_c - 1) / p.gamma_c) * p.cp_c
    R_t = ((p.gamma_t - 1) / p.gamma_t) * p.cp_t
    # Speed of Sound
    a0 = np.sqrt(p.gamma_c * R_c * p.T0)
    M0=p.V0/a0

    'Checks Mach Number and adjusts to proper freestream efficiency'
    if M0<1:
        eta_r=1
    elif M0>1:
        eta_r=1-0.075*(M0-1)**1.35

    pi_d=p.pi_d_max*eta_r

    'Freestream total temp and pressure ratios'
    tau_r=(1+((p.gamma_c-1)/2)*M0**2)
    pi_r=tau_r**(p.gamma_c/(p.gamma_c-1))

    'Burner enthalpy ratio'
    tau_lambda=(p.cp_t*p.Tt4)/(p.cp_c*p.T0)

    tau_compressor=pi_compressor**((p.gamma_c-1)/(p.gamma_c*p.polytropic_eff_comp))
    eta_compressor=(pi_compressor**((p.gamma_c-1)/p.gamma_c)-1)/(tau_compressor-1)

    tau_fan=p.pi_fan**((p.gamma_c-1)/(p.gamma_c*p.polytropic_eff_fan))
    eta_fan=(p.pi_fan**((p.gamma_c-1)/p.gamma_c)-1)/(tau_fan-1)

    fuel_air_ratio=(tau_lambda-tau_r*tau_compressor)/(((p.eta_burner*p.h_PR)/(p.cp_c*p.T0))-tau_lambda)

    tau_turbine=1-(1/(p.eta_mechanical*(1+fuel_air_ratio)))*(tau_r/tau_lambda)*(tau_compressor-1+BPR*(tau_fan-1))
    pi_turbine=tau_turbine**(p.gamma_t/((p.gamma_t-1)*p.polytropic_eff_turbine))
    eta_turbine=(1-tau_turbine)/(1-tau_turbine**(1/p.polytropic_eff_turbine))

    def exit_pressure_conditions(pi_r,pi_d,pi_fan,pi_fan_nozzle,pi_compressor,pi_turbine):

        P0_P19_cond=(((p.gamma_c+1)/2)**(p.gamma_c/(p.gamma_c-1)))/(pi_r*pi_d*pi_fan*pi_fan_nozzle)
        P0_P9_cond=(((p.gamma_t+1)/2)**(p.gamma_t/(p.gamma_t-1)))/(pi_r*pi_d*pi_compressor*pi_r*p.pi_burner*pi_turbine*p.pi_nozzle)

        return P0_P19_cond, P0_P9_cond

    P0_P19, P0_P9=exit_pressure_conditions(pi_r,pi_d,p.pi_fan,p.pi_fan_nozzle,pi_compressor,pi_turbine)

    'Checks to see if nozzles are choked'
    P19 = (P0_P19 ** -1) * p.P0
    P9 = (P0_P9 ** -1) * p.P0

    if P19<p.P0 and P9>p.P0:
        'P19=P0'
        P0_P19=1
    elif P9<p.P0 and P19>p.P0:
        'P9=P0'
        P0_P9=1
    elif P9<p.P0 and P19<p.P0:
        'P19=P0 and P9=P0'
        P0_P9=1
        P0_P19=1

    'Core Characteristics'
    Pt9_P9=P0_P9*pi_r*pi_d*pi_compressor*p.pi_burner*pi_turbine*p.pi_nozzle
    M9=np.sqrt((2/(p.gamma_t-1))*(Pt9_P9**((p.gamma_t-1)/p.gamma_t)-1))
    'Static Temp ratio for core exit to ambient'
    T9_T0=(tau_lambda*tau_turbine*p.cp_c)/((Pt9_P9**((p.gamma_t-1)/p.gamma_t))*p.cp_t)

    V9_a0=M9*np.sqrt(((p.gamma_t*R_t)/(p.gamma_c*R_c))*T9_T0)
    'Bypass Characteristics'
    Pt19_P19=P0_P19*pi_r*pi_d*p.pi_fan*p.pi_fan_nozzle
    M19 = np.sqrt((2 / (p.gamma_c - 1)) * (Pt19_P19 ** ((p.gamma_c - 1) / p.gamma_c) - 1))
    T19_T0=(tau_r*tau_fan)/(Pt19_P19**((p.gamma_c-1)/p.gamma_c))
    V19_a0=M19*np.sqrt(T19_T0)

    'Specific Thrust, F/(total mass flow)'
    Specific_Thrust=(a0/(1+BPR))*(((1+fuel_air_ratio)*V9_a0-M0+(1+fuel_air_ratio)*((R_t*T9_T0)/(R_c*V9_a0))*((1-P0_P9)/p.gamma_c))+((BPR*a0)/(1+BPR))*(V19_a0-M0+(T19_T0/V19_a0)*((1-P0_P19)/p.gamma_c)))

    SFC=fuel_air_ratio/((1+BPR)*Specific_Thrust)

    'Propulsive Efficiency'
    eta_propulsive=(2*M0*((1+fuel_air_ratio)*V9_a0+BPR*V19_a0-(1+BPR)*M0))/((1+fuel_air_ratio)*(V9_a0**2)+BPR*(V19_a0**2)-(1+BPR)*(M0**2))

    'Thermal Efficiency'
    eta_thermal=((a0**2)*((1+fuel_air_ratio)*(V9_a0**2)+BPR*(V19_a0**2)-(1+BPR)*(M0**2)))/(2*fuel_air_ratio*p.h_PR)

    'Total Efficiency'
    eta_total=eta_propulsive*eta_thermal


    # Compressor
    Tt0, Pt0=total_conditions(p.T0,p.P0,M0,p.gamma_c)
    Tt2=Tt0
    Tt3=tau_compressor*Tt2
    mdot_core=p.mdot_total/(1+BPR)

    # Turbine power balance
    Wc = mdot_core * p.cp_c * (Tt3 - Tt2)

    'Thrust to weight ratio'
    tw = Specific_Thrust / p.Weight

    V9=V9_a0*a0
    V19=V19_a0*a0
    'needs to return Specific_Thrust, (Thermal, propulsive, & total efficiency), Mach 9 and 19, V19_a0, V9_a0, Pt19/P19, Pt9/P9, SFC'
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

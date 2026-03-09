from math import sqrt, pi

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
h_PR = 42.8*(10**6)
T_t4 = 1923
pi_c = 6
BPR = 2
density = 1.23
fan_tip_radius = 0.06985
HTR = 0.35
Nacelle_radius = 0.0762
r_shaft=0.008

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

f = ((Cp * T_0) / h_PR) * (tau_lamb - tau_r * tau_c)

SFC = f / ((1 + BPR) * F_m0)

eta_T = 1 - 1 / (tau_r * tau_c)
eta_P = 2 * M_0 * ((V_9_a0 - M_0 + BPR * (V_19_a0 - M_0)) / (V_9_a0 ** 2 - M_0 ** 2 + BPR * (V_19_a0 ** 2 - M_0 ** 2)))
eta_0 = eta_T * eta_P

"Mass Flow Calculation based on geometry, Doesn't display"
fan_inlet_area = pi * (fan_tip_radius ** 2) * (1 - HTR ** 2)

'''
geometry_total_mass_flow = density * V_0 * fan_inlet_area
geometry_fan_mass_flow = (BPR * geometry_total_mass_flow) / (1 + BPR)
geometry_core_mass_flow = geometry_total_mass_flow - geometry_fan_mass_flow
'''

"Mass Flow Calculation based on  mass flow"
fan_mass_flow = (BPR * mass_flow) / (1 + BPR)
core_mass_flow = mass_flow - fan_mass_flow

"Uninstalled Thrust based on geometry and  mass flow"
#F_0_geometry = F_m0 * geometry_total_mass_flow #doesn't display
F_0_mass_flow = F_m0 * mass_flow

"Splitter Radius"
splitter_radius = sqrt((fan_tip_radius**2+BPR*(r_shaft**2))/(BPR+1))

"Area of core, Assuming constant hub to tip ratio"
A_21 = pi * (splitter_radius ** 2 - r_shaft**2)

"Area and Velocity(for geometry and  mass flow) at station 13"
A_13 = pi * (Nacelle_radius ** 2 - splitter_radius ** 2)
#V_13_geometry_mass_flow = geometry_fan_mass_flow / (density * A_13) #doesn't display
V_13_mass_flow = fan_mass_flow / (density * A_13)

"Area and Velocity at bypass nozzle exit, station 19 (vcmf: Velocity  mass flow)"
V_19 = V_19_a0 * a_0
#A_19_geometry_velocity = (V_13_geometry_mass_flow * A_13) / V_19 #doesn't display
A_19_vcmf = (V_13_mass_flow * A_13) / V_19
M_19 = V_19 / a_0

"Bypass Exit Radius"
r_bypass_nozzle=sqrt((A_19_vcmf/pi)+splitter_radius**2)

Output_values = [R, a_0, M_0, tau_r, tau_lamb, tau_c, tau_f, V_9_a0, V_19_a0, F_m0, f, SFC, eta_T, eta_P, eta_0,
                 fan_inlet_area, mass_flow,
                 fan_mass_flow, core_mass_flow, F_0_mass_flow,
                 splitter_radius, A_21, A_13, V_13_mass_flow, V_19,
                 A_19_vcmf]

'Limits decimal precision to 4 for each value'
formatted_values = [f"{v:.5f}" for v in Output_values]

labels = ["Specific Gas Constant (J/kg K):",
          "Speed of Sound (m/s):",
          "Mach Number:",
          "Freestream Total/Static temperature ratio",
          "Burner Enthalpy Ratio:",
          "Compressor Total Temperature Ratio:",
          "Fan Total Temperature Ratio:",
          "Core Velocity/Speed of Sound Ratio:",
          "Bypass Velocity/Speed of Sound:",
          "Specific Thrust (N/(kg/s)):",
          "Fuel to Air Ratio:",
          "Specific Fuel Consumption (kg/(N s)):",
          "Temperature Efficiency",
          "Propulsive Efficiency:",
          "Total Efficiency:",
          "Fan Inlet Area (m^2):",
          " total mass flow values (kg/s):",
          " fan mass flow values (kg/s):",
          " core mass flow values (kg/s) :",
          "Thrust based on  mass flow (N):",
          "Splitter Radius (m):",
          "Area of core (m^2):",
          "Area at station 13 (inlet to bypass duct) (m^2):",
          "Velocity at station 13 based on  mass flow (m/s):",
          "Velocity at Station 19, Bypass Nozzle Exit (m/s):",
          "Area of Bypass Nozzle Exit ( mass flow) (m^2):"]
for x, y in zip(labels, formatted_values):
    print(x, y)
print('Bypass Nozzle Radius, from center line ( mass flow) (m): ',r_bypass_nozzle)
"""
print("Specific Gas Constant: ", "\nSpeed of Sound:", "\nMach Number:",
      "\nFreestream Total/Static temperature ratio", "\nBurner Enthalpy Ratio:",
      "\nCompressor Total Temperature Ratio:", "\nFan Total Temperature Ratio:",
      "\nCore Velocity/Speed of Sound Ratio:", "\nBypass Velocity/Speed of Sound:",
      "\nSpecific Thrust:", "\nFuel to Air Ratio:", "\nSpecific Fuel Consumption:",
      "\nTemperature Efficiency", "\nPropulsive Efficiency:", "\nTotal Efficiency:",
      "\nFan Inlet Area:", "\nGeometry Total Mass Flow Values:",
      "\nGeometry Fan Mass Flow Values:", "\nGeometry Core Mass Flow Values:",
      "\n total mass flow values (total, fan, core):", "\n fan mass flow values:",
      "\n core mass flow values ",
      "\nThrust based on geometry mass flow:", "\nThrust based on  mass flow:",
      "\nSplitter Radius:", "\nArea of core:", "\nArea at station 13 (inlet to bypass duct):",
      "\nVelocity based on geometry mass flow:", "\nVelocity based on  mass flow:",
      "\nVelocity at Station 19, Bypass Nozzle Exit:",
      "\nArea of Bypass Nozzle Exit (geometry mass flow):", "\nArea of Bypass Nozzle Exit ( mass flow):")
"""

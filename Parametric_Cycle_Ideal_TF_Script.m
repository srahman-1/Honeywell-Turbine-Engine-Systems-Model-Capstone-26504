clear;clc;
%Assumptions
%P0=P9=P19
%T_0=T_19
%constant cp value
%Constant hub radius for entire length of turbofan

% %Given from RFP
% %BPR is 2 to 4, Bypass Ratio
% Range=150:250; %Range km
% F=150:250; %Thrust Newtons
% %SFC<=0.65; %Specific fuel consumption kg/(N h)
% fan_polytropic_efficiency=0.85;
% N=15000:100:45000; %rotational speed 
% HTR=0.35:0.1:0.5; %Hub to Tip ratio

corrected_mass_flow=0.8; %corrected mass flow kg/s (0.8:1.5)
V_0=27; %100km/h to 150km/h rounded converted to m/s, freestream velocity.
FPR=1.3; %Fan pressure ratio, typically denoted pi_f

%Input Parameters
T_0=253; %Freestream static temperature, Kelvin (-20C to +50C, operating range)
y=1.4; %Specific heat ratio, 1.4 for subsonic flow
cp=1006; %constant pressure specific heat, varies 1.006 to 1.007 for -20C to +50C temp range J/(kg K)

hPR=[42.8 43.17 43.33]; %Low heating value of fuel, MJ/kg, for [Jet A, JP-8, Jet A1]
T_t4=1923; %Burner exit stagnation temperature, K, based off avergae lean combustion temp. 1650C=1923
pi_c=6; %compressor total pressure ratio, set the same as OPR(overall pressure ratio)

pi_f=FPR; %Fan total pressure ratio
BPR=2; %Bypass ratio, ratio of mass flow through fan over mass flow through core
density=1.23; %density kg/m^3, varies with altitude, pressure, and temp.

fan_tip_radius=0.06985; %use meters, based off a 5.5 inch diameter fan
hub_to_tip_ratio=0.35;
Nacelle_radius=0.0762; %measured right after the fan at station 13, used to calculate bypass entrance area A_13

%Outputs: specific thrust, fuel to air ratio, SFC, (thermal, propulsive,total) efficency, Thrust ratio

%To test tensor aspect I used the following vectors
%(27:42),(6:10),(1.3:0.1:1.6),(253:323),(6:10),(2:4)for V_0, OPR(pi_c), FPR, T_0,pi_c, BPR respectively
%Tensor analysis is potentially uneeded

%Equations
R=((y-1)/y).*cp; %specific gas constant J/(kg K)


%for singular values of BPR,FPR,T_0,V_0, and pi_c
a_0=sqrt(y.*R.*T_0);%freestream speed of sound m/s
M_0=V_0./a_0; %freestream mach

tau_r=1+((y-1)/2).*(M_0.^2); %freestream total/static temperature ratio
tau_lamb=T_t4./T_0; %ratio of burner exit enthalpy to ambient enthalpy
tau_c=(pi_c).^((y-1)/y); %compressure stagnation(total) temperature ratio
tau_f=(pi_f).^((y-1)/y); %fan stagnation(total) temperature ratio

V_9_a0=sqrt((2/(y-1)).*(tau_lamb-tau_r.*(tau_c-1+BPR.*(tau_f-1))-(tau_lamb./(tau_r.*tau_c)))); %core velocity ratio
V_19_a0=sqrt((2/(y-1)).*(tau_r.*tau_f-1)); %bypass exit velocity

F_m0=(a_0./(1+BPR)).*(V_9_a0-M_0+BPR.*(V_19_a0-M_0)); %specific thrust, uninstalled thrust over total mass flow rate

f=((cp.*T_0)./(hPR.*(10^6))).*(tau_lamb-tau_r.*tau_f); %fuel to air ratio
SFC=f./((1+BPR).*F_m0); %specific fuel consumption, units would be (kg/s)/N

eta_T=1-1./(tau_r.*tau_c); %thermal efficiency, (eta is n looking character)
eta_P=2.*M_0.*((V_9_a0-M_0+BPR.*(V_19_a0-M_0))./(V_19_a0.^2-M_0.^2+BPR.*(V_19_a0.^2-M_0.^2))); %Propulsive efficiency
eta_O=eta_T.*eta_P; %Total efficency

FR=(V_9_a0-M_0)./(V_19_a0-M_0); %Thrust ratio, the ratio of specific thrust per unit mass flow of the core stream to that of the fan stream

%mass flow calculation based on geometry 
fan_inlet_area=pi*(fan_tip_radius^2)*(1-hub_to_tip_ratio^2); %m^2, fan area including hub to tip ratio
geometry_total_mass_flow=density*V_0*fan_inlet_area; %kg/s
geometry_fan_mass_flow=(BPR*geometry_total_mass_flow)/(1+BPR);
geometry_core_mass_flow=geometry_total_mass_flow-geometry_fan_mass_flow;

%mass flow calculation based on corrected mass flow
corrected_fan_mass_flow=(BPR*corrected_mass_flow)/(1+BPR);
corrected_core_mass_flow=corrected_mass_flow-corrected_fan_mass_flow;

%uninstalled thrust
F_0=[F_m0*geometry_total_mass_flow F_m0*corrected_mass_flow]; %Newtons

%the radius of the splitter, seperates the core from bypass
splitter_radius=fan_tip_radius*sqrt(((1-hub_to_tip_ratio^2)/BPR)+hub_to_tip_ratio^2); %in meters

%Area of the core taking into consideration hub(assuming constant hub radius)
A_21=pi*(splitter_radius^2-((hub_to_tip_ratio*fan_tip_radius)^2)); %in meters^2

%Area and velocity at station 13
A_13=pi*(Nacelle_radius^2-splitter_radius^2); %in meters^2
V_13=[geometry_fan_mass_flow/(density*A_13) corrected_fan_mass_flow/(density*A_13)];

%Area and velocity at bypass nozzle exit
V_19=V_19_a0.*a_0;
A_19=(V_13.*A_13)./V_19; %in meters^2
M_19=V_19/a_0;
%M_19 is the V_19/a_0 value since T_0=T_19

%Bypass nozzle exit radius measured from the center line of turbofan
%A_19=pi(bypass_nozzle_radius^2-splitter_radius^2) rearranged
bypass_nozzle_radius=sqrt((A_19/pi)+splitter_radius^2);

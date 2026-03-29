from math import pi
import numpy as np
import matplotlib.pyplot as plt
import csv

"""
TIP SPEED ANALYSIS FILE
Checks RPM and tip speed limits
"""

fan_tip_radius = 0.06985
T_0 = 253
y = 1.4
Cp = 1006

R = ((y - 1) / y) * Cp
a_0 = (y * R * T_0) ** 0.5

RPM_range = np.arange(15000, 45001, 2500)
rows = []

for rpm in RPM_range:
    omega = 2 * pi * rpm / 60
    tip_speed = omega * fan_tip_radius
    tip_mach = tip_speed / a_0
    pass_tip_speed = tip_speed < 350.0
    pass_rpm = 15000 <= rpm <= 45000

    rows.append([rpm, omega, tip_speed, tip_mach, pass_tip_speed, pass_rpm])

with open("turbofan_tip_speed_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["RPM", "Omega (rad/s)", "Tip Speed (m/s)", "Tip Mach", "Tip Speed Pass", "RPM Pass"])
    writer.writerows(rows)

print("Tip speed results saved as turbofan_tip_speed_results.csv")

for row in rows:
    print(
        "RPM:", row[0],
        "Omega:", f"{row[1]:.2f}",
        "Tip Speed:", f"{row[2]:.2f}",
        "Tip Mach:", f"{row[3]:.3f}",
        "Tip Speed Pass:", row[4]
    )

plt.figure()
plt.plot([row[0] for row in rows], [row[2] for row in rows])
plt.axhline(350.0, linestyle="--")
plt.xlabel("RPM")
plt.ylabel("Tip Speed (m/s)")
plt.title("Blade Tip Speed vs RPM")
plt.grid(True)
plt.show()

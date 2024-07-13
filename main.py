import math
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import compenents as comps

# component dimensions
panel_volume = 1  # m^3
tank_volume = 3  # m^3

# Components
panel_water = comps.Water()
tank_water = comps.Water()
sun = comps.Sun()
solar_panel = comps.SolarPanel(panel_volume,panel_water)
tank = comps.Tank(tank_volume, tank_water)

# Lists to store simulation results
panel_temperatures = []
tank_temperatures = []
solar_energy = []

# Simulation parameters
hours = 24
time_step = hours * 3600  # seconds

# Simulation loop in seconds
for i in range(time_step):
    if i < time_step / 4 or i > 3 * time_step / 4:
        sun.irradiance = 0
    else:
        t_max = time_step / 4  # time of solar noon after sunrise (in seconds)
        sun.irradiance = sun.max_irradiance * math.sin((2 * math.pi / time_step) * (i - t_max))

    # update components
    solar_energy.append(sun.irradiance)
    # heat gain
    solar_panel.fluid.update_temperature(sun.irradiance, solar_panel.fluid.mass(solar_panel.volume))
    
    # heat loss
    solar_panel.fluid.temperature -= solar_panel.heat_loss()
    tank.fluid.temperature -= tank.heat_loss()

    # store temperatures
    panel_temperatures.append(solar_panel.fluid.temperature)
    tank_temperatures.append(tank.fluid.temperature)


# Create the plot
x = range(time_step)  # time
panel_color = "red"
tank_color = "blue"
sun_color = "orange"
fig, ax = plt.subplots()
ax.plot(x, panel_temperatures, label="Panel Fluid Temp", color = panel_color)
ax.plot(x, tank_temperatures, label="Tank Fluid Temp", color = tank_color)
ax.set_title("Solar Water Heating Simulation")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Temperature (°C)")
ax.tick_params(axis="y")

ax2 = ax.twinx()

ax2.set_ylabel("Irradiance (W/m^2)", color = sun_color)
ax2.plot(x, solar_energy, label="Irradiance", color = sun_color)
ax2.tick_params(axis="y", labelcolor = sun_color)

ax.legend(loc="upper right")
ax2.legend(loc="upper left")
plt.show()



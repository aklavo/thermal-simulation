import math
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import compenents as comps

# component dimensions
panel_volume = 1  # m^3
tank_volume = 3  # m^3
flow_rate = 0.01 # kg/s

# Components
panel_water = comps.Water(26.6667) # Outside ambient air temperature 80°F
tank_water = comps.Water(21.1111) # Inside ambient air temperature 70°F
sun = comps.Sun()
panel = comps.SolarPanel(panel_volume,panel_water)
tank = comps.Tank(tank_volume, tank_water)

# Lists to store simulation results
panel_temperatures = []
panel_energy = []
tank_temperatures = []
tank_energy = []
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
    panel.fluid.update_temperature(sun.irradiance, panel.fluid.mass(panel.volume))
    
    # heat loss
    panel.fluid.temperature -= panel.heat_loss()
    tank.fluid.temperature -= tank.heat_loss()

    # piping/moving the fluid
    # into the tank
    panel.volume -= flow_rate
    panel_tank_temp_delta =  panel.fluid.temperature - tank.fluid.temperature
    energy_into_tank = tank.fluid.energy(panel_tank_temp_delta, flow_rate)

    tank.volume += flow_rate
    tank.fluid.update_temperature(energy_into_tank, tank.fluid.mass(tank.volume))

    # out of the tank
    tank.volume -= flow_rate
    tank_panel_temp_delta =   tank.fluid.temperature - panel.fluid.temperature
    energy_out_of_tank = panel.fluid.energy(tank_panel_temp_delta, flow_rate)

    panel.volume += flow_rate
    panel.fluid.update_temperature(energy_out_of_tank, panel.fluid.mass(panel.volume))



    # store temperatures
    panel_temperatures.append(panel.fluid.temperature)
    tank_temperatures.append(tank.fluid.temperature)





############ Create the plot ##############
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



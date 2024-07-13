import math
import matplotlib

matplotlib.use("TkAgg") # To show plots in Ubuntu
import matplotlib.pyplot as plt
import compenents as comps
import inputs

# System constants
flow_rate = 0.005 # kg/s

# Components
panel_water = comps.Water(26.6667) # Outside ambient air temperature 80°F
tank_water = comps.Water(21.1111) # Inside ambient air temperature 70°F
sun = comps.Sun()
panel = comps.SolarPanel(panel_water)
tank = comps.Tank(tank_water)

# Lists to store simulation results
panel_temperatures = []
panel_energy = []
tank_temperatures = []
tank_energy = []
solar_energy = []
energy_into_tank_list = []
energy_out_of_tank_list = []

# Simulation parameters
year = '2022'
lat = '39.8818'
lon = '-105.0552'
interval = '5'
attributes = 'ghi,clearsky_ghi,air_temperature'
sim_step = '5min'
weather_df = inputs.get_weather_data(lat, lon, year, interval, attributes,sim_step) # 5min data

start = '2022-07-01 00:00:00'
end = '2022-07-01 23:55:00'
weather_df = weather_df.loc[start:end]
#weather_df = weather_df.resample('1s').interpolate()
sim_length = len(weather_df)
sim_step_seconds = (weather_df.index[1]-weather_df.index[0]).total_seconds() # convert from minutes to seconds
clouds = True # True = use GHI, False = use Clearsky GHI

# Simulation loop in seconds
print(f"Starting simulation at {sim_step} intervals...")
for i in range(sim_length):

    # Store sun energy
    if clouds:
        sun.irradiance = weather_df.iloc[i]['GHI']
    else:
        sun.irradiance = weather_df.iloc[i]['Clearsky GHI']

    solar_energy.append(sun.irradiance)

    # Solar energy into the panel
    panel.fluid.update_temperature(sun.energy(sim_step_seconds)*panel.efficiency, panel.fluid.mass(panel.volume))
    
    # heat loss
    panel.fluid.temperature -= panel.heat_loss()
    tank.fluid.temperature -= tank.heat_loss()

    # Piping/moving the fluid
    volume_fluid = flow_rate * sim_step_seconds * panel.fluid.density
    mass_fluid = flow_rate * sim_step_seconds 

    # into the tank
    panel.volume -= volume_fluid
    panel_tank_temp_delta =  panel.fluid.temperature - tank.fluid.temperature
    energy_into_tank = tank.fluid.energy(panel_tank_temp_delta, mass_fluid)

    tank.volume += volume_fluid
    tank.fluid.update_temperature(energy_into_tank, tank.fluid.mass(tank.volume))

    # out of the tank
    tank.volume -= volume_fluid
    tank_panel_temp_delta =   tank.fluid.temperature - panel.fluid.temperature
    energy_out_of_tank = panel.fluid.energy(tank_panel_temp_delta, mass_fluid)

    panel.volume += volume_fluid
    panel.fluid.update_temperature(energy_out_of_tank, panel.fluid.mass(panel.volume))

    # store temperatures and energies
    panel_temperatures.append(panel.fluid.temperature)
    tank_temperatures.append(tank.fluid.temperature)
    panel_energy.append(panel.fluid.energy(panel_tank_temp_delta, mass_fluid))
    tank_energy.append(tank.fluid.energy(tank_panel_temp_delta, mass_fluid))
    energy_into_tank_list.append(energy_into_tank)
    energy_out_of_tank_list.append(energy_out_of_tank)

    # Print all properties
    print(f"Time: {weather_df.index[i]}")
    print(sim_step_seconds)
    print(f"Panel Fluid Temp: {panel.fluid.temperature:.2f}")
    print(f"Panel Fluid Mass: {panel.fluid.mass(panel.volume):.2f}")
    print(f"Panel Volume: {panel.volume:.2f}")
    print(f"Energy into tank: {energy_into_tank:.2f}")
    print(f"Tank Fluid Temp: {tank.fluid.temperature:.2f}")
    print(f"Tank Fluid Mass: {tank.fluid.mass(tank.volume):.2f}")
    print(f"Tank Volume: {tank.volume:.2f}")
    print(f"Energy out of tank: {energy_out_of_tank:.2f}")
    print(f"Sun Energy: {sun.energy(sim_step_seconds):.2f}")
    print(f"Panel Energy: {panel.fluid.energy(panel_tank_temp_delta, mass_fluid):.2f}")
    print(f"Tank Energy: {tank.fluid.energy(tank_panel_temp_delta, mass_fluid):.2f}")
    print("---------------------------------------")
    
print("Simulation complete!")

############ Create the plot ##############
x = weather_df.index  # time
panel_color = "red"
tank_color = "blue"
sun_color = "orange"
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

# Temperature plot
ax1.plot(x, panel_temperatures, label="Panel Fluid Temp", color=panel_color)
ax1.plot(x, tank_temperatures, label="Tank Fluid Temp", color=tank_color)
ax1.set_title("Solar Water Heating Simulation")
ax1.set_ylabel("Temperature (°C)")
ax1.tick_params(axis="y")
ax1.legend(loc="upper right")

# Irradiance plot (right y-axis for ax1)
ax1_twin = ax1.twinx()
ax1_twin.set_ylabel("Irradiance (W/m^2)", color=sun_color)
ax1_twin.plot(x, solar_energy, label="Irradiance", color=sun_color)
ax1_twin.tick_params(axis="y", labelcolor=sun_color)
ax1_twin.legend(loc="upper left")

# Energy plot
ax2.plot(x, panel_energy, label="Panel Energy", color=panel_color)
ax2.plot(x, tank_energy, label="Tank Energy", color=tank_color)
ax2.plot(x, energy_into_tank_list, label="Energy into tank", color="green")
ax2.plot(x, energy_out_of_tank_list, label="Energy out of tank", color="purple")
ax2.set_xlabel("Time")
ax2.set_ylabel("Energy (J)")
ax2.legend(loc="upper right")

plt.tight_layout()
plt.show()



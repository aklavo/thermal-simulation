import matplotlib

matplotlib.use("TkAgg") # To show plots in Ubuntu
import matplotlib.pyplot as plt
import compenents as comps
import inputs

# System constants
flow_rate = 0.005 # [kg/s]
water_density = 100 # density of water at 4°C [kg/m^3]
water_specific_heat = 4184 # specific heat of water at 20°C [J/kg°C]
panel_volume = 1.0 # [m^3]
tank_volume = 3.0 # [m^3]
sigma = 5.670367e-8 # Stefan-Boltzmann constant [W/m^2*K^4]

# System intial conditions
oa_temp = 26.6667 # [°C] Outside ambient air temperature 80°F
zone_temp = 21.111 # [°C] Inside ambient air temperature 70°F

# Components
panel_water = comps.Fluid(panel_volume, water_density, water_specific_heat, oa_temp)
tank_water = comps.Fluid(tank_volume, water_density, water_specific_heat, zone_temp) 
sun = comps.Sun()
panel = comps.SolarPanel(panel_water)
tank = comps.Tank(tank_water)

# Lists to store simulation results
panel_temperatures = []
tank_temperatures = []
solar_energy = []

# Weather parameters
year = '2022'
lat = '39.8818'
lon = '-105.0552'
interval = '5'
attributes = 'ghi,clearsky_ghi,air_temperature'
sim_step = '5min'
weather_df = inputs.get_weather_data(lat, lon, year, interval, attributes,sim_step) # 5min data

# Simulation parameters
start = '2022-07-01 00:00:00'
end = '2022-07-01 23:55:00'
weather_df = weather_df.loc[start:end]
sim_length = len(weather_df)
sim_step_seconds = (weather_df.index[1]-weather_df.index[0]).total_seconds() # [s]
clouds = 1 # 1 = use GHI, -1 = use Clearsky GHI, 0 = no sun

# Simulation loop in seconds
print(f"Starting simulation at {sim_step} intervals...")
for i in range(sim_length):
    print(f"Time: {weather_df.index[i]}")
    print(f"Panel Fluid Temp before heat transfer: {panel.fluid.temperature:.3f}")
    print(f"Tank Fluid Temp before heat transfer: {tank.fluid.temperature:.3f}")
    # Store sun energy
    if clouds == 1:
        sun.irradiance = weather_df.iloc[i]['GHI']
    elif clouds == -1:
        sun.irradiance = weather_df.iloc[i]['Clearsky GHI']
    else:
        sun.irradiance = 0

    solar_energy.append(sun.irradiance)

    # Solar energy into the panel
    energy_to_panel = sun.energy(sim_step_seconds)*panel.efficiency
    panel.fluid.add_energy(energy_to_panel, panel.fluid.mass(panel.volume))
    
    # heat loss
    #panel.fluid.temperature -= panel.heat_loss()
    #tank.fluid.temperature -= tank.heat_loss()

    # Piping/moving the fluid
    supply_volume = (flow_rate * sim_step_seconds) / panel.fluid.density
    supply_temp = panel.fluid.temperature
    supply_flow = comps.Fluid(supply_volume, water_density, water_specific_heat, supply_temp)

    return_volume = (flow_rate * sim_step_seconds) / tank.fluid.density
    return_temp = tank.fluid.temperature
    return_flow = comps.Fluid(return_volume, water_density, water_specific_heat, return_temp)

    # Update Tank and Panel temperatures
    tank.fluid.mix_with(supply_flow)
    print(f"Tank Fluid Temp after heat transfer: {tank.fluid.temperature:.3f}")

    panel.fluid.mix_with(return_flow)
    print(f"Panel Fluid Temp after heat transfer: {panel.fluid.temperature:.3f}")

    # store temperatures and energies
    panel_temperatures.append(panel.fluid.temperature)
    tank_temperatures.append(tank.fluid.temperature)
    print("---------------------------------------")
    
    
print("Simulation complete!")

############ Create the plot ##############
x = weather_df.index  # time
panel_color = "red"
tank_color = "blue"
sun_color = "orange"
oat_color = "green"
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

# Other plot
ax2.plot(x, weather_df["Temperature"], label="Outside Air Temp", color=oat_color)
ax2.set_xlabel("Time")
ax2.set_ylabel("Temperature (°C)")
ax2.legend(loc="upper right")

plt.tight_layout()
plt.show()



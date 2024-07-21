#!/usr/bin/env python

"""
File: main.py
Author: Andrew Klavekoske
Last Updated: 2024-07-22

Description: Physics-based thermal simulation of a solar
hot water panel and storage tank.
"""


import matplotlib

matplotlib.use("TkAgg") # To show plots in Ubuntu
import matplotlib.pyplot as plt
import components as comps
import inputs


def main():
    # System constants
    flow_rate = 0.0063 # [m^3/s] ~100gpm
    water_density = 100 # density of water at 4°C [kg/m^3]
    water_specific_heat = 4184 # specific heat of water at 20°C [J/kg°C]
    air_density = 0.985 # density of air at 5000ft, 70°F, 29.7 inHg, 47% RH [kg/m^3]
    air_specific_heat = 1.006 # specific heat of air at 20°C [J/kg°C]
    air_heat_transfer_coeff = 10 # heat transfer coefficient of air [W/m^2*K]
    panel_length = 2 # [m]
    panel_width = 1 # [m]
    panel_hieght = 0.1 # [m]
    tank_radius = 0.5 # [m]
    tank_height = 2 # [m]
    pipe_radius = 0.02 # [m]
    pipe_length = 3 # [m]
    sigma = 5.670367e-8 # Stefan-Boltzmann constant [W/m^2*K^4]
    k_stainless_steal = 17 # Thermal conductivity of stainless steel [W/m*K]
    k_glass = 1 # Thermal conductivity of glass [W/m*K]
    k_copper = 4#01 # Thermal conductivity of copper [W/m*K]

    # Ambient air intial conditions
    oa_temp = 26.6667 # [°C] Outside ambient air temperature 80°F
    zone_temp = 21.111 # [°C] Inside ambient air temperature 70°F

    # Initialize Components
    tank_stainless_steal = comps.Material(k_stainless_steal, zone_temp, 0.03)
    panel_glass = comps.Material(k_glass, oa_temp, 0.01)
    copper_pipe = comps.Material(k_copper, zone_temp, 0.005)

    sun = comps.Sun()

    outside_air = comps.Fluid(air_density, air_specific_heat, oa_temp)
    zone_air = comps.Fluid(air_density, air_specific_heat, zone_temp)
    panel_water = comps.Fluid(water_density, water_specific_heat, oa_temp)
    supply_hw = comps.Fluid(water_density, water_specific_heat, zone_temp)
    tank_water = comps.Fluid(water_density, water_specific_heat, zone_temp) 
    return_hw = comps.Fluid(water_density, water_specific_heat, zone_temp)

    panel = comps.SolarPanel(panel_water, panel_glass, panel_length, panel_width, panel_hieght)
    supply_pipe = comps.Pipe(supply_hw, copper_pipe, pipe_radius, pipe_length)
    tank = comps.Tank(tank_water, tank_stainless_steal, tank_radius, tank_height)
    return_pipe = comps.Pipe(return_hw, copper_pipe, pipe_radius, pipe_length)

    # Put Water in containers
    panel.fluid.add_container(panel)
    supply_pipe.fluid.add_container(supply_pipe)
    tank.fluid.add_container(tank)
    return_pipe.fluid.add_container(return_pipe)

    # Lists to store simulation results
    panel_temperatures = []
    tank_temperatures = []
    zone_air_temps = []
    solar_energy = []
    heat_loss = []

    # Weather parameters
    year = '2022'
    lat = '39.8818'
    lon = '-105.0552'
    interval = '5'
    attributes = 'ghi,clearsky_ghi,air_temperature'
    sim_step = '1min'
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
        print(f"Supply Pipe Fluid Temp before heat transfer: {supply_pipe.fluid.temperature:.3f}")
        print(f"Tank Fluid Temp before heat transfer: {tank.fluid.temperature:.3f}")
        print(f"Return Pipe Fluid Temp before heat transfer: {return_pipe.fluid.temperature:.3f}")
        # Update sun energy
        if clouds == 1:
            sun.irradiance = weather_df.iloc[i]['GHI']
        elif clouds == -1:
            sun.irradiance = weather_df.iloc[i]['Clearsky GHI']
        else:
            sun.irradiance = 0

        # Add solar energy into the panel
        energy_to_panel = sun.energy(sim_step_seconds, panel.solar_area())*panel.efficiency
        panel.fluid.add_energy(energy_to_panel)

        # Move and mix the fluids - This updates all comp fluid temps
        supply_pipe.fluid.mix_with(panel.fluid, flow_rate, sim_step_seconds)
        tank.fluid.mix_with(supply_pipe.fluid, flow_rate, sim_step_seconds)
        return_pipe.fluid.mix_with(tank.fluid, flow_rate, sim_step_seconds)
        panel.fluid.mix_with(return_pipe.fluid, flow_rate, sim_step_seconds)
      
        # Heat loss
        outside_air.temperature = weather_df.iloc[i]['Temperature']
        #panel heat loss blows up simulation
        #panel.fluid.lose_energy(panel.conduction_loss(outside_air, sim_step_seconds))
        supply_pipe_cond_loss = supply_pipe.conduction_loss(zone_air, sim_step_seconds)
        tank_cond_loss = tank.conduction_loss(zone_air, sim_step_seconds)
        return_pipe_cond_loss = return_pipe.conduction_loss(zone_air, sim_step_seconds)
        supply_pipe.fluid.lose_energy(supply_pipe_cond_loss)
        tank.fluid.lose_energy(tank_cond_loss)
        return_pipe.fluid.lose_energy(return_pipe_cond_loss)

        heat_transferred_to_air = (supply_pipe_cond_loss + tank_cond_loss + return_pipe_cond_loss)

        
        print(f"Sim timestep: {sim_step_seconds} s")
        print(f"Panel Fluid Temp after heat transfer: {panel.fluid.temperature:.3f}")
        print(f"Supply Pipe Fluid Temp after heat transfer: {supply_pipe.fluid.temperature:.3f}")
        print(f"Tank Fluid Temp after heat transfer: {tank.fluid.temperature:.3f}")
        print(f"Return Pipe Fluid Temp after heat transfer: {return_pipe.fluid.temperature:.3f}")
        
        
        # store temperatures and energies
        solar_energy.append(sun.irradiance)
        panel_temperatures.append(panel.fluid.temperature)
        tank_temperatures.append(tank.fluid.temperature)
        heat_loss.append(heat_transferred_to_air)
        zone_air_temps.append(zone_air.temperature)
        print("---------------------------------------")
        
        
    print("Simulation complete!")

    ############ Create the plot ##############
    x = weather_df.index  # time
    panel_color = "red"
    tank_color = "blue"
    sun_color = "orange"
    oat_color = "green"
    heat_color = "black"
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
    ax2.plot(x, zone_air_temps, label="Zone Air Temp", color=panel_color)
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Temperature (°C)")
    ax2.legend(loc="upper right")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(x, heat_loss, label="Heat Lost", color=heat_color)
    ax2_twin.set_xlabel("Time")
    ax2_twin.set_ylabel("Energy (J)")
    ax2_twin.legend(loc="upper left")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

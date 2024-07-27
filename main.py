#!/usr/bin/env python

"""
File: main.py
Author: Andrew Klavekoske
Last Updated: 2024-07-22

Description: Physics-based thermal simulation of a solar
hot water panel and storage tank.
"""

import matplotlib
#matplotlib.use("TkAgg") # To show plots in Ubuntu
import matplotlib.pyplot as plt
import components as comps
import inputs
import pandas as pd

def main():
    # True for development, False for production (saves outputs)
    DEV = False#input("Run in development mode? (True/False): ").lower() == 'true'
    # -------------------------------------------------- Inputs ------------------------------------------------
    # System constants
    flow_rate_initial = 0 # [m^3/s] 
    water_density = 100 # density of water at 4°C [kg/m^3]
    water_specific_heat = 4184 # specific heat of water at 20°C [J/kg°C]
    air_density = 0.985 # density of air at 5000ft, 70°F, 29.7 inHg, 47% RH [kg/m^3]
    air_specific_heat = 1.006 # specific heat of air at 20°C [J/kg°C]
    air_heat_transfer_coeff_inside = 10 # heat transfer coefficient of air [W/m^2*K]
    air_heat_transfer_coeff_outside = 50 # heat transfer coefficient of air [W/m^2*K]
    water_in_pipe_heat_transfer_coeff =  1000 # heat transfer coefficient of water in pipe [W/m^2*K]
    panel_length = 2 # [m]
    panel_width = 1 # [m]
    panel_height = 0.1 # [m]
    tank_radius = 0.5 # [m]
    tank_height = 2 # [m]
    pipe_radius = 0.02 # [m]
    pipe_length = 2 # [m]
    sigma = 5.670367e-8 # Stefan-Boltzmann constant [W/m^2*K^4]
    k_stainless_steal = 17 # Thermal conductivity of stainless steel [W/m*K]
    k_glass = 1 # Thermal conductivity of glass [W/m*K]
    k_cast_iron = 80 # Thermal conductivity of cast iron [W/m*K]
    k_fiberglass = 0.036 # Thermal conductivity of fiberglass [W/m*K]

    # Ambient air initial conditions
    oa_temp = 26.6667 # [°C] Outside ambient air temperature 80°F
    zone_temp = 21.111 # [°C] Inside ambient air temperature 70°F

    # Initialize Components
    tank_stainless_steal = comps.Material(k_stainless_steal, zone_temp, 0.03)
    panel_glass = comps.Material(k_glass, oa_temp, 0.01)
    cast_iron_pipe = comps.Material(k_cast_iron, oa_temp, 0.005)
    k_fiberglass_insulation = comps.Material(k_fiberglass, zone_temp, 0.03)

    sun = comps.Sun()
    pump = comps.Pump(flow_rate_initial)

    outside_air = comps.Fluid("OA", air_density, air_specific_heat, oa_temp, heat_transfer_coefficient=air_heat_transfer_coeff_outside)
    zone_air = comps.Fluid("ZN", air_density, air_specific_heat, zone_temp, heat_transfer_coefficient=air_heat_transfer_coeff_inside)
    panel_water = comps.Fluid("Panel water", water_density, water_specific_heat, oa_temp, heat_transfer_coefficient=water_in_pipe_heat_transfer_coeff)
    supply_hw = comps.Fluid("HWS", water_density, water_specific_heat, oa_temp, heat_transfer_coefficient=water_in_pipe_heat_transfer_coeff)
    tank_water = comps.Fluid("Tank water", water_density, water_specific_heat, zone_temp, heat_transfer_coefficient=water_in_pipe_heat_transfer_coeff)
    return_hw = comps.Fluid("HWR", water_density, water_specific_heat, oa_temp, heat_transfer_coefficient=water_in_pipe_heat_transfer_coeff)

    panel = comps.SolarPanel(panel_water, panel_glass, outside_air, panel_length, panel_width, panel_height)
    supply_pipe = comps.Pipe(supply_hw, cast_iron_pipe, outside_air, pipe_radius, pipe_length, k_fiberglass_insulation)
    tank = comps.Tank(tank_water, tank_stainless_steal, zone_air, tank_radius, tank_height, k_fiberglass_insulation)
    return_pipe = comps.Pipe(return_hw, cast_iron_pipe, outside_air, pipe_radius, pipe_length, k_fiberglass_insulation)

    # Put Water in containers
    panel.fluid.add_container(panel)
    supply_pipe.fluid.add_container(supply_pipe)
    tank.fluid.add_container(tank)
    return_pipe.fluid.add_container(return_pipe)

    # Lists to store simulation results
    panel_temperatures = []
    supply_pipe_temperatures = []
    tank_temperatures = []
    return_pipe_temperatures = []
    zone_air_temps = []
    solar_energy = []
    panel_heat_losses = []
    supply_pipe_heat_losses = []
    tank_heat_losses = []
    return_pipe_heat_losses = []
    total_heat_losses = []
    flow_rates = []

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
    end = '2022-07-31 23:55:00'
    weather_df = weather_df.loc[start:end]
    sim_length = len(weather_df)
    sim_step_seconds = (weather_df.index[1]-weather_df.index[0]).total_seconds() # [s]
    clouds = 1 # 1 = use GHI, -1 = use Clearsky GHI, 0 = no sun

    # ---------------------------------------------- Simulation ------------------------------------------------
    # Simulation loop in seconds
    print(f"Starting simulation at {sim_step} intervals...")
    for i in range(sim_length):
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

        # Pump control
        if supply_pipe.fluid.temperature < tank.fluid.temperature:
            pump.flow_rate = 0
        else:
            pump.flow_rate = 0.00063

        # Move and mix the fluids - This updates all fluid temps
        panel.fluid.mix_with(return_pipe.fluid, pump.flow_rate, sim_step_seconds)
        supply_pipe.fluid.mix_with(panel.fluid, pump.flow_rate, sim_step_seconds)
        tank.fluid.mix_with(supply_pipe.fluid, pump.flow_rate, sim_step_seconds)
        return_pipe.fluid.mix_with(tank.fluid, pump.flow_rate, sim_step_seconds)
      
        # Heat loss
        outside_air.temperature = weather_df.iloc[i]['Temperature']

        panel_heat_loss = panel.heat_loss(sim_step_seconds)
        supply_pipe_heat_loss = supply_pipe.heat_loss(sim_step_seconds)
        tank_heat_loss = tank.heat_loss(sim_step_seconds)
        return_pipe_heat_loss = return_pipe.heat_loss(sim_step_seconds)

        panel.fluid.lose_energy(panel_heat_loss)    
        supply_pipe.fluid.lose_energy(supply_pipe_heat_loss)
        tank.fluid.lose_energy(tank_heat_loss)
        return_pipe.fluid.lose_energy(return_pipe_heat_loss)

        
        # store temperatures and energies and flows
        heat_transferred_to_air = (panel_heat_loss + supply_pipe_heat_loss +
                                    tank_heat_loss + return_pipe_heat_loss)
        solar_energy.append(sun.irradiance)
        panel_temperatures.append(panel.fluid.temperature)
        supply_pipe_temperatures.append(supply_pipe.fluid.temperature)
        tank_temperatures.append(tank.fluid.temperature)
        return_pipe_temperatures.append(return_pipe.fluid.temperature)
        zone_air_temps.append(zone_air.temperature)
        panel_heat_losses.append(panel_heat_loss)
        supply_pipe_heat_losses.append(supply_pipe_heat_loss)
        tank_heat_losses.append(tank_heat_loss)
        return_pipe_heat_losses.append(return_pipe_heat_loss)
        total_heat_losses.append(heat_transferred_to_air)
        flow_rates.append(pump.flow_rate)
    print("Simulation complete!")

    # ------------------------------------------------ Outputs --------------------------------------------------
    x = weather_df.index  # time
    panel_color = "firebrick"
    supply_pipe_color = "chocolate"
    tank_color = "orange"
    return_pipe_color = "blue"
    sun_color = "goldenrod"
    oat_color = "green"
    zone_air_color = "indigo"

    plt.style.use("Solarize_Light2")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(18, 14), sharex=True)
    plt.tight_layout()
    fig.subplots_adjust(right=0.83, left= 0.05, top=0.97)

    # Weather plot 
    ax1.set_title("Solar Water Heating Simulation", fontweight='bold')
    ax1.plot(x, solar_energy, label="Irradiance", color=sun_color)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(x, weather_df["Temperature"], label="Outside Air Temp", color=oat_color, linestyle="--")
    ax1_twin.plot(x, zone_air_temps, label="Zone Air Temp", color=zone_air_color, linestyle=":")
    ax1.set_ylabel("Irradiance (W/m^2)", color=sun_color, fontweight='bold')
    ax1.tick_params(axis="y", labelcolor=sun_color)
    ax1_twin.set_ylabel("Temperature (°C)", color=oat_color, fontweight='bold')
    ax1_twin.tick_params(axis="y", labelcolor=oat_color)
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(1.05, 1.02))
    ax1.grid(True, linestyle='--', alpha=0.7)

    ax1_twin.grid(True, linestyle=':', alpha=0.5)

    # Temperature plot
    ax2.plot(x, panel_temperatures, label="Panel Fluid Temp", color=panel_color)
    ax2.plot(x, supply_pipe_temperatures, label="Supply Pipe Fluid Temp", color=supply_pipe_color, linestyle=":")
    ax2.plot(x, tank_temperatures, label="Tank Fluid Temp", color=tank_color)
    ax2.plot(x, return_pipe_temperatures, label="Return Pipe Fluid Temp", color=return_pipe_color, linestyle=":")
    ax2.set_ylabel("Temperature (°C)", fontweight='bold')
    ax2.tick_params(axis="y")
    ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 1.02))
    ax2_twin = ax2.twinx()
    ax2_twin.plot(x, flow_rates, label="Flow Rate", color='purple', alpha=0.5, zorder=0)
    ax2_twin.set_ylabel("Flow Rate (m^3/s)", color='purple', fontweight='bold')
    ax2_twin.tick_params(axis="y", labelcolor='purple')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2_twin.grid(True, linestyle=':', alpha=0.5)

    # Combine legends
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    lines_2_twin, labels_2_twin = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_2 + lines_2_twin, labels_2 + labels_2_twin, loc='upper left', bbox_to_anchor=(1.05, 1.02))
    
    # Heat Loss plot
    ax3.plot(x, supply_pipe_heat_losses, label="Pipe Heat Loss", color=supply_pipe_color, linestyle=":")
    ax3.plot(x, tank_heat_losses, label="Tank Heat Loss", color=tank_color)
    ax3.plot(x, return_pipe_heat_losses, label="Return Pipe Heat Loss", color=return_pipe_color, linestyle=":")
    ax3_twin = ax3.twinx()
    ax3_twin.set_ylabel("Panel Heat Loss (J)", color=panel_color, fontweight='bold')
    ax3_twin.tick_params(axis="y", labelcolor=panel_color)
    ax3_twin.plot(x, panel_heat_losses, label="Panel Heat Loss", color=panel_color)
    ax3.set_ylabel("Heat Loss (J)", fontweight='bold')
    ax3.tick_params(axis="y")
    lines_3, labels_3 = ax3.get_legend_handles_labels()
    lines_4, labels_4 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines_3 + lines_4, labels_3 + labels_4, loc='upper left', bbox_to_anchor=(1.05, 1.02))
    ax3.grid(True, linestyle='--', alpha=0.7)
    ax3_twin.grid(True, linestyle=':', alpha=0.5)

    if DEV:
        plt.show()
    else:
        plt.savefig("Outputs/thermal-simulation.png")
        df = pd.DataFrame({"Time": x,
                        "Irradiance": solar_energy,
                        "Outside Air Temp": weather_df["Temperature"],
                        "Zone Air Temp": zone_air_temps,
                        "Panel Temp": panel_temperatures,
                        "Supply Pipe Temp": supply_pipe_temperatures,
                        "Tank Temp": tank_temperatures,
                        "Return Pipe Temp": return_pipe_temperatures,
                        "Panel Heat Loss": panel_heat_losses,
                        "Supply Pipe Heat Loss": supply_pipe_heat_losses,
                        "Tank Heat Loss": tank_heat_losses,
                        "Return Pipe Heat Loss": return_pipe_heat_losses,
                        "Flow Rate": flow_rates,
                        "Total Heat Loss": total_heat_losses})
        df.to_csv("Outputs/thermal-simulation.csv", index=False)


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Thermal Simulation Report",
    page_icon="☀️" 
)

st.header("The Simulation")
st.subheader("Inputs")
'''
This simulation currently takes  in the following inputs:
- Start/End Datetime (must be within the weather data range)
- Timestep
- Clouds (1 = GHI, -1 = Clearsky GHI, 0 = no sun)

'''
st.subheader("Simulation")
'''
Other than storing the timeseries data, the simulation has four main sections.  
1. Add solar energy into the panel
2. Move/Mix the fluids of adjacent containers
3. Loss energy to the surroundings
4. Pump control
'''

show_code = st.toggle("Show Sim Code")

if show_code:
    sim_code = '''
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
        '''
    st.code(sim_code, language='python')

st.subheader("Outputs")
'''
Running the simulation in production mode produces a png image and csv file of the relevant simulation parameters.
'''
st.image("thermal-simulation.png")
sim_results = pd.read_csv("thermal-simulation.csv")
st.dataframe(sim_results)

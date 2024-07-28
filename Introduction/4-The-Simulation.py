import streamlit as st
import pandas as pd
import app

st.header("The Simulation")
st.subheader("Inputs")
'''
This simulation currently takes  in the following inputs:
- Start/End Datetime (must be within the weather data range)
- Time-step
- Clouds (1 = GHI, -1 = Clearsky GHI, 0 = no sun)

'''
st.subheader("Simulation")
'''
Other than storing the time-series data, the simulation has four main sections.  
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
        if pump_control == 0:
            pump.flow_rate = 0
        elif pump_control == 1:
            pump.flow_rate = flow_rate_initial
        elif pump_control == 2:
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
        if heat_loss:
            panel_heat_loss = panel.heat_loss(sim_step_seconds)
            supply_pipe_heat_loss = supply_pipe.heat_loss(sim_step_seconds)
            tank_heat_loss = tank.heat_loss(sim_step_seconds)
            return_pipe_heat_loss = return_pipe.heat_loss(sim_step_seconds)

            panel.fluid.lose_energy(panel_heat_loss)    
            supply_pipe.fluid.lose_energy(supply_pipe_heat_loss)
            tank.fluid.lose_energy(tank_heat_loss)
            return_pipe.fluid.lose_energy(return_pipe_heat_loss)
        else:
            panel_heat_loss = 0
            supply_pipe_heat_loss = 0
            tank_heat_loss = 0
            return_pipe_heat_loss = 0

        
        # store temperatures and energies and flows
        heat_transferred_to_air = (panel_heat_loss + supply_pipe_heat_loss +
                                    tank_heat_loss + return_pipe_heat_loss)
        sim_output_data['time'].append(weather_df.index[i])
        sim_output_data['solar_energy'].append(sun.irradiance)
        sim_output_data['panel_temperatures'].append(panel.fluid.temperature)
        sim_output_data['supply_pipe_temperatures'].append(supply_pipe.fluid.temperature)
        sim_output_data['tank_temperatures'].append(tank.fluid.temperature)
        sim_output_data['return_pipe_temperatures'].append(return_pipe.fluid.temperature)
        sim_output_data['zone_air_temperatures'].append(zone_air.temperature)
        sim_output_data['outside_air_temperatures'].append(outside_air.temperature)
        sim_output_data['panel_heat_losses'].append(panel_heat_loss)
        sim_output_data['supply_pipe_heat_losses'].append(supply_pipe_heat_loss)
        sim_output_data['tank_heat_losses'].append(tank_heat_loss)
        sim_output_data['return_pipe_heat_losses'].append(return_pipe_heat_loss)
        sim_output_data['total_heat_losses'].append(heat_transferred_to_air)
        sim_output_data['flow_rates'].append(pump.flow_rate)
    print("Simulation complete!")
        '''
    st.code(sim_code, language='python')

st.subheader("Outputs")
'''
Running the simulation in production mode produces saves a png image and parquet file of the relevant simulation parameters to the Outputs folder.
'''
results_df = pd.read_parquet("Outputs/thermal-simulation.parquet")
fig = app.sim_output_plot(results_df)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(results_df)

import streamlit as st
import pandas as pd
import main

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
            pump.flow_rate = flow_rate_max
        elif pump_control == 2:
            if supply_pipe.fluid.temperature < tank.fluid.temperature:
                pump.flow_rate = 0
            else:
                pump.flow_rate = flow_rate_max

        # Move and mix the fluids - This updates all fluid temps
        panel.fluid.mix_with(return_pipe.fluid, pump.flow_rate, sim_step_seconds)
        supply_pipe.fluid.mix_with(panel.fluid, pump.flow_rate, sim_step_seconds)
        tank.fluid.mix_with(supply_pipe.fluid, pump.flow_rate, sim_step_seconds)
        return_pipe.fluid.mix_with(tank.fluid, pump.flow_rate, sim_step_seconds)
      
        # Heat loss
        outside_air.temperature = weather_df.iloc[i]['Temperature']
        zone_air.temperature = zone_temp + random.uniform(-0.5, 0.5)        
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
        sim_output_data['Time'].append(weather_df.index[i])
        sim_output_data['Solar Energy'].append(sun.irradiance)
        sim_output_data['Panel Temperatures'].append(panel.fluid.temperature)
        sim_output_data['Supply Pipe Temperatures'].append(supply_pipe.fluid.temperature)
        sim_output_data['Tank Temperatures'].append(tank.fluid.temperature)
        sim_output_data['Return Pipe Temperatures'].append(return_pipe.fluid.temperature)
        sim_output_data['Zone Air Temperatures'].append(zone_air.temperature)
        sim_output_data['Outside Air Temperatures'].append(outside_air.temperature)
        sim_output_data['Panel Heat Losses'].append(panel_heat_loss)
        sim_output_data['Supply Pipe Heat Losses'].append(supply_pipe_heat_loss)
        sim_output_data['Tank Heat Losses'].append(tank_heat_loss)
        sim_output_data['Return Pipe Heat Losses'].append(return_pipe_heat_loss)
        sim_output_data['Total Heat Losses'].append(heat_transferred_to_air)
        sim_output_data['Flow Rates'].append(pump.flow_rate)
    print("Simulation complete!")
        '''
    st.code(sim_code, language='python')

st.subheader("Outputs")
'''
Running the simulation in production mode produces saves a png image and parquet file of the relevant simulation parameters to the Outputs folder.
Below are interactive plots and dataframes of the simulation results.
'''
with st.spinner("Getting Data..."):
    results_df = pd.read_parquet("Outputs/thermal-simulation-full-year.parquet")
    three_days_df = results_df.loc[(results_df['Time'] >= '2022-07-01 00:00:00') & (results_df['Time'] <= '2022-07-03 23:55:00')]
  

with st.spinner("Plotting simulation results..."):
    fig = main.sim_output_plot(three_days_df)
    st.plotly_chart(fig, use_container_width=True)
st.dataframe(three_days_df)

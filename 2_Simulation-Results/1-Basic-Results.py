import streamlit as st
import main
import datetime
import pandas as pd



def simulation_display(disabled_clouds, disabled_pumps, widget_id, cloud_start, flow_start, heat_loss_start=False):

    container = st.container()
    with container:
        col1, col2, col3 = st.columns(3)

        with col2:
            clouds = st.radio(
                "**Cloud Cover**",
                [1, -1, 0],
                index=[1, -1, 0].index(cloud_start),
                format_func=lambda x: (
                    "No Sun" if x == 0 else "Clear Sky GHI" if x == -1 else "GHI"
                ),
                disabled=disabled_clouds,
                key=f"clouds_{widget_id}"
            )
            heat_loss = st.toggle("Enable Heat Loss", value=heat_loss_start, key=f"heat_loss_{widget_id}")

        with col3:
            pump_control = st.radio(
                "**Pump Control**",
                [0, 1, 2],
                format_func=lambda x: {0: "No Flow", 1: "Constant Flow", 2: "Controlled Flow"}[
                    x
                ],
                index=flow_start,
                disabled=disabled_pumps,
                key=f"pump_control_{widget_id}"
            )

            if pump_control in [1, 2]:
                flow_rate_max = st.slider(
                    "Max Flow Rate [m³/s]",
                    min_value=0.0,
                    max_value=0.00063*3,
                    value=0.00063,
                    step=0.0001,
                    format="%.4f",
                    key=f"flow_rate_max_{widget_id}"
                )  
            else:
                flow_rate_max = 0.0

        @st.cache_data
        def run_sim_get_plot(clouds, heat_loss, pump_control, flow_rate_max):
            main.run_sim(
                clouds=clouds,
                heat_loss=heat_loss,
                pump_control=pump_control,
                flow_rate_max=flow_rate_max,
            )

            results_df = pd.read_parquet("Outputs/thermal-simulation.parquet")

            fig = main.sim_output_plot(results_df)
            return results_df, fig
        with st.spinner("Running simulation..."):
            results_df, fig = run_sim_get_plot(clouds, heat_loss, pump_control, flow_rate_max)
            st.plotly_chart(fig, use_container_width=True)

        with col1:
            # Simulation metrics
            start_tank_temp = results_df.iloc[0]["Tank Temperatures"]
            final_tank_temp = results_df.iloc[-1]["Tank Temperatures"]
            sim_step_seconds = (results_df['Time'].iloc[1]- results_df['Time'].iloc[0]).total_seconds()
            pump_time = (results_df["Flow Rates"] != 0).sum()*sim_step_seconds
            st.metric("Final Tank Temperature", f"{final_tank_temp:.2f}°C", delta=f"{final_tank_temp-start_tank_temp:.2f}°C")
            st.metric("Pump Runtime", f"{pump_time/60/60:.2f} hrs ")

st.header("Basic Results")
'''
This section will start from the most basic simulation **(no sun, no heat loss, no flow)** and work towards the
full simulation **(GHI, heat loss enabled, and controlled flow)**. 
'''
'''
The results discussed in this section are based on a start date of 2022-07-01 and an end date of 2022-07-03.
'''
st.subheader("Basic Simulation")
'''
When there is no sun, no heat loss, and no flow, all temperatures remain constant. The tank is modeled inside and thus remains at 21.11$^\circ$C
and the panels and pipes are initialized at 26.66$^\circ$C. With no heat loss they remain at 26.66$^\circ$C. 

If heat loss is **enabled**, the temperatures of the fluids in the panels and pipes will quickly track towards outdoor air temperatures. 
'''
simulation_display(disabled_clouds=True, disabled_pumps=True, widget_id=1,cloud_start=0, flow_start=0)

st.subheader("Adding the Sun")
'''
The first step in modeling this system is to add an energy source to the system. This is done by adding actual solar energy (GHI) into the panel fluid at every time-step.
With no flow and no heat loss, the fluid's temperature in the panel will quickly rise while the sun is out and remain constant overnight. The panel temperature will follow
this stair step rise indefinitely.

Now when heat loss is **enabled**, the panel temperature behaves differently. Due to the additional energy during the day the panel is able to maintain 
a higher than ambient temperature. All temperatures quickly track towards outdoor air temperatures at night when there is no solar energy. 
'''
simulation_display(disabled_clouds=False, disabled_pumps=True, widget_id=2, cloud_start=1, flow_start=0)

st.subheader("Adding Flow")
'''
The next step is to add flow to the system. Under basic conditions (no sun, no heat loss) and a constant flow rate the
system reaches thermal equilibrium in about 30 minutes at about 22.22$^\circ$C.

When heat loss is **enabled**, all temperatures quickly track towards outdoor air temperatures. Due to the constant flow, the pipe and tank temperatures
(which are downstream of the panel) lag behind the panel temperature. As **flow increases** the lag and amplitude approach the panel temperature. As the **flow
decreases** the temporal lag increases and the temperature amplitude decreases.

When the **sun is added back** in this lag or phase shift isn't present. The tank temperature remains above the panel temperature in the second half
of each day due to it's higher thermal resistance. This is only true at flow rates above ~ 0.0003 m³/s. Under this flow rate the
heat loss to the surroundings remains dominate and pushes the temperatures towards the indoor temperature.
'''
simulation_display(disabled_clouds=False, disabled_pumps=True, widget_id=3, cloud_start=0, flow_start=1)

st.subheader("Controlled Flow")
'''
The final simulation is that of a controlled flow. Controlled flow in this case refers to a static sequence of operation. The sequence is as follows:

1. Compare the supply pipe temperature to the tank temperature. 
    - If the supply pipe temperature is greater than the tank temperature, turn the pump on.
    - If the supply pipe temperature is less than the tank temperature, turn the pump off.

This sequence ensures that the tank only ever losses heat to its surroundings and not due to mixing with colder temperature fluids. Under this control
the tank temperature can increase day over day despite its losses the the surrounding indoor air. Given more time a multi-objective
optimization would be considered to determine the optimal flow rate for maximizing tank temperature while minimizing pump runtime. 
'''
simulation_display(disabled_clouds=False, disabled_pumps=False, widget_id=4, cloud_start=1, flow_start=2, heat_loss_start=True)
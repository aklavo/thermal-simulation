import streamlit as st
import main
import datetime
import pandas as pd



st.header("Basic Results")
'''
Toggle between the most basic simulation **(no sun, no heat loss, no flow)** and the full simulation **(GHI, heat loss enabled, and controlled flow)**. 
'''
col1, col2, col3 = st.columns(3)

with col1:
    start = st.date_input(
        "Start Date",
        value=datetime.date(2022, 7, 1),
        min_value=datetime.date(2022, 1, 1),
        max_value=datetime.date(2022, 12, 31),
    )
    end = st.date_input(
        "End Date",
        value=datetime.date(2022, 7, 3),
        min_value=datetime.date(2022, 1, 1),
        max_value=datetime.date(2022, 12, 31),
    )

with col2:
    clouds = st.radio(
        "**Cloud Cover**",
        [0, -1, 1],
        format_func=lambda x: (
            "No Sun" if x == 0 else "Clear Sky GHI" if x == -1 else "GHI"
        ),
    )
    heat_loss = st.toggle("Enable Heat Loss", value=False)

with col3:
    pump_control = st.radio(
        "**Pump Control**",
        [0, 1, 2],
        format_func=lambda x: {0: "No Flow", 1: "Constant Flow", 2: "Controlled Flow"}[
            x
        ],
    )

    if pump_control in [1, 2]:
        flow_rate_max = st.slider(
            "Flow Rate [m³/s]",
            min_value=0.0,
            max_value=0.00063*3,
            value=0.00063,
            step=0.0001,
            format="%.4f",
        )  
    else:
        flow_rate_max = 0.0

if start <= end:
    start_str = start.strftime("%Y-%m-%d 00:00:00")
    end_str = end.strftime("%Y-%m-%d 23:55:00")

    sim_step = "5min"
    DEV = False

    with st.spinner("Running simulation..."):
        main.run_sim(
            start=start_str,
            end=end_str,
            sim_step=sim_step,
            clouds=clouds,
            heat_loss=heat_loss,
            pump_control=pump_control,
            flow_rate_max=flow_rate_max,
            DEV=DEV,
        )

    results_df = pd.read_parquet("Outputs/thermal-simulation.parquet")
    fig = main.sim_output_plot(results_df)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Start date must be before or equal to end date.")

st.subheader("Basic Simulation")
'''
The results discussed in this section are based on a start date of 2022-07-01 and an end date of 2022-07-03.
'''
'''
When there is no sun, no heat loss, and no flow, all temperatures remains constant. The tank is modeled inside and thus remains at 21.11$^\circ$C
and the panels and pipes are initialized at 26.66$^\circ$C. With no heat loss they remain at 26.66$^\circ$C. 

If heat loss is enabled, the temperatures of the fluids in the panels and pipes will quickly track towards outdoor air temperatures. 
'''

st.subheader("Adding the Sun")
'''
The first step in modelling this system is to add an energy source to the system. This is done by adding actual solar energy (GHI) into the panel fluid.
With no flow and no heat loss, the fluid in the panel will quickly rise while the sun is out and remain constant overnight. The panel temperature will follow
this stair step rise indefinitely.

When heat loss is enabled, again the fluids in pipes quickly track towards outdoor air temperatures. The panel temperature however is able to maintain 
a higher than ambient temperature during the daytime (nonzero irradiance).
'''

st.subheader("Adding Flow")
'''
The next step is to add flow to the system. Under basic conditions (no sun, no heat loss) with a constant flow rate all fluids converge at final temperature
of about 22.22$^\circ$C after about 30 minutes.

When heat loss is enabled, all temperatures quickly track towards outdoor air temperatures, but because of the constant flow the pipe and tank temperatures
(which are downstream of the panel) lag behind the panel temperature. As flow increases the lag and amplitude approach the panel temperature. As the flow
decreases the temporal lag increases and the temperature amplitude decreases.

When the sun is added back in this phase shift mentioned above isn't present and the tank temperature remains above the panel temperature in the second half
of each day due to it's higher thermal resistance.
'''

st.subheader("Controlled Flow")
'''
Controlled flow in this cause refers to a static sequence of operation. The sequence is as follows:

1. Compare the supply pipe temperature to the tank temperature. 
    - If the supply pipe temperature is greater than the tank temperature, then the pump is turned on.
    - If the supply pipe temperature is less than the tank temperature, then the pump is turned off.

This sequence ensures that tank only every losses heat to its surroundings and not due to mixing with colder temperature fluids. Under this control
the tank temperature can increase day over day despite its steady losses the the surrounding indoor air while the pump is off. 

'''
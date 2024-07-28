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
            DEV=DEV,
        )

    results_df = pd.read_parquet("Outputs/thermal-simulation.parquet")
    fig = main.sim_output_plot(results_df)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Start date must be before or equal to end date.")

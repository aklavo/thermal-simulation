import streamlit as st
import main
import datetime
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

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
        [1, -1, 0],
        format_func=lambda x: (
            "GHI" if x == 1 else "Clear Sky GHI" if x == -1 else "No Sun"
        ),
    )
    heat_loss = st.toggle("Enable Heat Loss", value=True)

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
    with st.spinner("Plotting results..."):
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]], subplot_titles=("Weather", "Temperatures & Flow", "Heat Losses"))

        # Weather plot
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Solar Energy'], name="Irradiance", line=dict(color="goldenrod")), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Outside Air Temperatures'], name="Outside Air Temp", line=dict(color="green", dash="dash")), row=1, col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Zone Air Temperatures'], name="Zone Air Temp", line=dict(color="indigo", dash="dot")), row=1, col=1, secondary_y=True)

        # Temperature plot
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Panel Temperatures'], name="Panel Fluid Temp", line=dict(color="firebrick")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Supply Pipe Temperatures'], name="Supply Pipe Fluid Temp", line=dict(color="chocolate", dash="dot")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Tank Temperatures'], name="Tank Fluid Temp", line=dict(color="orange")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Return Pipe Temperatures'], name="Return Pipe Fluid Temp", line=dict(color="blue", dash="dot")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Flow Rates'], name="Flow Rate", line=dict(color="purple"), opacity=0.5), row=2, col=1, secondary_y=True)
    
        # Heat Loss plot
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Supply Pipe Heat Losses'], name="Pipe Heat Loss", line=dict(color="chocolate", dash="dot")), row=3, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Tank Heat Losses'], name="Tank Heat Loss", line=dict(color="orange")), row=3, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Return Pipe Heat Losses'], name="Return Pipe Heat Loss", line=dict(color="blue", dash="dot")), row=3, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=results_df['Time'], y=results_df['Panel Heat Losses'], name="Panel Heat Loss", line=dict(color="firebrick")), row=3, col=1, secondary_y=True)
        
        # Update y-axes labels
        fig.update_yaxes(title_text="Irradiance (W/m^2)", secondary_y=False, row=1, col=1, title_font=dict(color="goldenrod"), tickfont=dict(color="goldenrod"))
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True, row=1, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False, row=2, col=1)
        fig.update_yaxes(title_text="Flow Rate (m^3/s)", secondary_y=True, row=2, col=1, title_font=dict(color="purple"), tickfont=dict(color="purple"))
        fig.update_yaxes(title_text="Heat Loss (J)", secondary_y=False, row=3, col=1)
        fig.update_yaxes(title_text="Panel Heat Loss (J)", secondary_y=True, row=3, col=1, title_font=dict(color="firebrick"), tickfont=dict(color="firebrick"))        
        
        # Create separate legend groups
        for i in range(1, 4):
            for trace in fig.select_traces(row=i):
                trace.update(legendgroup=f"group{i}")

        # Position legends
        fig.update_layout(
            height=1000,
            width=1200,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.1,
                traceorder="grouped"
            ),
            legend_tracegroupgap=210
        )

        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Start date must be before or equal to end date.")

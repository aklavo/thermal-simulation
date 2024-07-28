import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# st.set_page_config(
#     page_title="Thermal Simulation Report",
#     page_icon="☀️" 
# )
#st.logo("Images/image_with_text.png")
# Introduction Section
motivation = st.Page("Introduction/1-Motivation.py", title="Motivation", icon=":material/target:")
model_inputs = st.Page("Introduction/2-Model-Inputs.py", title="Model Inputs", icon=":material/input:")
the_model = st.Page("Introduction/3-The-Model.py", title="The Model", icon=":material/aq_indoor:")
the_sim = st.Page("Introduction/4-The-Simulation.py", title="The Simulation",  icon=":material/play_circle:")
# Simulation Results Section
basic_results = st.Page("Simulation-Results/1-Basic-Results.py", title="Basic Results", icon=":material/change_history:")
regressions = st.Page("Simulation-Results/2-Regressions.py", title="Regressions", icon=":material/square:")
sensitivity_analysis = st.Page("Simulation-Results/3-Sensitivity-Analysis.py", title="Sensitivity Analysis", icon=":material/pentagon:")

pg = st.navigation(
    {
        "Introduction": [motivation, model_inputs, the_model, the_sim],
        "Simulation Results": [basic_results, regressions, sensitivity_analysis],
    }
)


def sim_output_plot(df):
    with st.spinner("Plotting results..."):
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]], subplot_titles=("Weather", "Temperatures & Flow", "Heat Losses"))

        # Weather plot
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Solar Energy'], name="Irradiance", line=dict(color="goldenrod")), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Outside Air Temperatures'], name="Outside Air Temp", line=dict(color="green", dash="dash")), row=1, col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Zone Air Temperatures'], name="Zone Air Temp", line=dict(color="indigo", dash="dot")), row=1, col=1, secondary_y=True)

        # Temperature plot
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Panel Temperatures'], name="Panel Fluid Temp", line=dict(color="firebrick")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Supply Pipe Temperatures'], name="Supply Pipe Fluid Temp", line=dict(color="chocolate", dash="dot")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Tank Temperatures'], name="Tank Fluid Temp", line=dict(color="orange")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Return Pipe Temperatures'], name="Return Pipe Fluid Temp", line=dict(color="blue", dash="dot")), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Flow Rates'], name="Flow Rate", line=dict(color="purple"), opacity=0.5), row=2, col=1, secondary_y=True)
    
        # Heat Loss plot
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Supply Pipe Heat Losses'], name="Pipe Heat Loss", line=dict(color="chocolate", dash="dot")), row=3, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Tank Heat Losses'], name="Tank Heat Loss", line=dict(color="orange")), row=3, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Return Pipe Heat Losses'], name="Return Pipe Heat Loss", line=dict(color="blue", dash="dot")), row=3, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Panel Heat Losses'], name="Panel Heat Loss", line=dict(color="firebrick")), row=3, col=1, secondary_y=True)
        
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
        return fig
pg.run()

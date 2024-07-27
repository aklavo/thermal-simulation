import streamlit as st
import numpy as np
import pandas as pd

st.logo("Images/image_with_text.png")
# Introduction Section
motivation = st.Page("Introduction/1-Motivation.py", title="Motivation", icon=":material/target:")
model_inputs = st.Page("Introduction/2-Model-Inputs.py", title="Model Inputs", icon=":material/input:")
the_model = st.Page("Introduction/3-The-Model.py", title="The Model", icon=":material/aq_indoor:")
the_sim = st.Page("Introduction/4-The-Simulation.py", title="The Simulation",  icon=":material/play_circle:")
# Simulation Results Section
no_flow_no_loss = st.Page("Simulation-Results/1-No-Flow-No-Loss.py", title="No Flow & No Losses", icon=":material/change_history:")
no_flow = st.Page("Simulation-Results/2-No-Flow.py", title="No Flow", icon=":material/square:")
constant_flow = st.Page("Simulation-Results/3-Constant-Flow.py", title="Constant Flow", icon=":material/pentagon:")
controlled_flow = st.Page("Simulation-Results/4-Controlled-Flow.py", title="Controlled Flow", icon=":material/hexagon:")

pg = st.navigation(
    {
        "Introduction": [motivation, model_inputs, the_model, the_sim],
        "Simulation Results": [no_flow_no_loss, no_flow, constant_flow, controlled_flow],
    }
)

pg.run()

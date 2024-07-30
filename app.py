import streamlit as st

st.set_page_config(
    page_title="Thermal Simulation Report",
    page_icon="☀️", 
    layout="wide",
)
#st.logo("Images/image_with_text.png")
# Introduction Section
motivation = st.Page("Introduction/1-Motivation.py", title="Motivation", icon=":material/target:")
model_inputs = st.Page("Introduction/2-Model-Inputs.py", title="Model Inputs", icon=":material/input:")
the_model = st.Page("Introduction/3-The-Model.py", title="The Model", icon=":material/aq_indoor:")
the_sim = st.Page("Introduction/4-The-Simulation.py", title="The Simulation",  icon=":material/play_circle:")
# Simulation Results Section
basic_results = st.Page("Simulation-Results/1-Basic-Results.py", title="Basic Results", icon=":material/change_history:")
data_analysis = st.Page("Simulation-Results/2-Data-Analysis.py", title="Data Analysis", icon=":material/square:")
data_science = st.Page("Simulation-Results/3-Data-Science.py", title="Black Box Models", icon=":material/pentagon:")
# Conclusion Section
conclusion = st.Page("Conclusion/1-Conclusion.py", title="Conclusion", icon=":material/lightbulb:")

pg = st.navigation(
    {
        "Introduction": [motivation, model_inputs, the_model, the_sim],
        "Simulation Results": [basic_results, data_analysis, data_science],
        "Conclusion": [conclusion],
    }
)

pg.run()

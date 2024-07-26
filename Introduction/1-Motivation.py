import streamlit as st
st.set_page_config(
    page_title="Thermal Simulation Report",
    page_icon="☀️" 
)

st.header("Passive Logic's Prompt")
'''
Write a simple software simulation of the following system.  
'''
st.image("system-diagram.jpg")
'''
Minimum Requirements:
1. The system should simulate the heat transfer from a solar panel to a storage tank
2. Use whichever coding language you wish
3. We will evaluate thermodynamic correctness, code approach, and results.
'''
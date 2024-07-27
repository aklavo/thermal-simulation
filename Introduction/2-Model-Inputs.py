import streamlit as st
import inputs
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Thermal Simulation Report",
    page_icon="☀️" 
)

st.header("Model Inputs")
st.subheader("Weather")
'''
Weather data for this simulation was obtained from the NREL's 
[National Solar Radiation Database](https://developer.nrel.gov/docs/solar/nsrdb/psm3-5min-download/).
This simulation will take place in 2022, Westminster, CO. **Global horizontal irradenace (GHI), clear sky GHI, 
and outdoor dry-bulb temperature** will pulled at resolution of 5-min intervals. Indoor temperatures was assumed
to be a constant 21.11°C (70°F) during the simulation.

Data is requested via an API call which returns a csv. This is then read into a pandas dataframe and visualized below.
'''

get_weather = st.button("Get Weather Data", type="primary")
if get_weather:
    with st.spinner("Fetching weather data..."):
        # Weather parameters
        year = '2022'
        lat = '39.8818'
        lon = '-105.0552'
        interval = '5'
        attributes = 'ghi,clearsky_ghi,air_temperature'
        sim_step = '5min'
        weather_df = inputs.get_weather_data(lat, lon, year, interval, attributes,sim_step) # 5min data

if 'weather_df' in locals():
    with st.spinner("Plotting weather data..."):
 
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=weather_df.index, y=weather_df['GHI'], name="GHI"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=weather_df.index, y=weather_df['Clearsky GHI'], name="Clearsky GHI"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=weather_df.index, y=weather_df['Temperature'], name="Temperature"),
            secondary_y=True,
        )

        fig.update_layout(
            xaxis_title="Time",
        )
        
        fig.update_yaxes(title_text="Irradiance (W/m^2)", secondary_y=False)
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)
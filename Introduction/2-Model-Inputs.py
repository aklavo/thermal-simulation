import streamlit as st
import inputs
import numpy as np
import plotly.graph_objects as go
import pandas as pd
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
This simulation will take place in 2022, Westminster, CO. **Global horizontal irradiance (GHI), clear sky GHI, 
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
        inputs.get_weather_data(lat, lon, year, interval, attributes,sim_step) # 5min data
        weather_df = pd.read_parquet('Outputs/weather_data.parquet')
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

st.subheader("Geometry")
'''
The geometry of each component of the system is defined below.
##### Solar Panel
'''

panel_geometry = '''
    panel_length = 2 # [m]
    panel_width = 1 # [m]
    panel_height = 0.1 # [m]
'''
st.code(panel_geometry, language='python')
panel_length = 2  # [m]
panel_width = 1  # [m]
panel_height = 0.1  # [m]

# Define the vertices of the rectangle
vertices = [
    [0, 0, 0],
    [panel_length, 0, 0],
    [panel_length, panel_width, 0],
    [0, panel_width, 0],
    [0, 0, panel_height],
    [panel_length, 0, panel_height],
    [panel_length, panel_width, panel_height],
    [0, panel_width, panel_height]
]

# Define the x, y, z coordinates for each vertex
x = [vertex[0] for vertex in vertices]
y = [vertex[1] for vertex in vertices]
z = [vertex[2] for vertex in vertices]

# Define the faces of the rectangle using vertex indices
faces = [
    [0, 1, 5, 4],  # Bottom face
    [2, 3, 7, 6],  # Top face
    [0, 3, 7, 4],  # Left face
    [1, 2, 6, 5],  # Right face
    [0, 1, 2, 3],  # Front face
    [4, 5, 6, 7]   # Back face
]

# Define the I, J, K vertex indices for the triangles forming the faces
I = []
J = []
K = []

# Each face is divided into two triangles
for face in faces:
    I += [face[0], face[0]]
    J += [face[1], face[2]]
    K += [face[2], face[3]]

# Create a Mesh3d plot
panel_fig = go.Figure(data=[
    go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=I,
        j=J,
        k=K,
        opacity=0.5,
        color='blue'
    )
])

# Set the layout to ensure all axes go to panel_length
panel_fig.update_layout(
    scene=dict(
        xaxis=dict(
            title='Length [m]',
            range=[0, panel_length]
        ),
        yaxis=dict(
            title='Width [m]',
            range=[0, panel_length]
        ),
        zaxis=dict(
            title='Height [m]',
            range=[0, panel_width]
        )
    )
)

st.plotly_chart(panel_fig, use_container_width=True)

'''
##### Pipes
Both the supply and return pipes are the size dimensions.
'''

panel_geometry = '''
    pipe_radius = 0.02 # [m]
    pipe_length = 2 # [m]
'''
st.code(panel_geometry, language='python')
pipe_radius = 0.02 # [m]
pipe_length = 2 # [m]

# Create the cylinder
theta = np.linspace(0, 2 * np.pi, 100)
z = np.linspace(0, pipe_length, 100)
theta, z = np.meshgrid(theta, z)
x = pipe_radius * np.cos(theta)
y = pipe_radius * np.sin(theta)

# Create the plot
pipe_fig = go.Figure()

# Add the cylindrical surface
pipe_fig.add_trace(
    go.Surface(
        x=x,
        y=z,
        z=y,
        surfacecolor=np.ones_like(z),  # Dummy surfacecolor array for single color
        colorscale=[[0, "orange"], [1, "orange"]],  # Single color
        showscale=False,  # Hide the color scale
        opacity=0.7,
    )
)

# Set the layout to ensure all axes go to pipe_length
pipe_fig.update_layout(
    scene=dict(
        xaxis=dict(
            title='Height [m]',
            range=[-pipe_radius*4, pipe_radius*4]
        ),
        yaxis=dict(
            title='Length [m]',
            range=[0, pipe_length]
        ),
        zaxis=dict(
            title='Width [m]',
            range=[-pipe_radius*4, pipe_radius*4]
        ),
        camera=dict(
            eye=dict(x=1.5, y=1.1, z=0)  # Adjust the camera to get the desired view
        )
    )
)

st.plotly_chart(pipe_fig, use_container_width=True)

'''
##### Tank
'''

panel_geometry = '''
    tank_radius = 0.5 # [m]
    tank_height = 2 # [m]
'''
st.code(panel_geometry, language='python')
tank_radius = 0.5 # [m]
tank_height = 2 # [m]

# Create the cylinder
theta = np.linspace(0, 2 * np.pi, 100)
z = np.linspace(0, tank_height, 100)
theta, z = np.meshgrid(theta, z)
x = tank_radius * np.cos(theta)
y = tank_radius * np.sin(theta)

# Create the plot
pipe_fig = go.Figure()

# Add the cylindrical surface
pipe_fig.add_trace(
    go.Surface(
        x=x,
        y=y,
        z=z,
        surfacecolor=np.ones_like(z),  # Dummy surfacecolor array for single color
        colorscale=[[0, "red"], [1, "red"]],  # Single color
        showscale=False,  # Hide the color scale
        opacity=0.7,
    )
)

# Set the layout to ensure all axes go to tank_height
pipe_fig.update_layout(
    scene=dict(
        xaxis=dict(
            title='Height [m]',
            range=[-tank_radius, tank_radius]
        ),
        yaxis=dict(
            title='Width [m]',
            range=[-tank_radius, tank_radius]
        ),
        zaxis=dict(
            title='Length [m]',
            range=[0, tank_height]
        ),
        camera=dict(
            eye=dict(x=1, y=1, z=2)  # Adjust the camera to get the desired view
        )
    )
)

st.plotly_chart(pipe_fig, use_container_width=True)


st.subheader("Physical Constants")
'''
The physical constant used in this simulation are defined below. In reality many of these values
vary with the temperature and pressure of the system. Future work would more dynamic physical
properties.
'''

constants = '''
    water_density = 100 # density of water at 4°C [kg/m^3]
    water_specific_heat = 4184 # specific heat of water at 20°C [J/kg°C]
    air_density = 0.985 # density of air at 5000ft, 70°F, 29.7 inHg, 47% RH [kg/m^3]
    air_specific_heat = 1.006 # specific heat of air at 20°C [J/kg°C]
    air_heat_transfer_coeff_inside = 10 # heat transfer coefficient of air [W/m^2*K]
    air_heat_transfer_coeff_outside = 50 # heat transfer coefficient of air [W/m^2*K]
    water_in_pipe_heat_transfer_coeff =  1000 # heat transfer coefficient of water in pipe [W/m^2*K]
    sigma = 5.670367e-8 # Stefan-Boltzmann constant [W/m^2*K^4]
    k_stainless_steal = 17 # Thermal conductivity of stainless steel [W/m*K]
    k_glass = 1 # Thermal conductivity of glass [W/m*K]
    k_cast_iron = 80 # Thermal conductivity of cast iron [W/m*K]
    k_fiberglass = 0.036 # Thermal conductivity of fiberglass [W/m*K]
'''
st.code(constants, language='python')
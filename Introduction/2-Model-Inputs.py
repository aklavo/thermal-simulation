import streamlit as st
import inputs
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

st.header("Model Inputs")
'''
This model takes three categories of inputs, weather,  geometry, and physical properties.
'''
st.subheader("Weather")
'''
Weather data for this simulation was obtained from the NREL's 
[National Solar Radiation Database](https://developer.nrel.gov/docs/solar/nsrdb/psm3-5min-download/).
The data available in this report is from 2022, Westminster, CO. **Global horizontal irradiance (GHI), clear sky GHI, 
and outdoor dry-bulb temperature** are used at a resolution of 5-min intervals. Indoor temperatures was assumed
to be a roughly 21.11°C (70°F). A random deviation of ±0.5°C was added to the indoor temperature every time-step to simulate
subtle changes in internal loads.

The method responsible for pulling the weather data is located in the `inputs.py` file. In that file the `get_weather_data()` takes
in the latitude and longitude of the location, the year, the interval, attributes to be pulled, and a resampling frequency. The method
sends a GET request to the NREL API. The csv formatted data returned is then cleaned and saved as a parquet file in the `Outputs` folder.
Below is a years worth of GHI, clearksy GHI, and outside air temperature data plotted.
'''
weather_df = pd.read_parquet('Outputs/weather_data.parquet')

@st.cache_data  
def plot_weather(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=weather_df.index, y=weather_df['GHI'], name="GHI", line=dict(color="goldenrod")),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=weather_df.index, y=weather_df['Clearsky GHI'], name="Clearsky GHI", visible='legendonly'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=weather_df.index, y=weather_df['Temperature'], name="Temperature", line=dict(color="green", dash="dash")),
        secondary_y=True,
    )

    fig.update_layout(
        xaxis_title="Time",
        hovermode="x unified"
    )
    
    fig.update_yaxes(title_text="Irradiance (W/m^2)", secondary_y=False, title_font=dict(color="goldenrod"), tickfont=dict(color="goldenrod"))
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True, title_font=dict(color="green"), tickfont=dict(color="green"))
    return fig
    
with st.spinner("Plotting weather data..."):
    st.plotly_chart(plot_weather(weather_df), use_container_width=True)

st.subheader("Geometry")
'''
The geometries of each component were simplified to lower the complexity of heat transfer and aid in the speed of development of
the project. With more time, these geometries would be refined to more accurately model real world devices. The geometry of each component of the system is defined below.
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


st.subheader("Physical Properties")
'''
The physical properties used in this simulation are defined below. In reality many of these values
vary with the temperature and pressure of the system. Future work would incorporate more dynamic physical
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
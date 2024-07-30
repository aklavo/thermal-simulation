# Solar Water Heater Simulation

## Passive Logic Prompt:

Write a simple software simulation of the following system.
Minimum Requirements:
1. The system should simulate the heat transfer from a solar panel to a storage tank
2. Use whichever coding language you wish
3. We will evaluate thermodynamic correctness, code approach, and results.


## System Diagram
![system-diagram](Images/system-diagram.jpg)

## Project Description
This repository contains three python files, `main.py`, `input.py`, and `components.py`.

This project can be viewed in webapp format [here](https://thermal-simulation.streamlit.app/The-Simulation).

### input.py
This file contains a single function called `get_weather_data()` which connects to the NREL's National Solar Radiation Database (NSRDB) API and pulls  weather data for the desired location and return a pandas dataframe.

### components.py
This file contains the model components of the system. All model components are defined as classes. The classes are:
- `Fluid`
- `Material`
- `Sun`
- `Container`
    - `Tank`
    - `SolarPanel`
    - `Pipe`
- `Pump`
All physics based heat transfer equations are implemented in the classes.

### main.py
This file contains the main simulation loop. It is responsible for initializing model components, calling `get_weather_data()` based on desired inputs, running the simulation, and producing a simple plot and csv of simulation results.

## Installation
#### Manual Installation
After cloning the repo, install the necessary packages to your environment by running command below:  

`pip install -r requirements.txt`

Execute the simulation by running the command:  

`python main.py`  

By default the simulation will run with the following parameters:
- start='2022-07-01 00:00:00'
- end='2022-07-03 23:55:00'
- sim_step='5min'
- clouds=1 (1 = GHI, -1 = Clearsky GHI, 0 = no sun)
- heat_loss=True (True = heat loss, False = no heat loss)
- pump_control=2 (0 = no pump, 1 = constant pump, 2 = variable pump)
- flow_rate_max=0.00063 (m^3/s)
- DEV=False (True = just plt.show() output graph, False = save png and parquet to Outputs folder)

 DEV mode will run `plt.show()` while `DEV == false` will save a png of the graph output and parquet file of simulation time-series. 
 
To kill the DEV process simply exit the graphical pop-up window.

#### Docker Installation
After cloning the repo, build the docker image by running the command:  

`docker build -t solar-water-heater-simulation .`  

`docker run -it solar-water-heater-simulation`

## Simulation Assumptions

### Basic Assumptions
- The storage tank is a perfect cylinder.
- The panel is a rectangle of water. 
- The flow of a pump is modelled based on the transfer of energy through fluid mixing and
a flow rate.
- All pipe surface area is in the outdoor environment. 

### Thermodynamic Assumptions
- The tank is in thermal equilibrium with the indoor zone temperature at sim start.
- The panel and pipes are in thermal equilibrium with the outdoor zone temperature at sim start.
- 80% of energy from the sun is transferred into the panel.
- Mixing is assumed to be instantaneous, thus T_final is always reached after each time-step.
- The indoor temperature is constant despite the tanks heat loss (there's a really good cooling system in there lol)
- Air has a constant convective heat transfer coefficient of 10 W/m^2K inside and 50 W/m^2K outside.
- Heat loss due to radiation is included in the heat transfer coefficient of air.
- All heat loss is 1D steady state heat transfer.

### Operational Assumptions
- The pump is sized such that it can overcome the system head and produce the constant flow defined.
- The speed of the pump is constant and instantaneous.

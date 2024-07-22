# thermal-simulation-PassiveLogic


## Name
Solar Water Heater Simulation

## Description
PassiveLogical Prompt:

Write a simple software simulation of the following system.
Minimum Requirements:
1. The system should simulate the heat transfer from a solar panel to a storage tank
2. Use whichever coding language you wish
3. We will evaluate thermodynamic correctness, code approach, and results.


## Visuals
![system-diagram](system-diagram.jpg)

## Installation
The packages require to run this code can be installed with the following command:  
`pip install -r requirements.txt`

## Usage
Execute the similation by running the command:  
`python main.py`  
Console output will prompt the user to execute the simulation in DEV mode or not. DEV mode will run plt.show() while `DEV == false` will save a png of the graph output and csv of simulation timeseries. Both modes print system variables each timestep. 

To kill the DEV process simply exit the graphical pop-up window.



# Simulation Assumptions

### Basic Assumptions
- The storage tank is a perfect cylinder.
- The panel is a rectangle of water. 
- The flow of a pump is modelled based on the transfer of energy through fluid mixing and
a flow rate.
- All pipe surface area is in the outdoor environment. 

### Thermodynamic Assumptions
- The tank is in thermal equalibrium with the indoor zone temperature at sim start.
- The panel and pipes are in thermal equalibrium with the outdoor zone temperature at sim start.
- 80% of energy from the sun is transferred into the panel.
- Mixing is assumed to be instantaneous, thus T_final is always reached after each timestep.
- The indoor temperature is constant dispate the tanks heat loss (there's a really good cooling system in there lol)
- Air has a constant convective heat transfer coefficient of 10 W/m^2K inside and 50 W/m^2K outside.
- Heat loss due to radiation is included in the heat transfer coefficent of air.
- All heat loss is 1D steady state heat transfer.

### Operational Assumptions
- The pump is sized such that it can overcome the system head and produce the constant flow defined.
- The speed of the pump is constant and instantaneous.

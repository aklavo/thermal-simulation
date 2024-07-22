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

## Notes
All units are in SI.

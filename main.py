import math
import matplotlib.pyplot as plt
import numpy as np
import compenents as comps

# Constants
solar_irradiance = 1000 # W/m^2
panel_efficiency = 0.6 # 60% efficiency
intial_temp = 20 # C
intial_flow = 0.05 # m^3/s
intial_Q = 0 # W (J/s)
panel_area = 2 # m^2
pipe_1_len = 5 # m
pipe_2_len = 5 # m
pipe_3_len = 10 # m
pipe_diameter = 0.02 # m
tank_volume = 3 # m^3

# Components
Panel = comps.SolarPanel(panel_area, intial_temp, intial_temp, intial_flow, intial_flow, intial_Q, intial_Q) # solar water heating panel
Pipe_1 = comps.Pipe(pipe_1_len, pipe_diameter, intial_temp, intial_temp, intial_flow, intial_flow, intial_Q, intial_Q) # piping between panel and pump
Pump = comps.Pump(intial_temp,intial_temp, intial_flow, intial_flow, intial_Q, intial_Q) # circulation pump
Pipe_2 = comps.Pipe(pipe_2_len, pipe_diameter, intial_temp, intial_temp, intial_flow, intial_flow, intial_Q, intial_Q) # piping between pump and tank 
Tank = comps.StorageTank(tank_volume, intial_temp, intial_temp, intial_flow, intial_flow, intial_Q, intial_Q) # hot water storage
Pipe_3 = comps.Pipe(pipe_3_len, pipe_diameter, intial_temp, intial_temp, intial_flow, intial_flow, intial_Q, intial_Q) # piping between tank and panel 

# Lists to store simulation results
panel_temperatures = []
tank_temperatures = []
total_heat_inputs = []
total_heat_outputs = []
total_heat_losses = []
panel_heat_inputs = []

# Simulation parameters
hours = 24
time_step = hours * 3600 # seconds


# Simulation loop
for i in range(time_step):
    
    panel_temperatures.append(Panel.temp_out)
    tank_temperatures.append(Tank.temp_in)
    
x = range(time_step) # time

# Create the plot
fig, ax = plt.subplots()

ax.plot(x, panel_temperatures, label='Panel Temp')
ax.plot(x, tank_temperatures, label='Tank Temp')
ax.set_title('Solar Water Heating Simulation')
ax.set_xlabel('Time (sec)')
ax.set_ylabel('Temperature (°C)')

ax.legend()
plt.show()

# # Constants
# solar_irradiance = 1000 # W/m^2
# panel_efficiency = 0.6 # 60% efficiency
# panel_area = 2 # m^2
# panel_heat_capacity = 1000 # J/(kg*K)
# panel_mass = 50 # kg
# panel_initial_temperature = 20 # deg C
# tank_volume = 100 # liters
# tank_heat_capacity = 4184 # J/(kg*K)
# tank_mass = 50 # kg
# tank_initial_temperature = 10 # deg C
# pump_flow_rate = 0.05 # m^3/h
# pump_power = 100 # W
# pipe_length = 5 # m
# pipe_diameter = 0.02 # m
# pipe_heat_transfer_coefficient = 10 # W/(m^2*K)

# # Simulation parameters
# time_step = 3600 # 1 hour
# num_steps = 24 # 24 hours

# # Lists to store simulation results
# panel_temperatures = []
# tank_temperatures = []
# total_heat_inputs = []
# total_heat_outputs = []
# total_heat_losses = []
# panel_heat_inputs = []

# # Simulation loop
# for i in range(num_steps):
#     # Update temperatures
#     panel_temperatures.append(panel_initial_temperature)
#     tank_temperatures.append(tank_initial_temperature)
    
#     panel_heat_loss = panel_area * (1 - panel_efficiency) * solar_irradiance
#     panel_heat_input = panel_area * panel_efficiency * solar_irradiance
#     panel_heat_output = panel_mass * panel_heat_capacity * (panel_initial_temperature - tank_initial_temperature)
    
#     tank_heat_input = panel_heat_output
#     tank_heat_loss = (tank_initial_temperature - 5) * tank_volume * tank_heat_capacity
    
#     pump_heat_output = pump_flow_rate * tank_mass * tank_heat_capacity * (tank_initial_temperature - 5)
#     pipe_heat_loss = (math.pi * pipe_diameter * pipe_length * pipe_heat_transfer_coefficient *
#                       (tank_initial_temperature - 5 + panel_initial_temperature - 5) / 2)
    
#     total_heat_loss = panel_heat_loss + tank_heat_loss + pipe_heat_loss
    
#     panel_initial_temperature += (panel_heat_input - panel_heat_output - panel_heat_loss) / (panel_mass * panel_heat_capacity)
#     tank_initial_temperature += (tank_heat_input - pump_heat_output - tank_heat_loss) / (tank_mass * tank_heat_capacity)
    
#     total_heat_input = panel_heat_input + tank_heat_input
#     total_heat_output = pump_heat_output
    
#     total_heat_inputs.append(total_heat_input / 1000) # Convert to kW
#     total_heat_outputs.append(total_heat_output / 1000) # Convert to kW
#     total_heat_losses.append(total_heat_loss / 1000) # Convert to kW
#     panel_heat_inputs.append(panel_heat_input / 1000) # Convert to kW

# # Create a graph of the tank temperature and panel heat input over time
# fig, ax1 = plt.subplots()

# color = 'tab:red'
# ax1.set_xlabel('Time (hours)')
# ax1.set_ylabel('Tank temperature (deg C)', color=color)
# ax1.plot(range(num_steps), tank_temperatures, color=color)
# ax1.tick_params(axis='y', labelcolor=color)

# ax2 = ax1.twinx()

# color = 'tab:blue'
# ax2.set_ylabel('Panel heat input (kW)', color=color)
# ax2.plot(range(num_steps), panel_heat_inputs, color=color)
# ax2.tick_params(axis='y', labelcolor=color)

# # fig.tight_layout()
# fig.show()


# # # Print simulation results
# # print("Panel temperatures:", panel_temperatures)
# # print("Tank temperatures:", tank_temperatures)
# # print("Total heat inputs:", total_heat_inputs)
# # print("Total heat outputs:", total_heat_outputs)
# # print("Total heat losses:", total_heat_losses)

#!/usr/bin/env python
"""
File: components.py
Author: Andrew Klavekoske
Last Updated: 2024-07-22

Description: This file stores the classes for the components of the
thermal simulation.
"""

import math
from abc import ABC, abstractmethod
#################################################
# Q = m * c * dT
# T_f = ((m1*T1)+(m2*T2))/(m1 + m2)
#
# Conduction: Q = k * A * (T_hot - T_cold)/d
# Convection: Q = h * A * (T_hot - T_cold)
# Radiation: Q = sig * A*  (T_hot - T_cold)^4
#################################################


# ------------------------------- Fluids -------------------------------
class Fluid:
  def __init__(self,density, specific_heat, temperature=20, container=None):
    self.density = density
    self.specific_heat = specific_heat
    self.temperature = temperature # initial temperature of water 20°C
    self.container = container # container object if fluid is in a container


  def volume(self):
    return self.container.volume() if self.container else 0
  
  def mass(self):
    return self.density*self.volume()
  
  def to_kelvin(self):
    return self.temperature + 273.15
  
  def add_container(self, container):
    self.container = container
  
  # T2 = T1 + Q/mc
  def add_energy(self, energy):
    self.temperature += energy/(self.specific_heat*self.mass())

  def lose_energy(self, energy):
    print(f"Temperaure Change: {energy/(self.specific_heat*self.mass())}")
    if energy > 0:
      self.temperature -= energy/(self.specific_heat*self.mass())
    else:
      self.temperature += energy/(self.specific_heat*self.mass())

  # Heat lossed by fluid_1 + Heat gained by fluid_2 = 0
  def mix_with(self, fluid, flow_rate, time):
    mass_1 = self.mass()
    mass_2 = fluid.density*flow_rate*time
    mass_3 = mass_1 + mass_2
    temp_1 = self.temperature
    temp_2 = fluid.temperature

    # update both fluid temperature to final temperatre
    self.temperature = ((mass_1*temp_1)+(mass_2*temp_2))/(mass_3)  
    fluid.temperature = self.temperature  

# ------------------------------- Surfaces -------------------------------
class Material:
  def __init__(self, heat_transfer_coefficient, surface_temperature, thickness):
    self.heat_transfer_coefficient = heat_transfer_coefficient
    self.surface_temperature = surface_temperature 
    self.thickness = thickness

# ------------------------------- The Sun -------------------------------
class Sun:
  def __init__(self):
    self.irradiance = 0 # intal irradiance in W/m^2 or J/s*m^2

  def energy(self, time, area):
    return self.irradiance*time*area
  
# ------------------------------- Containers -------------------------------    
class Container(ABC):
  def __init__(self, fluid, material):
    self.fluid = fluid
    self.material = material

  @abstractmethod
  def volume(self):
    pass

  @abstractmethod
  def surface_area(self):
    pass

  def simple_heat_loss(self,temp_loss):
    self.fluid.temperature -= temp_loss
    
  def conduction_loss(self, fluid_2, time):
    temp_1 = self.fluid.temperature
    temp_2 = fluid_2.temperature
    if abs(temp_1-temp_2) < 0.01:
      return 0
    else:
      thickness = self.material.thickness
      heat_transfer_coefficient = self.material.heat_transfer_coefficient
      area = self.surface_area()
      #print(f"Conduction Loss: {area:.3f} * {heat_transfer_coefficient} * ({temp_1:.3f} - {temp_2:.3f})/ {thickness} * {time}")
      heat_energy = (heat_transfer_coefficient*area*(temp_1-temp_2)/thickness)*time

    return heat_energy  #if + self.temp is hotter, if - fluid2.temp is hotter
 
  def convection_loss(h, A, delta_T):
      return h * A * delta_T
  
  def radiation_loss(epsilon, sigma, A, T_surface, T_environment):
      return epsilon * sigma * A * (T_surface**4 - T_environment**4)

  
# ------------------------------- Solar Panel -------------------------------
class SolarPanel(Container):
  def __init__(self, fluid, material, length, width, hieght):
    super().__init__(fluid, material)
    self.length = length
    self.width = width
    self.height = hieght
    self.efficiency = 0.7 # % of sunlight coverted to heat <-- this is a heat transfer bandaid for now

  def volume(self):
    return self.length * self.width * self.height
  
  def surface_area(self):
    top_bottom = 2*(self.length * self.width)
    left_right = 2*(self.length * self.height)
    front_back = 2*(self.width * self.height)
    return top_bottom + left_right + front_back
  
  def solar_area(self):
    return self.length * self.width
    
 # ------------------------------- Water Tank -------------------------------   
class Tank(Container):
  def __init__(self, fluid, material, radius, height):
    super().__init__(fluid, material)
    self.radius = radius
    self.height = height

  def volume(self):
    return math.pi*self.height*self.radius**2
  
  def surface_area(self):
    return (2*math.pi*self.radius**2)+(2*math.pi*self.radius*self.height)
    
# ------------------------------- Pipe -------------------------------   
class Pipe(Container):
  def __init__(self, fluid, material, radius, length):
    super().__init__(fluid, material)
    self.radius = radius
    self.length = length

  def volume(self):
    return math.pi*self.length*self.radius**2
  
  def surface_area(self):
    return (2*math.pi*self.radius*self.length)



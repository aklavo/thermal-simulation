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
  def __init__(self, density, specific_heat, temperature=20, container=None, heat_transfer_coefficient=None):
    self.density = density
    self.specific_heat = specific_heat
    self.temperature = temperature # initial temperature of water 20°C
    self.container = container # container object if fluid is in a container
    self.heat_transfer_coefficient = heat_transfer_coefficient

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
    print(f"Temperaure Change: {energy/(self.specific_heat*self.mass()):.3f}")
    if energy > 0:
      self.temperature -= energy/(self.specific_heat*self.mass())
    else:
      self.temperature += energy/(self.specific_heat*self.mass())

  # heat lossed by fluid_1 + Heat gained by fluid_2 = 0
  def mix_with(self, fluid, flow_rate, time):
    mass_1 = self.mass()
    mass_2 = fluid.density*flow_rate*time
    mass_3 = mass_1 + mass_2
    temp_1 = self.temperature
    temp_2 = fluid.temperature

    # update both fluid temperature to final temperatre
    if flow_rate > 0:
      self.temperature = ((mass_1*temp_1)+(mass_2*temp_2))/(mass_3)
      fluid.temperature = self.temperature
      return 

# ------------------------------- Surfaces -------------------------------
class Material:
  def __init__(self, thermal_conductivity, surface_temperature, thickness):
    self.thermal_conductivity = thermal_conductivity
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
  def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid):
    self.fluid = fluid
    self.material = material
    self.surroundings = surroundings # another fluid object (air)

  @abstractmethod
  def volume(self):
    pass

  @abstractmethod
  def overall_heat_transfer_coefficient(self):
    pass

  def temp_loss(self,temp_loss):
    self.fluid.temperature -= temp_loss # used to simulate simple heat loss

  def heat_loss(self, surface_area, time):

    heat_loss = ((self.fluid.temperature - self.surroundings.temperature) *
                 surface_area *
                 self.overall_heat_transfer_coefficient(self.surroundings) *
                 time)

    return heat_loss
  
  def radiation_loss(epsilon, sigma, A, T_surface, T_environment):
      return epsilon * sigma * A * (T_surface**4 - T_environment**4)

  
# ------------------------------- Solar Panel -------------------------------
class SolarPanel(Container):
  def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid, length, width, hieght):
    super().__init__(fluid, material, surroundings)
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
  
  def overall_heat_transfer_coefficient(self):
    pass
    
# ------------------------------- Water Tank -------------------------------   
class Tank(Container):
  def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid, radius, height,  insulation: Material):
    super().__init__(fluid, material, surroundings)
    self.radius = radius
    self.height = height
    self.insulation = insulation

  def volume(self):
    return math.pi*self.height*self.radius**2
  
  def surface_area_walls(self):
    return (2*math.pi*self.radius*self.height)
  
  def surface_area_top(self):
    return (math.pi*self.radius**2)
  
  #inner diameter of tank
  def diameter_1(self):
    return self.radius * 2
  
  #outer diameter of tank
  def diameter_2(self):
    return (self.radius + self.material.thickness) * 2
  
  #outer diameter of tank + insulation
  def diameter_3(self):
    return (self.radius + self.material.thickness + self.insulation.thickness) * 2
  
  # just tank walls
  def overall_heat_transfer_coefficient(self, air: Fluid):

    wall_fluid_term = (self.diameter_3())/(self.diameter_1()*self.fluid.heat_transfer_coefficient)
    wall_material_term = (self.diameter_3()*math.log(self.diameter_2()/self.diameter_1()))/(self.material.thermal_conductivity) 
    wall_insulation_term = (self.diameter_3()*math.log(self.diameter_3()/self.diameter_1()))/(self.insulation.thermal_conductivity)
    wall_air_term = 1/air.heat_transfer_coefficient

    # top_fluid_term = 1/self.fluid.heat_transfer_coefficient
    # top_material_term = self.material.thickness/self.material.thermal_conductivity
    # top_insulation_term = self.insulation.thickness/self.insulation.thermal_conductivity
    # top_air_term = 1/air.heat_transfer_coefficient

    side_h = 1/(wall_fluid_term + wall_material_term + wall_insulation_term + wall_air_term)
    #top_h = 1/(top_fluid_term + top_material_term + top_insulation_term + top_air_term)

    overall_heat_transfer_coefficient = side_h #+ top_h

    return overall_heat_transfer_coefficient
    
# ------------------------------- Pipe --------------------------------------   
class Pipe(Container):
  def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid, radius, length, insulation: Material):
    super().__init__(fluid, material, surroundings)
    self.radius = radius
    self.length = length
    self.insulation = insulation

  def volume(self):
    return math.pi*self.length*self.radius**2
  
  def surface_area(self):
    return (math.pi*self.diameter_3()*self.length) # outer surface area
  
  #inner diameter of pipe
  def diameter_1(self):
    return self.radius * 2
  
  #outer diameter of pipe
  def diameter_2(self):
    return (self.radius + self.material.thickness) * 2
  
  #outer diameter of pipe + insulation
  def diameter_3(self):
    return (self.radius + self.material.thickness + self.insulation.thickness) * 2


  def overall_heat_transfer_coefficient(self, air: Fluid):
    # diameter ratios are necessary to correctly account for the cylindrical geometry and the logarithmic nature of radial heat conduction
    fluid_term = (self.diameter_3())/(self.diameter_1()*self.fluid.heat_transfer_coefficient)
    material_term = (self.diameter_3()*math.log(self.diameter_2()/self.diameter_1()))/(self.material.thermal_conductivity) 
    insulation_term = (self.diameter_3()*math.log(self.diameter_3()/self.diameter_1()))/(self.insulation.thermal_conductivity)
    air_term = 1/air.heat_transfer_coefficient

    overall_heat_transfer_coefficient = 1/(fluid_term + material_term + insulation_term + air_term)

    return overall_heat_transfer_coefficient
   
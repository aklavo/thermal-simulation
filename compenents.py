import math

#################################################
# Q = m * c * dT
# T_f = ((m1*T1)+(m2*T2))/(m1 + m2)
#
# Conduction: Q = k * A * (T_hot - T_cold)^(t/d)
# Convection: Q = h * A * (T_hot - T_cold)
# Radiation: Q = sig * A*  (T_hot - T_cold)^4
#################################################


# ------------------------------- Fluids -------------------------------
class Fluid:
  def __init__(self,volume, density, specific_heat, temperature=20):
    self.volume = volume 
    self.density = density
    self.specific_heat = specific_heat
    self.temperature = temperature # initial temperature of water 20°C

  def mass(self, volume):
    return self.density*volume
  
  def volume(self, mass):
    return mass/self.density
  
  def to_kelvin(self):
    return self.temperature + 273.15
  
  # T2 = T1 + Q/mc
  def add_energy(self, energy, mass):
    self.temperature += energy/(self.specific_heat*mass)

  # Heat lossed by fluid_1 + Heat gained by fluid_2 = 0
  def mix_with(self, fluid):
    m_1 = self.mass(self.volume)
    m_2 = fluid.mass(fluid.volume)
    m_3 = m_1 + m_2
    T_1 = self.temperature
    T_2 = fluid.temperature
    self.temperature = ((m_1*T_1)+(m_2*T_2))/(m_3)  
    fluid.temperature = self.temperature  

# ------------------------------- The Sun -------------------------------
class Sun:
  def __init__(self):
    self.irradiance = 0 # intal irradiance in W/m^2 or J/s*m^2

  def energy(self, time):
    return self.irradiance*time
# ------------------------------- Containers -------------------------------    
class Container:
  def __init__(self, volume, fluid):
    self.volume = volume
    self.insulated = False
    self.fluid = fluid
    
  def conduction_loss(self):
    if self.insulated:
      return 0#.00001 # J/s
    else:
      return 0#.0001 # J/s

# ------------------------------- Solar Panel -------------------------------
class SolarPanel(Container):
  def __init__(self, fluid):
    self.volume = fluid.volume # default is 1 m^3
    self.insulated = False
    self.fluid = fluid
    self.efficiency = 0.7 # % of sunlight coverted to heat

 # ------------------------------- Water Tank -------------------------------   
class Tank(Container):
  def __init__(self, fluid):
    self.volume = fluid.volume # default is 3 m^3
    self.insulated = True
    self.fluid = fluid

# ------------------------------- Pipe -------------------------------   
class Pipe(Container):
  def __init__(self, fluid, length, diameter):
    self.volume = fluid.volume # default is 3 m^3
    self.length = length
    self.diameter = diameter
    self.insulated = True
    self.fluid = fluid



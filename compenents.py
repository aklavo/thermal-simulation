import math
# ------------------------------- Water -------------------------------
class Water:
  def __init__(self, temperature=20):
    self.density = 100 # density of water at 4°C(kg/m^3)
    self.specifc_heat = 4184 # specific heat of water at 20°C(J/kg*C)
    self.temperature = temperature # initial temperature of water 20°C

  def mass(self, volume):
    return self.density*volume
  
  def volume(self, mass):
    return mass/self.density
  
  def temperature_delta(self, energy, mass):
    return energy/self.specifc_heat/mass
  
  def energy(self, temperature_delta, mass):
    return temperature_delta*self.specifc_heat*mass
  
  def update_temperature(self, energy, mass):
    self.temperature += self.temperature_delta(energy, mass)

# ------------------------------- The Sun -------------------------------
class Sun:
  def __init__(self):
    self.max_irradiance = 1000 # irradiance in W/m^2 or J/s*m^2
    self.irradiance = 0 # intal irradiance in W/m^2 or J/s*m^2

  def energy(self, time):
    return self.irradiance*time
    
class Vessel:
  def __init__(self, volume, fluid):
    self.volume = volume
    self.insulated = False
    self.fluid = fluid
    
  def heat_loss(self):
    if self.insulated:
      return 0.00001 # J/s
    else:
      return 0.0001 # J/s

# ------------------------------- Solar Panel -------------------------------
class SolarPanel(Vessel):
  def __init__(self, volume, fluid):
    self.volume = volume
    self.insulated = False
    self.fluid = fluid

 # ------------------------------- Water Tank -------------------------------   
class Tank(Vessel):
  def __init__(self, volume, fluid):
    self.volume = volume
    self.insulated = True
    self.fluid = fluid



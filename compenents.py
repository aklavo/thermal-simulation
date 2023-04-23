
import math

class SolarPanel:
  def __init__(self, area, temp_in, temp_out, flow_in, flow_out, Q_in, Q_out):
    self.area = area
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out
    self.Q_in = Q_in
    self.Q_out = Q_out
    
  def volume(self, pipe_diameter):
    # the volume of water in the panel is approximated to be panel area multiplied by pipe diamter
    return self.area*pipe_diameter
   
  def mass_fulid(self, rho_fuild, pipe_diameter):
    return self.volume(pipe_diameter)*rho_fuild
    
class Pump:
  def __init__(self, temp_in, temp_out, flow_in, flow_out, Q_in, Q_out):
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out
    self.Q_in = Q_in
    self.Q_out = Q_out
    
class StorageTank:
  def __init__(self, volume, temp_in, temp_out, flow_in, flow_out, Q_in, Q_out):
    self.volume = volume
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out
    self.Q_in = Q_in
    self.Q_out = Q_out
    
  def mass_fulid(self, rho_fuild):
    return self.volume*rho_fuild
  
class Pipe:
  def __init__(self, length, diameter, temp_in, temp_out, flow_in, flow_out, Q_in, Q_out):
    self.length = length
    self.diameter = diameter
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out
    self.Q_in = Q_in
    self.Q_out = Q_out
    
  def volume(self):
    return math.pi*self.length*(self.diameter/2)**2
  
  def mass_fulid(self, rho_fuild):
    return self.volume()*rho_fuild


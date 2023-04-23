
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


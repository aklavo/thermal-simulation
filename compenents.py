class SolarPanel:
  def __init__(self, area, temp_in, temp_out, flow_in, flow_out):
    self.area = area
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out
    
class Pump:
  def __init__(self, temp_in, temp_out, flow_in, flow_out):
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out
    
class StorageTank:
  def __init__(self, volume, temp_in, temp_out, flow_in, flow_out):
    self.volume = volume
    self.temp_in = temp_in
    self.temp_out = temp_out
    self.flow_in = flow_in
    self.flow_out = flow_out


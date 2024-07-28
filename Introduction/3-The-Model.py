import streamlit as st 
import app

st.header("The Model")
st.subheader("Classes")
'''
To model the different components of the system, classes were created that contain the necessary
methods to calculate the heat transfer between the components. The classes are outlined below and 
viewable in detail via the *Show Classes* toggle. All model components are initialized with the geometry and
physical properties mentioned in the [Model Inputs](Model-Inputs) section.
#### Fluids
The `Fluid` class is used to represent a fluid that can be stored within a container. Through 
internal methods, fluids can `add_energy()` or `lose_energy()` via direct heat transfer or they can `mix_with()`
another fluid.
#### Containers
The `Container` class is used to represent a volume that can contain a fluid. Three additional
classes inherit from the `Container` class to handle the specific heat transfer associated with the geometry of
that component:  
 - `Solar Panel`
 - `Tank`
 - `Pipe`  

All contain `volume()` and `surface_area()` methods, which are used within the `overall_UA()` method
that handles the convection and conduction from the water, through the container, to the surroundings.
#### Materials
The `Material` class is used to represent a material that can be used to build a container. Materials
have a `thermal_conductivity`, `surface_temperature` and `thickness`.
#### Sun
The `Sun` class is used to represent the sun and its irradiance.
#### Pump
The `Pump` class is used to represent a pump which only has single attributes: `flow_rate`.
Future work would expand on this class to include more attributes such as: `power`, `pressure`, etc.
'''


show_code = st.toggle("Show Classes")

if show_code:
    classes = '''
              # ------------------------------- Fluids -------------------------------
              class Fluid:
                def __init__(self,name: str, density: float, specific_heat: float, temperature: float,
                              container=None, heat_transfer_coefficient=None):
                  self.name = name
                  self.density = density
                  self.specific_heat = specific_heat
                  self.temperature = temperature # initial temperature of water 20°C
                  self.container = container # container object if fluid is in a container
                  self.heat_transfer_coefficient = heat_transfer_coefficient

                def get_name(self) -> str:
                  return self.name

                def volume(self) -> float:
                  return self.container.volume() if self.container else 0
                
                def mass(self) -> float:
                  return self.density*self.volume()
                
                def temperature_in_kelvin(self) -> float:
                  return self.temperature + 273.15
                
                def add_container(self, container):
                  self.container = container
                
                # T2 = T1 + Q/mc
                def add_energy(self, energy: float):
                  self.temperature += energy/(self.specific_heat*self.mass())

                def lose_energy(self, energy: float):
                  self.temperature -= energy/(self.specific_heat*self.mass())

                # heat lost by fluid_1 + Heat gained by fluid_2 = 0
                def mix_with(self, fluid, flow_rate: float, time: float):
                  if flow_rate < 0:
                      raise ValueError("Flow rate must be non-negative.")
                  mass_1 = self.mass()
                  mass_2 = fluid.density*flow_rate*time
                  mass_3 = mass_1 + mass_2
                  temp_1 = self.temperature
                  temp_2 = fluid.temperature

                  # update both fluid temperature to final temperature
                  if flow_rate > 0:
                    self.temperature = ((mass_1*temp_1)+(mass_2*temp_2))/(mass_3) #update only temp in direction of flow
                    #fluid.temperature = self.temperature
                    return 

              # ------------------------------- Surfaces -------------------------------
              class Material:
                def __init__(self, thermal_conductivity: float, surface_temperature: float, thickness: float):
                  self.thermal_conductivity = thermal_conductivity
                  self.surface_temperature = surface_temperature 
                  self.thickness = thickness

              # ------------------------------- The Sun -------------------------------
              class Sun:
                def __init__(self):
                  self.irradiance = 0 # initial irradiance in W/m^2 or J/s*m^2

                def energy(self, time: float, area: float) -> float:
                  return self.irradiance*time*area
                
              # ------------------------------- Containers -------------------------------    
              class Container(ABC):
                def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid):
                  self.fluid = fluid
                  self.material = material
                  self.surroundings = surroundings # another fluid object (air)

                @abstractmethod
                def volume(self) -> float:
                  pass

                @abstractmethod
                def overall_UA(self) -> float:
                  pass

                def temp_loss(self,temp_loss) -> float:
                  self.fluid.temperature -= temp_loss # used to simulate simple heat loss

                def heat_loss(self, time) -> float:

                  heat_loss = ((self.fluid.temperature - self.surroundings.temperature) *
                              self.overall_UA(self.surroundings) *
                              time)

                  return heat_loss
                
                def radiation_loss(epsilon, sigma, A, T_surface, T_environment) -> float:
                    return epsilon * sigma * A * (T_surface**4 - T_environment**4) #not currently in use

              # ------------------------------- Solar Panel -------------------------------
              class SolarPanel(Container):
                def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid,
                              length: float, width: float, height: float):
                  super().__init__(fluid, material, surroundings)
                  self.length = length
                  self.width = width
                  self.height = height
                  self.efficiency = 0.8 # % of light energy converted to heat energy in water <-- this is a heat transfer band-Aid for now

                def volume(self) -> float:
                  return self.length * self.width * self.height
                
                def surface_area(self) -> float:
                  top = (self.length * self.width) # assume bottom is lossless
                  left_right = 2*(self.length * self.height)
                  front_back = 2*(self.width * self.height)
                  return top + left_right + front_back
                
                def solar_area(self) -> float:
                  return self.length * self.width
                
                def overall_UA(self, air: Fluid) -> float:
                  r_inside = 1/self.fluid.heat_transfer_coefficient
                  r_material = self.material.thickness/self.material.thermal_conductivity
                  r_air = 1/air.heat_transfer_coefficient

                  overall_UA = (1/(r_inside + r_material  + r_air)) * self.surface_area()

                  return overall_UA
                  
              # ------------------------------- Water Tank -------------------------------   
              class Tank(Container):
                def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid,
                              radius: float, height: float,  insulation: Material):
                  super().__init__(fluid, material, surroundings)
                  self.radius = radius
                  self.height = height
                  self.insulation = insulation

                def volume(self) -> float:
                  return math.pi*self.height*self.radius**2
                
                def surface_area_walls(self, diameter) -> float:
                  return (math.pi*diameter*self.height)
                
                def surface_area_top(self) -> float:
                  return (math.pi*self.radius**2)
                
                #inner diameter of tank
                def diameter_1(self) -> float:
                  return self.radius * 2
                
                #outer diameter of tank
                def diameter_2(self) -> float:
                  return (self.radius + self.material.thickness) * 2
                
                #outer diameter of tank + insulation
                def diameter_3(self) -> float:
                  return (self.radius + self.material.thickness + self.insulation.thickness) * 2
                
                # just tank walls
                def overall_UA(self, air: Fluid) -> float:
                  # wall thermal resistances
                  # diameter ratios are necessary to correctly account for the cylindrical geometry and the logarithmic nature of radial heat conduction
                  wall_r_inside = 1/(self.surface_area_walls(self.diameter_1())*self.fluid.heat_transfer_coefficient)
                  wall_r_pipe = (math.log(self.diameter_2()/self.diameter_1()))/(self.material.thermal_conductivity*2*math.pi*self.height) 
                  wall_r_insulation = (math.log(self.diameter_3()/self.diameter_2()))/(self.insulation.thermal_conductivity*2*math.pi*self.height)
                  wall_r_air = 1/(air.heat_transfer_coefficient*self.surface_area_walls(self.diameter_3()))

                  # tank top thermal resistances
                  top_r_inside = 1/self.fluid.heat_transfer_coefficient
                  top_r_pipe = self.material.thickness/self.material.thermal_conductivity
                  top_r_insulation = self.insulation.thickness/self.insulation.thermal_conductivity
                  top_r_air = 1/air.heat_transfer_coefficient

                  wall_UA = 1/(wall_r_inside + wall_r_pipe + wall_r_insulation + wall_r_air)
                  top_UA = (1/(top_r_inside + top_r_pipe + top_r_insulation + top_r_air)) * self.surface_area_top()
                  overall_UA = wall_UA + top_UA

                  return overall_UA
                  
              # ------------------------------- Pipe --------------------------------------   
              class Pipe(Container):
                def __init__(self, fluid: Fluid, material: Material, surroundings: Fluid,
                              radius: float, length: float, insulation: Material):
                  super().__init__(fluid, material, surroundings)
                  self.radius = radius
                  self.length = length
                  self.insulation = insulation

                def volume(self) -> float:
                  return math.pi*self.length*self.radius**2
                
                def surface_area(self, diameter) -> float:
                  return (math.pi*diameter*self.length) # outer surface area
                
                #inner diameter of pipe
                def diameter_1(self) -> float:
                  return self.radius * 2
                
                #outer diameter of pipe
                def diameter_2(self) -> float:
                  return (self.radius + self.material.thickness) * 2
                
                #outer diameter of pipe + insulation
                def diameter_3(self) -> float:
                  return (self.radius + self.material.thickness + self.insulation.thickness) * 2


                def overall_UA(self, air: Fluid) -> float:
                  # diameter ratios are necessary to correctly account for the cylindrical geometry and the logarithmic nature of radial heat conduction
                  r_inside = 1/(self.surface_area(self.diameter_1())*self.fluid.heat_transfer_coefficient)
                  r_pipe = (math.log(self.diameter_2()/self.diameter_1()))/(self.material.thermal_conductivity*2*math.pi*self.length) 
                  r_insulation = (math.log(self.diameter_3()/self.diameter_2()))/(self.insulation.thermal_conductivity*2*math.pi*self.length)
                  r_air = 1/(air.heat_transfer_coefficient*self.surface_area(self.diameter_3()))

                  overall_UA = (1/(r_inside + r_pipe + r_insulation + r_air))

                  return overall_UA
                
              # ------------------------------- Pump --------------------------------------
              class Pump:
                def __init__(self, flow_rate: float):
                  self.flow_rate = flow_rate
              '''
    st.code(classes, language='python')


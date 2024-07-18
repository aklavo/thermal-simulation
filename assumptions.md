# Assumptions

### Basic Assumptions
- The storage tank is a perfect cylinder.
- The panel is a rectangle of water. 
- The flow of a pump is modelled based on the transfer of energy through fluid mixing.

### Thermodynamic Assumptions
- The tank is in thermal equalibrium with the indoor zone temperature at sim start.
- The panel is in thermal equalibrium with the outdoor zone temperature at sim start.
- The supply pipe intial temperature is the panel temperature.
- The return pipe intial temperature is the tank temperature.
- All energy from the sun is transferred into the panel.
- Mixing is assumed to be instantaneous, thus T_final is always reached after each timestep.
- The indoor temperature is constant dispate the tank heat loss (there's a really good cooling system in there lol)
- Air has a constant convective heat transfer coefficient of 10 W/m^2K.

### Operational Assumptions
- The pump is sized such that it can overcome the system head and produce the constant flow defined.
- The speed of the pump is constant and instantaneous.
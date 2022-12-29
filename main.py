import pandas as pd
from tespy.components.basics.cycle_closer import CycleCloser
from tespy.networks import Network
from tespy.components import (
    CycleCloser, Pipe, Pump, HeatExchangerSimple, SolarCollector
)
from tespy.connections import Connection
import matplotlib.pyplot as plt
import numpy as np

## INTIALIZE NETWORK
fluid_list = ['water']
nw = Network(fluids=fluid_list)
nw.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')
cc = CycleCloser(label='cycle closer')

# solar water heater panel
sc = SolarCollector(label='solar scector')

# pump
pu = Pump(label='feed pump')

# storage tank
tank = HeatExchangerSimple(label='tank')

# pipes
pipe_feed_pump = Pipe(label='feed pipe pump')
pipe_feed_tank = Pipe(label='feed pipe tank')
pipe_return = Pipe(label='return pipe')

# connections
c0 = Connection(cc, "out1", sc, "in1", label="0") # cycle closer -> solar panel
c1 = Connection(sc, "out1", pipe_feed_pump, "in1", label="1") # solar panel -> feed pipe pump
c2 = Connection(pipe_feed_pump, "out1", pu, "in1", label="2") # feed pipe pump -> pump
c3 = Connection(pu, "out1", pipe_feed_tank, "in1", label="3") # pump -> feed pipe tank
c4 = Connection(pipe_feed_tank, "out1", tank, "in1", label="4") # feed pipe tank -> tank
c5 = Connection(tank, "out1", pipe_return, "in1", label="5") # tank -> return pipe
c6 = Connection(pipe_return, "out1", cc, "in1", label="6") # return pipe -> cycle closer
nw.add_conns(c0, c1, c2, c3, c4, c5, c6) 

## SET ATTRIBUTES
sc.set_attr(E=8e2, A=3, pr=1, Q='var') # average solar irradiance surface during summer is ~800 W/m2 
tank.set_attr(Q=-1000,pr=0.98) # assume constant heat demand of the consumer
pu.set_attr(eta_s=0.80) # pump efficiency assumed 80%
# assumed constant pressure and thermal losses in all pipes
pipe_feed_pump.set_attr(Q=-100,pr=0.98)
pipe_feed_tank.set_attr(Q=-100,pr=0.98)
pipe_return.set_attr(Q=-100,pr=0.98)
c0.set_attr(p=5, T=35,fluid={'water': 1})
c1.set_attr(p0=2, T=120)
print('#'*50)
print('MAIN SIMULATION')
print('#'*50)
nw.solve(mode="design")
nw.print_results()
print('MAIN SIMULATION END')
print('#'*50)
gridnum = 10
T_amb = np.linspace(-10, 30, gridnum, dtype=float)
E_glob = np.linspace(100, 1000, gridnum, dtype=float)

df = pd.DataFrame(columns=T_amb)

for E in E_glob:
    eta = []
    sc.set_attr(E=E)
    for T in T_amb:
        sc.set_attr(Tamb=T)
        nw.solve(mode='design')
        eta += [sc.Q.val / (sc.E.val * sc.A.val)]
        # cut out efficiencies smaller than zero
        if eta[-1] < 0:
            eta[-1] = np.nan

    df.loc[E] = eta

E, T = np.meshgrid(T_amb, E_glob)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(E, T, df.values)
# temperature difference -> mean scector temperature to ambient temperature
ax.set_xlabel('ambient temperature t_a in °C')
# absorption on the inclined surface
ax.set_ylabel('absorption E in $\mathrm{\\frac{W}{m^2}}$')
# thermal efficiency (no optical losses)
ax.set_zlabel('efficiency $\eta$')
plt.show()

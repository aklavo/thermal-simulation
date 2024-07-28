import streamlit as st
import main
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.header("Data Analysis")
'''
The follow analysis is performed on the full year of 2022, using the default simulation parameters. 
- GHI
- Heat Losses
- Controlled Flow
- Flow rate max = 0.00063 m³/s

The purpose of this section is to analyze only the results and deduce insight on tank temperature.
'''

with st.spinner("Running simulation..."):
        main.run_sim()

results_df = pd.read_parquet("Outputs/thermal-simulation.parquet")

st.dataframe(results_df)

st.subheader("Parameter Correlation")
'''
To start a Pearson's Correlation analysis was performed to understand how all the parameters relate to each other. 
The Pearson Correlation Coefficient (PCC) measures the linear correlation between two variables. It is the ratio between the covariance of two variables and 
the product of their standard deviations. A value of 1 means there is a perfect linear relationship between the variables, a value of -1 means there is a perfect
inverse linear relationship, and a value of 0 means there is no linear relationship.
'''
st.latex(r'PCC = \frac{Cov(X,Y)}{\sigma_X \sigma_Y}')
corr = results_df.corr()

corr_plot = px.imshow(corr, labels={'color':'Correlation Coefficient'}, text_auto='.2f', aspect="auto")
st.plotly_chart(corr_plot, use_container_width=True)
'''
Tank temperature is perfectly positively correlated with itself and tank heat losses. This is because tank heat losses are directly
proportional to the tank temperature, scaled by the ratio energy loss over fluid mass multiplied by the fluid specific heat capacity.

The next highest correlation is with the supply and return pipe temperature. This makes sense since these are the two fluids mixing with the tank fluid.

Outside air is also positively correlated with tank temperature. This is because the outside air temperature is heavily correlated with the temperatures of the
the other three components (panels, supply and return pipes) and those temperatures lead into the tank temperature. The high correlation indicates that those components
have lose heat to their surrounding easily.
'''
st.subheader("Tank Temperature Regression")

regression_fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05)

regression_fig.add_trace(
                 go.Scatter(x=results_df["Outside Air Temperatures"], y=results_df["Tank Temperatures"], 
                             mode='markers', name='Tank Temperature', marker=dict(color='orange')),
                 row=1, col=1
)

regression_fig.add_trace(
                 go.Scatter(x=results_df["Outside Air Temperatures"], y=results_df["Tank Heat Losses"], 
                             mode='markers', name='Tank Heat Losses'),
                 row=2, col=1
)

regression_fig.add_trace(
                 go.Scatter(x=results_df["Outside Air Temperatures"], y=results_df["Supply Pipe Temperatures"], 
                             mode='markers', name='Supply Pipe Temperatures', marker=dict(color='green')),
                 row=3, col=1
)

for i, y_col in enumerate(['Tank Temperatures', 'Tank Heat Losses', 'Supply Pipe Temperatures'], 1):
           x = results_df["Outside Air Temperatures"]
           y = results_df[y_col]
           slope, intercept = np.polyfit(x, y, 1)
           line = slope * x + intercept
           equation = f'y = {slope:.2f}x + {intercept:.2f}'
    
           regression_fig.add_trace(
               go.Scatter(x=x, y=line, mode='lines', 
                           name=f'OLS Trendline ({equation})', 
                           line=dict(color='red', dash='dash')),
               row=i, col=1
           )

regression_fig.update_layout(height=900)
regression_fig.update_xaxes(title_text="Outside Air Temperatures", row=3, col=1)
regression_fig.update_yaxes(title_text="Tank Temperatures", row=1, col=1)
regression_fig.update_yaxes(title_text="Tank Heat Loss", row=2, col=1)
regression_fig.update_yaxes(title_text="Supply Temperature", row=3, col=1)

st.plotly_chart(regression_fig, use_container_width=True)
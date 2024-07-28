import streamlit as st
import main
import pandas as pd
import plotly.express as px

st.header("Data Analysis")
'''
The follow analysis is performed on the full year of 2022, using the default simulation parameters. 
- GHI
- Heat Losses
- Controlled Flow
- Flow rate max = 0.00063 m³/s

The purpose of this section is to analyze only the results and deduce model insight from the data.
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
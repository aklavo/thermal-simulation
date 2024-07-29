import streamlit as st
import main
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from scipy import stats

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
    start = '2022-01-01 00:00:00'
    end = '2022-12-31 23:55:00'
    if not os.path.exists("Outputs/thermal-simulation.parquet") or \
      pd.read_parquet("Outputs/thermal-simulation.parquet")["Time"].min().strftime("%Y-%m-%d %H:%M:%S") != start or \
      pd.read_parquet("Outputs/thermal-simulation.parquet")["Time"].max().strftime("%Y-%m-%d %H:%M:%S") != end:
       main.run_sim(start=start, end=end)

results_df = pd.read_parquet("Outputs/thermal-simulation.parquet")
# Convert to hourly to speed things up
results_df['Time'] = pd.to_datetime(results_df['Time'])
results_df.set_index('Time', inplace=True)
results_df = results_df.resample('H').mean()
results_df.reset_index(inplace=True)
with st.container():
    st.subheader("Basic Analysis")

    simple_stats = results_df.describe()
    tank_start_temp = results_df["Tank Temperatures"].iloc[0]
    max_tank_start_temp = simple_stats["Tank Temperatures"]["max"]

    time_of_max_tank_start_temp = results_df.loc[results_df["Tank Temperatures"].idxmax(), "Time"]
    formatted_time = time_of_max_tank_start_temp.strftime("%B %d at %I:%M %p")
    st.write(f'''The Tank temperature starts at {tank_start_temp:.2f}°C and reaches its maximum 
                at {max_tank_start_temp:.2f}°C on {formatted_time}.''')
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
            st.dataframe(simple_stats["Tank Temperatures"])
    with col2:
            box_plot_fig = px.box(results_df, y="Tank Temperatures")

            st.plotly_chart(box_plot_fig, use_container_width=True)
    with col3:
            # Calculate mean and standard deviation
            mean_temp = results_df["Tank Temperatures"].mean()
            std_temp = results_df["Tank Temperatures"].std()

            # Create standard deviation plot
            std_dev_fig = go.Figure()
            std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=results_df["Tank Temperatures"],
                                            mode='lines', name='Tank Temperature'))
            std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=[mean_temp] * len(results_df),
                                            mode='lines', name='Mean', line=dict(color='red', dash='dash')))
            std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=[mean_temp + std_temp] * len(results_df),
                                            mode='lines', name='+1 Std Dev', line=dict(color='green', dash='dot')))
            std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=[mean_temp - std_temp] * len(results_df),
                                            mode='lines', name='-1 Std Dev', line=dict(color='green', dash='dot')))

            std_dev_fig.update_layout(xaxis_title='Time', yaxis_title='Temperature (°C)')

            st.plotly_chart(std_dev_fig, use_container_width=True)
        



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
with st.container():

    st.subheader("Tank Temperature Regression")
    summer = results_df.loc[results_df["Time"].dt.month.isin([6,7,8])]
    winter = results_df.loc[results_df["Time"].dt.month.isin([12,1,2])]
    fall = results_df.loc[results_df["Time"].dt.month.isin([9,10,11])]
    spring = results_df.loc[results_df["Time"].dt.month.isin([3,4,5])]

    seasons = {"Summer": summer, "Fall": fall, "Winter": winter, "Spring": spring}
   
    col1, col2 = st.columns([1,2])
    with col1:
        selected_season = st.select_slider("Select Season", options=list(seasons.keys()))
        reg_df = seasons[selected_season]
    with col2:
        '''
        Throughout all seasons tank temperature has strong correlations with tank heat losses, supply pipe temperatures, and outside air temperatures. 
        This correlation is lost in winter, when the outside air temperatures are the lowest and heat loss dominates the system, leaving the tank temperature to 
        hover around the indoor zone temperature.
        '''
    with st.spinner("Calculating Regression..."):

        regression_fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05)


        regression_fig.add_trace(

                        go.Scatter(x=reg_df["Tank Temperatures"], y=reg_df["Tank Heat Losses"], 
                                    mode='markers', name='Tank Heat Losses'),
                        row=1, col=1
        )

        regression_fig.add_trace(

                        go.Scatter(x=reg_df["Tank Temperatures"], y=reg_df["Supply Pipe Temperatures"], 
                                    mode='markers', name='Supply Pipe Temperatures', marker=dict(color='green')),
                        row=2, col=1
        )

        regression_fig.add_trace(
                        go.Scatter(x=reg_df["Tank Temperatures"], y=reg_df["Outside Air Temperatures"], 
                                    mode='markers', name='Outside Air Temperature', marker=dict(color='orange')),
                        row=3, col=1
        )

        for i, y_col in enumerate(['Tank Heat Losses', 'Supply Pipe Temperatures', 'Outside Air Temperatures'], 1):
                x = reg_df["Tank Temperatures"]
                y = reg_df[y_col]
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                line = slope * x + intercept
                r_squared = r_value**2
                equation = f'y = {slope:.2f}x + {intercept:.2f}, R² = {r_squared:.2f}'

                regression_fig.add_trace(
                    go.Scatter(x=x, y=line, mode='lines', 
                                name=f'OLS Trendline ({equation})', 
                                line=dict(color='red', dash='dash')),
                    row=i, col=1
                )

        regression_fig.update_layout(height=900)
        regression_fig.update_xaxes(title_text="Tank Temperatures", row=3, col=1)
        regression_fig.update_yaxes(title_text="Outside Air Temperatures", row=3, col=1)
        regression_fig.update_yaxes(title_text="Tank Heat Loss", row=1, col=1)
        regression_fig.update_yaxes(title_text="Supply Temperature", row=2, col=1)

        st.plotly_chart(regression_fig, use_container_width=True)
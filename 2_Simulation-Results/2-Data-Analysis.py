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
- `clouds = 1` (GHI)  
- `heat loss = True`  
- `pump_control = 2` (Controlled Flow)
- `flow_rate_max = 0.00063` (m³/s)

The purpose of this section is to analyze only the results and deduce insight on tank temperature.
'''

results_df = pd.read_parquet("Outputs/thermal-simulation-full-year.parquet")
# Convert to hourly to speed things up
results_df['Time'] = pd.to_datetime(results_df['Time'])
results_df.set_index('Time', inplace=True)
results_df = results_df.resample('H').mean()
results_df.reset_index(inplace=True)
st.subheader("Basic Analysis")

simple_stats = results_df.describe()
tank_start_temp = results_df["Tank Temperatures"].iloc[0]
max_tank_start_temp = simple_stats["Tank Temperatures"]["max"]

time_of_max_tank_start_temp = results_df.loc[results_df["Tank Temperatures"].idxmax(), "Time"]
formatted_time = time_of_max_tank_start_temp.strftime("%B %d at %I:%M %p")
st.write(f'''The Tank temperature starts at {tank_start_temp:.2f}°C and reaches its maximum 
            at {max_tank_start_temp:.2f}°C on {formatted_time}.''')
with st.container():
    # Top row with dataframe and metrics
    col1, col2 = st.columns([1, 3], )
    
    with col1:
        st.dataframe(simple_stats["Tank Temperatures"].transpose())
    
    with col2:
        # Add seasonal max tank temperatures
        results_df['Season'] = pd.to_datetime(results_df['Time']).dt.month.map({12:'Winter', 1:'Winter', 2:'Winter',
                                                                                3:'Spring', 4:'Spring', 5:'Spring',
                                                                                6:'Summer', 7:'Summer', 8:'Summer',
                                                                                9:'Fall', 10:'Fall', 11:'Fall'})
        
        seasonal_max = results_df.groupby('Season')['Tank Temperatures'].max()
        
        metric_col1, metric_col2 = st.columns(2)
        metric_col3, metric_col4 = st.columns(2)
        
        metric_col1.metric("Summer Max Temperature", f"{seasonal_max['Summer']:.2f}°C")
        metric_col2.metric("Winter Max Temperature", f"{seasonal_max['Winter']:.2f}°C")
        metric_col3.metric("Fall Max Temperature", f"{seasonal_max['Fall']:.2f}°C")
        metric_col4.metric("Spring Max Temperature", f"{seasonal_max['Spring']:.2f}°C")

    # Bottom row with plots
    plot_col1, plot_col2 = st.columns([1, 3])
    
    with plot_col1:
        with st.spinner("Plotting Data..."):
            @st.cache_data
            def display_box_plot(results_df):
                box_plot_fig = px.box(results_df, y="Tank Temperatures")
                box_plot_fig.update_layout(hovermode=False)
                
                return box_plot_fig
            
            st.plotly_chart(display_box_plot(results_df), use_container_width=True)
    
    with plot_col2:
        with st.spinner("Plotting Data..."):
            @st.cache_data
            def plot_mean_std(results_df):
                mean_temp = results_df["Tank Temperatures"].mean()
                std_temp = results_df["Tank Temperatures"].std()

                std_dev_fig = go.Figure()
                std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=results_df["Tank Temperatures"],
                                                mode='lines', name='Tank Temperature'))
                std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=[mean_temp] * len(results_df),
                                                mode='lines', name='Mean', line=dict(color='red', dash='dash')))
                std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=[mean_temp + std_temp] * len(results_df),
                                                mode='lines', name='+1 Std Dev', line=dict(color='green', dash='dot')))
                std_dev_fig.add_trace(go.Scatter(x=results_df["Time"], y=[mean_temp - std_temp] * len(results_df),
                                                mode='lines', name='-1 Std Dev', line=dict(color='green', dash='dot')))

                std_dev_fig.update_layout(xaxis_title='Time', yaxis_title='Temperature (°C)', hovermode="x unified")

                return std_dev_fig 
            
            st.plotly_chart(plot_mean_std(results_df), use_container_width=True)
'''
It's clear that the tank temperature cannot maintain an above ambient temperature during the winter months. This is due to the
high heat loss through the panel and pipes which are exposed to the cold outdoor air.
'''

st.subheader("Parameter Correlation")
'''
To see how other parameters interact with tank temperature a Pearson's Correlation analysis was performed. 
'''
st.latex(r'PCC = \frac{Cov(X,Y)}{\sigma_X \sigma_Y}')
results_df.drop(columns=["Season"], inplace=True)
corr = results_df.corr()

corr_plot = px.imshow(corr, labels={'color':'Correlation Coefficient'}, text_auto='.2f', aspect="auto")
st.plotly_chart(corr_plot, use_container_width=True)
'''
Tank temperature is perfectly positively correlated with itself and tank heat losses. This is because tank heat losses are directly
proportional to the tank temperature. Specifically the temperature is scaled by the ratio energy lost to the fluid mass multiplied by the fluid specific heat capacity.

The next highest correlation is with the supply and return pipe temperatures. This is because these are the two fluids mixing with the tank fluid.

Outside air is also positively correlated with tank temperature. This is because the outside air temperature is heavily correlated with the temperatures of the
other three components (panels, supply and return pipes) and those temperatures lead into the tank temperature. The high correlation indicates that those components
lose heat to their surrounding easily.
'''
with st.container():
    st.subheader("Tank Temperature Regression")
    @st.cache_data
    def get_seasons(results_df):
        summer = results_df.loc[results_df["Time"].dt.month.isin([6,7,8])]
        winter = results_df.loc[results_df["Time"].dt.month.isin([12,1,2])]
        fall = results_df.loc[results_df["Time"].dt.month.isin([9,10,11])]
        spring = results_df.loc[results_df["Time"].dt.month.isin([3,4,5])]
        return {"Summer": summer, "Fall": fall, "Winter": winter, "Spring": spring}
    seasons = get_seasons(results_df)


    selected_y_axis = st.radio("Select Y-axis", options=["Tank Heat Losses", "Supply Pipe Temperatures", "Outside Air Temperatures"], horizontal=True)
 
    selected_seasons = st.multiselect("Select Seasons", options=list(seasons.keys()), default=list(seasons.keys()))

with st.spinner("Calculating Regressions..."):
    @st.cache_data

    def regression_plots(seasons, selected_y_axis, selected_seasons):
        regression_fig = go.Figure()

        colors = {'Summer': 'red', 'Fall': 'orange', 'Winter': 'blue', 'Spring': 'green'}

        for season, df in seasons.items():
            if season not in selected_seasons:
                continue
            
            x = df["Tank Temperatures"]
            y = df[selected_y_axis]
            
            regression_fig.add_trace(
                go.Scatter(x=x, y=y, mode='markers', name=season,
                           marker=dict(color=colors[season]))
            )

            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            line = slope * x + intercept
            r_squared = r_value**2
            equation = f'y = {slope:.2f}x + {intercept:.2f}, R² = {r_squared:.2f}'

            regression_fig.add_trace(
                go.Scatter(x=x, y=line, mode='lines', 
                           name=f'{season} OLS Trendline ({equation})', 
                           line=dict(color=colors[season], dash='dash'))
            )

        regression_fig.update_layout(height=600, hovermode="x unified")
        regression_fig.update_xaxes(title_text="Tank Temperatures")
        regression_fig.update_yaxes(title_text=selected_y_axis)
        
        return regression_fig


    st.plotly_chart(regression_plots(seasons, selected_y_axis, selected_seasons), use_container_width=True)
'''
Throughout all seasons expect winter, tank temperature has a strong correlations with tank heat losses, supply pipe temperatures, and outside air temperatures. 
This is because when outside air temperatures are the lowest heat loss dominates the system.This leaves the tank temperature to hover around the indoor zone temperature.
Since the indoor temperature randomly fluctuates, the tank temperature and tank heat fluctuate about the point 21.11 °C and 0.0 Joules.
'''
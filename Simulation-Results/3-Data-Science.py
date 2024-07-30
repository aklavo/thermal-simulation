import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor

with st.container():
    st.header("Date Science")
    
    "Can we predict the temperature of the tank based on model inputs alone?"
    
    st.subheader("Data Cleaning")
    '''
    We'll start by parsing the datetime column and removing all simulation results accept for the tank temperature which will be our dependent variable.
    Our model inputs (or independent variables) are:
    - Month
    - Day
    - Hour
    - Minute
    - Solar Energy
    - Outside Air Temperatures
    - Zone Air Temperatures
    '''
    results_df = pd.read_parquet("Outputs/thermal-simulation-full-year.parquet")
    results_df = results_df[
        [
            "Time",
            "Tank Temperatures",
            "Outside Air Temperatures",
            "Zone Air Temperatures",
            "Solar Energy",
        ]
    ]
    # parse the datetime column and add month, day, hour, and minute columns
    results_df["Time"] = pd.to_datetime(results_df["Time"])
    results_df["Month"] = results_df["Time"].dt.month
    results_df["Day"] = results_df["Time"].dt.day
    results_df["Hour"] = results_df["Time"].dt.hour
    results_df["Minute"] = results_df["Time"].dt.minute
    results_df.drop(columns=["Time"], inplace=True)
    st.dataframe(results_df, hide_index=True)
with st.container():
    def display_model_results(predictions, y_test):
        with st.spinner("Displaying Results..."):
            results = st.container()
            col1, col2 = results.columns([1,3])    
            residuals = y_test - predictions

            # model performance metrics r2, mse, mae
            mse = mean_squared_error(y_test, predictions)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            
            # display metrics as st.metrics
            col1.metric("MSE:", f"{mse:.2f}")
            col1.metric("RMSE:", f"{rmse:.2f}")
            col1.metric("MAE:", f"{mae:.2f}")
            col1.metric("R2:", f"{r2:.2f}")

            # Create a faceted plot using plotly
            fig = make_subplots(rows=1, cols=2, subplot_titles=['Residuals vs Fitted Values', 'Q-Q Plot'])

            # Residuals vs Fitted Values Plot
            fig.add_trace(go.Scatter(x=predictions, y=residuals, mode='markers', name='Residuals'), row=1, col=1)
            fig.add_trace(go.Scatter(x=predictions, y=np.zeros_like(predictions), mode='lines', line=dict(color='red', dash='dash'), name='Zero Line'), row=1, col=1)

            # Q-Q Plot
            qq = sm.qqplot(residuals, fit=True, line='45')
            fig.add_trace(go.Scatter(x=qq.gca().lines[0].get_xdata(), y=qq.gca().lines[0].get_ydata(), mode='markers', name='Q-Q'), row=1, col=2)
            fig.add_trace(go.Scatter(x=qq.gca().lines[1].get_xdata(), y=qq.gca().lines[1].get_ydata(), mode='lines', line=dict(color='red'), name='45 Degree Line'), row=1, col=2)

            fig.update_xaxes(title_text="Fitted Values", row=1, col=1)
            fig.update_xaxes(title_text="Theoretical Quantiles", row=1, col=2)
            fig.update_yaxes(title_text="Residuals", row=1, col=1)
            fig.update_yaxes(title_text="Sample Quantiles", row=1, col=2)
            fig.update_layout(hovermode="x unified")

            col2.plotly_chart(fig, use_container_width=True)

            # plot actual vs predicted
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=y_test, y=predictions, mode='markers', name='Actual vs Predicted', marker=dict(color='purple')))  
            fig.update_xaxes(title_text="Actual Values")
            fig.update_yaxes(title_text="Predicted Values")
            fig.update_layout(hovermode="x unified")
            results.plotly_chart(fig, use_container_width=True)

    st.subheader("Linear Regression")
    lin_reg_code = '''
    X = results_df.drop(columns=["Tank Temperatures"])
    y = results_df["Tank Temperatures"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
    model = LinearRegression().fit(X_train, y_train)

    predictions = model.predict(X_test)
    
    '''
    st.code(lin_reg_code, language="python")
    # We'll use a linear regression model to predict the tank temperature based on the model inputs
    X = results_df.drop(columns=["Tank Temperatures"])
    y = results_df["Tank Temperatures"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if st.button("Run Linear Regression Model"):
        with st.spinner("Training/Testing Model..."):
            model = LinearRegression().fit(X_train, y_train)
            predictions = model.predict(X_test)
            display_model_results(predictions, y_test)

    st.subheader("Random Forest")
    forest_code = '''
    model_rf = RandomForestRegressor().fit(X_train, y_train)
    predictions_rf = model_rf.predict(X_test) 
    '''
    st.code(forest_code, language="python")

    if st.button("Run Random Forest Model"):
        with st.spinner("Training/Testing Model..."):
            model_rf = RandomForestRegressor().fit(X_train, y_train)
            predictions_rf = model_rf.predict(X_test)   
            display_model_results(predictions_rf, y_test)
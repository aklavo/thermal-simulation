import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
import pickle

with st.container():
    st.header("Black Box Modeling")
    '''The simulation currently runs pretty quick due to the simple implementation of heat transfer and basic geometry.
    As complexity increases in both those disciplines the need for a data driven model may emerge. This section showcases
    a couple basic machine learning model in an an attempt to answer: '''
    st.write("***Can we predict accurately predict the temperature of the tank based on model inputs alone?***")
    
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
    @st.cache_data
    def display_model_results(predictions, y_test):
        with st.spinner("Displaying Results..."):
            results = st.container()
            col1, col2 = results.columns([1,5])    
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

            # Create a figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 2))
        
            # Residuals vs Fitted Values Plot
            ax1.scatter(predictions, residuals, s=3)
            ax1.axhline(y=0, color='r', linestyle='--', linewidth=0.8)
            ax1.set_xlabel('Fitted Values', fontsize=6)
            ax1.set_ylabel('Residuals', fontsize=6)
            ax1.set_title('Residuals vs Fitted Values', fontsize=6)
            ax1.tick_params(axis='both', which='major', labelsize=6)

            # Q-Q Plot
            sm.qqplot(residuals, fit=True, line='45', ax=ax2)
            ax2.set_title('Q-Q Plot', fontsize=6)
            ax2.set_xlabel('Theoretical Quantiles', fontsize=6)
            ax2.set_ylabel('Sample Quantiles', fontsize=6)
            ax2.tick_params(axis='both', which='major', labelsize=6)

            plt.tight_layout()
            col2.pyplot(fig)

            # plot actual vs predicted
            fig, ax = plt.subplots(figsize=(5, 1.5))
            ax.scatter(y_test, predictions, color='purple', alpha=0.6, s=3)
            ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=0.8)
            ax.set_xlabel('Actual Values', fontsize=5)
            ax.set_ylabel('Predicted Values', fontsize=5)
            ax.tick_params(axis='both', which='major', labelsize=5)
            plt.tight_layout()

            results.pyplot(fig)
    st.subheader("Linear Regression")
    '''
    We'll start by using a linear regression model to predict the tank temperature based on the model inputs.
    '''
    lin_reg_code = '''
    X = results_df.drop(columns=["Tank Temperatures"])
    y = results_df["Tank Temperatures"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
    model = LinearRegression().fit(X_train, y_train)

    predictions = model.predict(X_test)
    
    '''
    st.code(lin_reg_code, language="python")
    # We'll use a linear regression model to predict the tank temperature based on the model inputs
    # Ran once to get pickle file
    # X = results_df.drop(columns=["Tank Temperatures"])
    # y = results_df["Tank Temperatures"]
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    

    y_test = pickle.load(open("Outputs/y_test.pkl", "rb"))
    with st.spinner("Plotting Results..."):
        # ran once to get pickle file
        # model = LinearRegression().fit(X_train, y_train)
        # predictions = model.predict(X_test)
        # pickle.dump(y_test, open("Outputs/y_test.pkl", "wb"))
        # pickle.dump(predictions, open("Outputs/predictions.pkl", "wb"))

        predictions = pickle.load(open("Outputs/predictions.pkl", "rb"))
        display_model_results(predictions, y_test)
    '''
    The performance of the linear regression model leaves room for improvement. The R2 of 70% indicates that the model struggles 
    to explain the variance of 30% of the tank temperatures. It's clear from the plots that this is primarily happening at lower temperatures, 
    when tank temperature is no longer strongly correlated with the any model inputs. This aligns with what we know to be true from
    earlier regression analysis. 

    '''
    st.subheader("Random Forest")
    forest_code = '''
    model_rf = RandomForestRegressor().fit(X_train, y_train)
    predictions_rf = model_rf.predict(X_test) 
    '''
    st.code(forest_code, language="python")

    with st.spinner("Plotting Results..."):
        # ran once to get pickle file
        # model_rf = RandomForestRegressor().fit(X_train, y_train)
        # predictions_rf = model_rf.predict(X_test)   

        # pickle.dump(predictions_rf, open("Outputs/predictions_rf.pkl", "wb"))
        predictions_rf = pickle.load(open("Outputs/predictions_rf.pkl", "rb"))
        
        display_model_results(predictions_rf, y_test)
    '''
    The random forest model produces more accurate predictions. All error metrics are significantly lower than the linear
    regression and the R2 is 99%. The residual plot has also greatly improved, showing less clear patterns and a fairly even spread about the
    zero line. The Q-Q plot shows a significant deviation from the 45 degree line. This indicates that the residuals are not normally distributed. This could be
    due to outliers or a sign of unmodeled complexity. Given more time, a deeper residual analysis and additional modeling 
    would be warranted. 
    '''
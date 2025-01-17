#!/usr/bin/env python
"""
File: inputs.py
Author: Andrew Klavekoske
Last Updated: 2024-07-22

Description: An inputs file to store functions needed as 
inputs to the main simulation file main.py. get_weather_data() fetches local weather
data from the NREL NSRDB API.
"""
import requests
import pandas as pd
import urllib.parse
import time
from io import StringIO
from dotenv import load_dotenv
import os
import streamlit as st

@st.cache_data
def get_weather_data(lat, lon, year, interval, attributes, resample="5min"):
    print(f"Getting weather data for {year} at {lat}, {lon}...")
    # ----------------------------- Request data from API --------------------------------------
    load_dotenv()
    API_KEY = st.secrets["API_KEY"] #os.getenv("API_KEY")
    BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-5min-download.csv"
    FULL_NAME = st.secrets["FULL_NAME"]#os.getenv("FULL_NAME")
    EMAIL = st.secrets["EMAIL"] #os.getenv("EMAIL")
    url = f"{BASE_URL}?api_key={API_KEY}"
    payload = {
        "names": year,
        "leap_day": "false",
        "interval": interval,
        "utc": "false",
        "full_name": FULL_NAME,
        "email": EMAIL,
        "affiliation": "NREL",
        "mailing_list": "true",
        "reason": "Personal",
        "attributes": attributes,
        "wkt": f"POINT({lon} {lat})",
    }
    # Convert dictionary to URL-encoded query string
    payload_string = urllib.parse.urlencode(payload)
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    time.sleep(1)
    response = requests.request("GET", url, data=payload_string, headers=headers)
    if response.status_code != 200:
        print(
            f"An error has occurred with the server or the request. The request response code/status: {response.status_code} {response.reason}"
        )
        print(f"The response body: {response.text}")
        exit(1)
    else:
        print(f"The request was successful (Response code: {response.status_code})...")
    # --------------------------- Clean data --------------------------------------------------
    print("Cleaning data...")
    data = StringIO(response.text)
    df = pd.read_csv(data, low_memory=False)
    # Create a new DataFrame with the first two rows
    metadata_df = df.iloc[:1].copy()
    # Use the second row (index 1) as the new column headers
    df.columns = df.iloc[1]
    # Remove the first two rows from the original DataFrame
    df = df.iloc[2:].reset_index(drop=True)
    # create the timestamp column
    df["timestamp"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
    # keep only relevant columns
    df = df[["timestamp", "GHI", "Clearsky GHI", "Temperature"]]
    # set index to timestamp
    df = df.set_index("timestamp")
    # convert to numeric
    df = df.apply(pd.to_numeric, errors="coerce")
    # resample based on resample parameter
    df = df.resample(resample).interpolate()
    print(f"Done cleaning data. Weather is in {resample} intervals...")
    df.to_parquet("Outputs/weather_data.parquet")
    
# Weather parameters
# year = '2022'
# lat = '39.8818'
# lon = '-105.0552'
# interval = '5'
# attributes = 'ghi,clearsky_ghi,air_temperature'
# 
#inputs.get_weather_data(lat, lon, year, interval, attributes,sim_step) # 5min data
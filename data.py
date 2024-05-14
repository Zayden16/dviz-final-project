import json

import requests
import pandas as pd
from datetime import datetime
from util import base_url, country_code, process_timestamps

cache = {}

def get_public_power(start_date, end_date, desired_types):
    """Fetch and process public power production data within the specified date range.

    Parameters:
    - start_date (str): Start date in ISO format.
    - end_date (str): End date in ISO format.
    - desired_types (list): List of desired production types to filter the data.
    """
    cache_key = (start_date, end_date, tuple(desired_types))

    if cache_key in cache:
        print("Using cached data")
        return cache[cache_key]

    start_datetime = datetime.fromisoformat(start_date).strftime('%Y-%m-%dT%H:%M:%S%z')
    end_datetime = datetime.fromisoformat(end_date).strftime('%Y-%m-%dT%H:%M:%S%z')
    url = base_url + 'public_power'
    params = {
        'country': country_code,
        'start': start_datetime,
        'end': end_datetime
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return pd.DataFrame()  # Return an empty DataFrame in case of failure.

    data = response.json()
    timestamps = process_timestamps(data['unix_seconds'])
    production_data = data['production_types']
    exclude_types = ["Residual load", "Renewable share of generation", "Renewable share of load"]

    df = pd.DataFrame()

    for entry in production_data:
        if entry['name'] in exclude_types or (desired_types and entry['name'] not in desired_types):
            continue

        df_entry = pd.DataFrame({
            'Time': timestamps,
            'Production Type': entry['name'],
            'Power (MW)': entry['data']
        })

        df = pd.concat([df, df_entry], ignore_index=True)

    cache[cache_key] = df
    return df


def get_energyreporter_data():
    data_path = "./data/energyreporter_municipality_historized.csv"
    energy_data = pd.read_csv(data_path)

    return energy_data

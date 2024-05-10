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


def get_treemap_data():
    data_path = "./data/energyreporter_municipality_historized.csv"
    energy_data = pd.read_csv(data_path)

    with open("./data/canton_population_2022.json", "r") as file:
        population_data = json.load(file)
    population_df = pd.DataFrame(population_data.items(), columns=["canton", "population"])

    energy_data["renelec_production_date_from"] = pd.to_datetime(
        energy_data["renelec_production_date_from"]
    )
    year_filter = 2022
    filtered_data = energy_data[
        energy_data["renelec_production_date_from"].dt.year == year_filter
    ].copy()

    filtered_data.fillna(0, inplace=True)

    aggregated_data = (
        filtered_data.groupby("canton")
        .agg(
            {
                "renelec_production_water_mwh_per_year": "sum",
                "renelec_production_solar_mwh_per_year": "sum",
                "renelec_production_wind_mwh_per_year": "sum",
                "renelec_production_biomass_mwh_per_year": "sum",
                "renelec_production_waste_mwh_per_year": "sum",
            }
        )
        .reset_index()
    )

    aggregated_data = pd.merge(aggregated_data, population_df, on="canton", how="left")

    sources = ["water", "solar", "wind", "biomass", "waste"]
    for source in sources:
        col_name = f"{source}_per_capita"
        energy_col = f"renelec_production_{source}_mwh_per_year"
        aggregated_data[col_name] = (
            aggregated_data[energy_col] / aggregated_data["population"]
        ).round(2)

    return aggregated_data
import requests
import pandas as pd
from datetime import datetime
from util import base_url, country_code, process_timestamps

cache = {}

def get_public_power(start_date, end_date):
    """Fetch and process public power production data within the specified date range."""
    cache_key = (start_date, end_date)

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
        return pd.DataFrame()

    data = response.json()
    timestamps = process_timestamps(data['unix_seconds'])
    production_data = data['production_types']

    df_list = []
    hydro_data = None
    exclude_types = ["Residual load", "Renewable share of generation", "Renewable share of load"]

    for entry in production_data:
        if entry['name'] in exclude_types:
            continue
        if entry['name'] == 'Wind onshore':
            entry['name'] = 'Wind'

        df = pd.DataFrame({
            'Time': timestamps,
            'Production Type': entry['name'],
            'Power (MW)': entry['data']
        })

        if 'Hydro' in entry['name']:
            if hydro_data is None:
                hydro_data = df
            else:
                hydro_data['Power (MW)'] += df['Power (MW)']
        else:
            df_list.append(df)

    if hydro_data is not None:
        hydro_data['Production Type'] = 'Hydro'
        df_list.append(hydro_data)

    final_df = pd.concat(df_list, ignore_index=True)

    cache[cache_key] = final_df
    return final_df

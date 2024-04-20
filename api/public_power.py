import requests
import pandas as pd
from datetime import datetime
from util import base_url, country_code, process_timestamps

def fetch_data(url, params):
    """ Fetch data from the API and return the JSON response. """
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return None

def aggregate_hydro_data(df_list, hydro_data):
    """ Aggregate Hydro production types into one category and append to the list of dataframes. """
    if hydro_data is not None:
        hydro_data['Production Type'] = 'Hydro'
        df_list.append(hydro_data)

def process_production_data(production_data, timestamps):
    """ Process the production data from the API response into a DataFrame. """
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

    aggregate_hydro_data(df_list, hydro_data)

    return pd.concat(df_list, ignore_index=True)

def get_public_power(start_date, end_date):
    """ Retrieve public power production data between specified start and end dates. """
    start_datetime = datetime.fromisoformat(start_date).strftime('%Y-%m-%dT%H:%M:%S%z')
    end_datetime = datetime.fromisoformat(end_date).strftime('%Y-%m-%dT%H:%M:%S%z')

    url = base_url + 'public_power'
    params = {
        'country': country_code,
        'start': start_datetime,
        'end': end_datetime
    }

    data = fetch_data(url, params)
    if data:
        timestamps = process_timestamps(data['unix_seconds'])
        return process_production_data(data['production_types'], timestamps)
    return pd.DataFrame()

import os, requests
import pandas as pd
import streamlit as st
import json
import datetime as dt


"""
Reads json-file given by Fingrid's open data API and converts it to list of timestamps and values
"""

def get_data_from_fg_api_with_start_end(variableid, start, end, apikey):

    headers = {'x-api-key': apikey}
    start_str = start.strftime("%Y-%m-%dT") + "00:00:00"
    end_str = end.strftime("%Y-%m-%dT") + "23:59:00"
    res = requests.api.get(f'https://data.fingrid.fi/api/datasets/{variableid}/data?startTime={start_str}Z&'
                           f'endTime={end_str}Z&format=json&oneRowPerTimePeriod=true&pageSize=20000&'
                           f'locale=fi&sortBy=startTime&sortOrder=asc',
                           headers=headers)
    res_decoded = res.content.decode('utf-8')
    response = json.loads(res_decoded)
    df = pd.DataFrame(response['data'])
    # Check for pagination
    num_of_pages = response['pagination']['lastPage']
    
    # If multiple pages, loop through and get all data
    if num_of_pages > 1:
        for page in range(2, num_of_pages + 1):
            next_res = requests.api.get(
                f'https://data.fingrid.fi/api/datasets/{variableid}/data?startTime={start_str}Z&'
                f'endTime={end_str}Z&format=json&oneRowPerTimePeriod=true&pageSize=20000&page={page}&'
                f'locale=fi&sortBy=startTime&sortOrder=asc',
                headers=headers)
            next_res_decoded = next_res.content.decode('utf-8')
            next_df = pd.DataFrame(json.loads(next_res_decoded)['data'])
            df = pd.concat([df, next_df])
    # Handle potential additional JSON data from Datahub data
    if len(df.columns) > 3:
        df.columns = ['Timestamp', 'End', 'Value', 'JSON']
        df['JSON'] = df['JSON'].apply(json.loads)
        new_df = pd.json_normalize(df['JSON'])
        new_df.drop(['Value'], inplace=True, axis=1)
        new_df.index = df.index
        df = pd.concat([df, new_df], axis=1)
        df.drop(['End', 'JSON', 'TimeSeriesType', 'Res', 'Uom', 'ReadTS', 'Count'], inplace=True, axis=1)
    else:
        df.columns = ['Timestamp', 'End', 'Value']

        df.drop(['End'], inplace=True, axis=1)
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_convert('Europe/Helsinki')
    df.set_index('Timestamp', inplace=True)
    return df

def search_fg_api(searchkey, apikey):
    headers = {'x-api-key': apikey}
    res = requests.api.get(f"https://data.fingrid.fi/api/datasets?search={searchkey}&orderBy=id",
                    headers=headers)
    res_decoded = res.content.decode('utf-8')

    response = json.loads(res_decoded)
    df = pd.DataFrame(response['data'])
    return df

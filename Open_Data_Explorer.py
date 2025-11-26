
import os
import pandas as pd
import streamlit as st
import plotly.express as px

from streamlit_extras.chart_container import chart_container
from src.fingridapi import get_data_from_fg_api_with_start_end, search_fg_api
from src.general_functions import aggregate_data, sidebar_contact_info
from datetime import datetime, timedelta, date
import time

st.set_page_config(
    page_title="EnergiaData - Wind and Power System Statistics",
    page_icon="https://i.imgur.com/Kd4P3y2.png",
    layout='wide',
    initial_sidebar_state='expanded'
)


@st.cache_data(show_spinner=False)
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")


@st.cache_data(show_spinner=False, max_entries=200)
def get_data_df(start, end, id, nimi, api_key):
    """
    Get the production and  demand values from Fingrid API between the start and end dates
    :param start: start date
    :param end: end date
    :return: production dataframe with demand values included
    """
    df = get_data_from_fg_api_with_start_end(id, start, end, api_key)
    df.rename({'Value': nimi}, axis=1, inplace=True)
    return df


def click_button():
    st.session_state.clicked = True


def search_button_click():
    st.session_state.search = True


@st.cache_data(show_spinner=False, max_entries=200)
def search_data_df(search_key, api_key):
    search_df = search_fg_api(search_key, api_key)
    search_df = search_df[['nameEn', 'id', 'dataPeriodEn', 'unitEn', 'searchScore', 'descriptionEn']]
    search_df.insert(0, 'search', False)
    return search_df

datahub_mapping = {
    'BE01': 'Apartments, block of flats',
    'BE02': 'Apartments, small house (row, semi-detached, detached), electric heating',
    'BE03': 'Apartments, small house (row, semi-detached, detached), non-electric heating',
    'BE04': 'Apartments, holiday home',
    'BE05': 'Residential properties',
    'BE06': 'Agricultural production (TOL A)',
    'BE07': 'Industry (TOL B and C)',
    'BE08': 'Community or energy and water supply (TOL D, E)',
    'BE09': 'Construction (temporary electricity) (TOL F)',
    'BE10': 'Services',
    'BE11': 'Outdoor lighting',
    'BE12': 'Electric car charging points',
    'BE13': 'Traffic',
    'BE14': 'Other site',
    'AB01': 'Company',
    'AB02': 'Consumer',
    'AV01': 'Hydropower',
    'AV02': 'Wind power',
    'AV03': 'Nuclear power',
    'AV04': 'Gas turbine',
    'AV05': 'Diesel engine',
    'AV06': 'Solar power',
    'AV07': 'Wave power',
    'AV08': 'Combined heat and power',
    'AV09': 'Biopower',
    'AV10': 'Other production',
    'AV11': 'Wind power, offshore',
    'AV12': 'Energy storage',
    '0': '0-2000 kWh',
    '2k': '2000-20 000 kWh',
    '20k': '20 000-100 000 kWh',
    '100k': 'over 100 000 kWh',
    'E13': 'Continuous measurement',
    'E14': 'Reading measurement',
    'E16': 'Unmetered'
}

with st.sidebar:
    sidebar_contact_info()

if 'clicked' not in st.session_state:
    st.session_state.clicked = False
if 'search' not in st.session_state:
    st.session_state.search = False
if 'fetced' not in st.session_state:
    st.session_state.fetched = False

st.header('Fingrid Open Data Explorer ⚡')

user_api_key = st.text_input("Enter your own API key for searching:")
env_api_key = os.environ.get("FGAPIKEY", "")
api_key = user_api_key if user_api_key else env_api_key
st.markdown(
    "You can obtain an API key by registering / logging in at [data.fingrid.fi](https://data.fingrid.fi/en/instructions)  \n"
    "The API key is not stored anywhere else except only in the browser's memory during the session. If you do not enter a key, the application will use a default key with limited search capabilities.")

with st.expander("Search and select data sources"):
    search_key = st.text_input("Enter a search key for the data source you are looking for:")
    button = st.button("Search", on_click=click_button)

    if st.session_state.clicked and api_key:
        try:
            search_df = search_data_df(search_key, api_key)
            search_score_max = search_df['searchScore'].max()

        except KeyError as e:
            st.error("An error occurred during the search, results may not have been found. You can also try again or check the API key.")
            st.session_state.clicked = False
            st.session_state.search = False
            st.session_state.fetched = False
    

    if st.session_state.clicked:
        
        end = datetime.now()
        st.write("Select the time range for which you want to fetch data:")
        col1, col2, _ = st.columns(3)
        if user_api_key:
            min_start_date = date(2015, 1, 1)
            default_start_date = date(2025, 1, 1)
        else:
            #only allow last week if no user api key
            min_start_date = date.today() - timedelta(7)
            default_start_date = date.today() - timedelta(7)
        with col1:


            start_date = st.date_input("Start date", default_start_date,
                                       min_value=min_start_date,
                                       max_value=end)
        with col2:
            end_date = st.date_input("End date", end,
                                     min_value=start_date,
                                     max_value=end)
            
        if not user_api_key:
            st.warning("Set your own API key to enable searching for longer period.")
        st.write("Select the data sources you want")
        with st.form("data_search"):
            edited_df = st.data_editor(
                search_df,
                column_config={
                    "nameEn": "Name",
                    "id": "ID",
                    'dataPeriodEn': "Measurement interval",
                    'unitEn': 'Unit',
                    'searchScore': st.column_config.ProgressColumn(
                        "Search match accuracy",
                        help="How well the search key matches this data source",
                        format="%d",
                        min_value=0,
                        max_value=search_score_max,
                    ),
                    "search": st.column_config.CheckboxColumn(
                        "Search?",
                        help="Select the data sources you want",
                        default=False,
                    ),
                    'descriptionEn': "Description"

                },
                disabled=["nameEn", "id", 'dataPeriodEn', 'unitEn', 'searchScore', 'descriptionEn'],
                hide_index=True,
            )

            search_data = st.form_submit_button("Fetch data", on_click=search_button_click)
df_list = []
if st.session_state.search:
    st.header("Search results:")

    for i, row in edited_df[edited_df['search'] == True].iterrows():
        data_id = row['id']
        data_name = row['nameEn']
        data_unit = row['unitEn']
        data_period = row['dataPeriodEn']
        with st.status(f"{data_name}"):
            if (end_date - start_date > timedelta(28)) and data_period == "3 min":
                st.toast(f'Data search {data_name} measurement interval is 3 min and may take longer to fetch')
            try:
                data = get_data_df(start_date, end_date, data_id, data_name, api_key)
            except Exception as e:
                st.info(f"Error fetching data for {data_name}: {e}. Retrying in 2 seconds...")
                time.sleep(2)
                try:
                    data = get_data_df(start_date, end_date, data_id, data_name, api_key)
                except Exception as e2:
                    st.error(f"Failed to fetch data for {data_name} after retry: {e2}")
                    continue

            # Handle Datahub data
            if len(data.columns) > 1:
                cols = list(data.columns[1:])
                data = pd.pivot_table(data=data, index=data.index, columns=cols, values=data_name)
                # Flatten multi-index columns
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [(datahub_mapping[col[0]], datahub_mapping[col[1]]) for col in data.columns]
                    data.columns = [' - '.join(col).strip() for col in data.columns]
                else:
                    data.columns = [datahub_mapping[col] for col in data.columns]

            else:
                df_list.append(data)
            with chart_container(data, ["Chart 📈", "Data 📄", "Download 📁"], ["CSV"]):
                fig = px.line(data)
                fig.update_traces(line=dict(width=2.5))
                fig.update_layout(dict(yaxis_title=data_unit, legend_title="Time series", yaxis_tickformat=".2r",
                                       yaxis_hoverformat=".1f"))
                st.plotly_chart(fig, use_container_width=True)

                # Add ability to copy API call for the data
                with st.expander("Show API call for this data"):
                    start_str = start_date.strftime("%Y-%m-%dT00:00:00")
                    end_str = end_date.strftime("%Y-%m-%dT23:59:59")
                    api_call = (
                        f"https://data.fingrid.fi/api/datasets/{data_id}/data?"
                        f"startTime={start_str}Z&endTime={end_str}Z&format=json&oneRowPerTimePeriod=true&"
                        f"pageSize=20000&locale=fi&sortBy=startTime&sortOrder=asc"
                    )
                    st.code(api_call, language='html')
        # sleep for a short while to avoid overwhelming the API
        time.sleep(0.5)
    st.session_state.fetched = True
if st.session_state.fetched and len(df_list) > 1:
    with st.status("Combined searches", expanded=True):
        aggregation_selection = st.radio('Select data aggregation level',
                                         ['3min', '15min', 'Hour', 'Day', 'Week', 'Month'],
                                         key="search_agg", horizontal=True, index=2)

        all_data = pd.concat(df_list, axis=1)
        all_data = aggregate_data(all_data, aggregation_selection, 'ffill')
        with chart_container(all_data, ["Chart 📈", "Data 📄", "Download 📁"], ["CSV"]):
            fig = px.line(all_data)
            fig.update_traces(line=dict(width=2.5))
            fig.update_layout(dict(yaxis_title="", legend_title="Time series", yaxis_tickformat=".2r",
                                   yaxis_hoverformat=".1f"))
            st.plotly_chart(fig, use_container_width=True)

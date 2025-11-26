import streamlit as st
import pandas as pd
from streamlit_extras.mention import mention

import datetime



def get_general_layout(start=None):
    # Start of the page
    end = datetime.datetime.now()
    st.sidebar.subheader("Valitse aikaikkuna 📆")
    if start is not None:
        default = datetime.date(2018, 1, 1)
    else:
        if 'current_start_date' in st.session_state:
            default = st.session_state['current_start_date']
        else:
            default = datetime.date(2024, 1, 1)

    # Setup date inputs so user can select their desired date range but make sure they don't non-feasible date ranges
    # start_date cannot go over end_date, and we need to save end_date to session_state in case user changed end_date

    if 'current_end_date' not in st.session_state:
        start_date = st.sidebar.date_input("Päivä alkaen", default,
                                           min_value=datetime.date(2015, 1, 1),
                                           max_value=end)
        end_date = st.sidebar.date_input("Päivä saakka", end,
                                         min_value=start_date,
                                         max_value=end, key='current_end_date')
    else:
        start_date = st.sidebar.date_input("Päivä alkaen", default,
                                           min_value=datetime.date(2015, 1, 1),
                                           max_value=st.session_state['current_end_date'])
        end_date = st.sidebar.date_input("Päivä saakka", st.session_state['current_end_date'],
                                         min_value=start_date,
                                         max_value=end, key='current_end_date')
    if start is None:
        st.session_state['current_start_date'] = start_date
    aggregation_selection_selection = st.sidebar.radio('Valitse aggregointitaso 🕑', ['Tunti', 'Päivä', 'Viikko', 'Kuukausi'])

    # Add contact info and other information to the end of sidebar
    with st.sidebar:
        sidebar_contact_info()

    return start_date, end_date, aggregation_selection_selection


def sidebar_contact_info():
    # Setup sidebar contact and other info

    st.subheader("Contact:")
    mention(
        label="Pekko Niemi",
        icon="X",
        url="https://X.com/PekkoNiemi"
    )
    mention(
        label="Source code",
        icon="github",
        url="https://github.com/pekkon/EnergiaDataApp"
    )
    st.markdown('Data source:  \n[Fingrid Open Data](https://data.fingrid.fi),  '
                'license [CC 4.0 BY](https://creativecommons.org/licenses/by/4.0/)')



@st.cache_data(show_spinner=False, max_entries=200)
def aggregate_data(df, aggregation_selection, agg_level='mean'):
    """
    Aggregates the given data based on user selected aggregation_selection level
    :param df: dataframe
    :param aggregation_selection: aggregation_selection level
    :return: aggregated dataframe
    """
    if aggregation_selection == 'Päivä':
        agg = 'D'
    elif aggregation_selection == 'Viikko':
        agg = 'W-MON'
    elif aggregation_selection == 'Kuukausi':
        agg = 'MS'
    elif aggregation_selection == '3min':
        agg = '3min'
    elif aggregation_selection == '15min':
        agg = '15min'
    else:
        agg = 'H'
    if agg_level == 'mean':
        return df.resample(agg).mean().round(1)
    elif agg_level == 'sum':
        return df.resample(agg).sum().round(1)
    elif agg_level == 'ffill':
        return df.resample(agg).mean().ffill()
    else:
        return df.resample(agg)

def check_previous_data(old_df, start_time):
    # Identify the last date in the existing data
    if not old_df.empty:
        return old_df.index.max() + datetime.timedelta(hours=1)
    else:
        return pd.to_datetime(start_time) - datetime.timedelta(hours=1)

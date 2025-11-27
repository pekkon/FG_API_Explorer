import streamlit as st
import pandas as pd
from streamlit_extras.mention import mention

import datetime





def sidebar_contact_info():
    # centered logo at the top of the sidebar
    st.image("./src/logo.png", width=80)
    # Introduction text
    
    st.title("Fingrid Open Data Explorer")
    st.markdown(
        "This application allows you to explore and visualize data from Fingrid's Open Data API. "
        "You can search for various data sources, select the ones you are interested in, and visualize the data over a specified time range. "
        "The application supports different aggregation levels to help you analyze the data effectively."
    )
    # Disclaimer, small text
    st.markdown(
        "<small>Disclaimer: This application is not affiliated with Fingrid. It is developed for educational and exploratory purposes only. "
        "Please verify any critical data directly from Fingrid's official resources. And please don't misuse the data or the application.</small>",
        unsafe_allow_html=True
    )

    # Add a horizontal line
    st.markdown("---")

    # Setup sidebar contact and other info

    st.subheader("Contact:")
    mention(
        label="Pekko Niemi",
        url="https://linkedin.com/in/pekko-niemi"
    )
    mention(
        label="Source code",
        icon="github",
        url="https://github.com/pekkon/FG_API_Explorer"
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
    if aggregation_selection == 'Day':
        agg = 'D'
    elif aggregation_selection == 'Week':
        agg = 'W-MON'
    elif aggregation_selection == 'Month':
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

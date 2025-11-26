# Fingrid Open Data Explorer ⚡

A modern Streamlit web application for exploring, visualizing, and downloading data from Fingrid's Open Data API.

## Features
- Search and select from Fingrid's open data sources
- Visualize time series data with interactive charts (Plotly)
- Download data as CSV
- Aggregation options: 3min, 15min, Hour, Day, Week, Month
- Datahub and multi-index data support
- API call preview for each dataset

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/pekkon/EnergiaDataApp.git
   cd EnergiaDataApp
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   If `requirements.txt` is missing, install manually:
   ```sh
   pip install streamlit pandas plotly streamlit-extras requests
   ```

### Running the App
1. (Optional) Set your Fingrid API key as an environment variable:
   - On Windows (PowerShell):
     ```sh
     $env:FGAPIKEY = "your_api_key_here"
     ```
   - On Linux/macOS:
     ```sh
     export FGAPIKEY=your_api_key_here
     ```
2. Start the app:
   ```sh
   streamlit run Open_data_explorer.py
   ```
3. Open your browser to the provided local URL.

## Usage
- Enter your own API key in the sidebar for full access, or use the default (limited) key from the environment variable.
- Search for data sources, select time range and sources, and visualize or download the data.
- For longer time ranges, you must provide your own API key.

## Project Structure
```
Open_data_explorer.py         # Main Streamlit app
src/
    fingridapi.py             # API interaction functions
    general_functions.py      # Aggregation, sidebar, and helpers
```

## Data Source & License
- Data: [Fingrid Open Data](https://data.fingrid.fi)
- License: [CC 4.0 BY](https://creativecommons.org/licenses/by/4.0/)

## Contact
- Author: Pekko Niemi ([LinkedIn](https://linkedin.com/in/pekko-niemi))
- Source: [GitHub](https://github.com/pekkon/EnergiaDataApp)

## Disclaimer
This application is not affiliated with Fingrid. It is for educational and exploratory purposes only. Please verify any critical data directly from Fingrid's official resources.

# Climate Change Analysis using Google Earth Engine

## Overview
This project utilizes Google Earth Engine (GEE) and Python to analyze the levels of Carbon Monoxide (CO), Methane (CH4), and Nitrogen Dioxide (NO2) over selected locations. Users can click on a map to select a location, and the system will extract monthly averaged gas concentration data from Sentinel-5P satellite images.

## Features
- Interactive map selection for analyzing gas emissions.
- Extraction of CO, CH4, and NO2 data from Sentinel-5P.
- Data processing and storage in CSV and GeoJSON formats.
- Automated report generation for further analysis.

## Requirements
To run this project, ensure you have the following dependencies installed:

- Python 3.8+
- Google Earth Engine (GEE) API
- geemap
- pandas

You can install the dependencies using:
```sh
pip install earthengine-api geemap pandas
```

## Setup Instructions
1. **Authenticate with Google Earth Engine:**
   ```sh
   earthengine authenticate
   ```

2. **Run the Python Script:**
   ```sh
   python gee_co_analysis.py
   ```

3. **Interact with the Map:**
   - Click on a location to retrieve emissions data.
   - The extracted data is saved as `Gas_Emissions.csv` and `Gas_Emissions.geojson`.

## Output
The script generates:
- **Gas_Emissions.csv** - A tabular representation of gas concentration levels over time.
- **Gas_Emissions.geojson** - A geographical dataset for spatial analysis.

## Data Source
The data is sourced from:
- **Sentinel-5P**: Copernicus Atmosphere Monitoring Service (CAMS) for greenhouse gas monitoring.


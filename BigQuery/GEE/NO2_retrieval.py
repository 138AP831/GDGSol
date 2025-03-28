import ee
import geemap
import pandas as pd

# Initialize Earth Engine
ee.Initialize()

# Load administrative boundaries
admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

# Define analysis years
analysis_start_year = 2020
analysis_end_year = 2024

# Sentinel-5P CO, Methane, and NO2 image collections
sentinel5p_co = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO")\
    .select(['CO_column_number_density'], ['CO'])\
    .filterDate(f"{analysis_start_year}-01-01", f"{analysis_end_year}-12-31")

sentinel5p_ch4 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CH4")\
    .select(['CH4_column_volume_mixing_ratio_dry_air'], ['methane'])\
    .filterDate(f"{analysis_start_year}-01-01", f"{analysis_end_year}-12-31")

sentinel5p_no2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")\
    .select(['NO2_column_number_density'], ['NO2'])\
    .filterDate(f"{analysis_start_year}-01-01", f"{analysis_end_year}-12-31")

# Function to extract monthly CO, Methane, and NO2 data at a given point
def get_gas_data(lon, lat):
    point_geometry = ee.Geometry.Point(lon, lat)
    
    month_range = list(range(1, 13))
    years = list(range(analysis_start_year, analysis_end_year))
    
    monthly_gas_data = []
    
    for year in years:
        for month in month_range:
            monthly_co_image = sentinel5p_co\
                .filter(ee.Filter.calendarRange(year, year, 'year'))\
                .filter(ee.Filter.calendarRange(month, month, 'month'))\
                .mean()
            
            monthly_ch4_image = sentinel5p_ch4\
                .filter(ee.Filter.calendarRange(year, year, 'year'))\
                .filter(ee.Filter.calendarRange(month, month, 'month'))\
                .mean()
            
            monthly_no2_image = sentinel5p_no2\
                .filter(ee.Filter.calendarRange(year, year, 'year'))\
                .filter(ee.Filter.calendarRange(month, month, 'month'))\
                .mean()
            
            date = f"{year}-{str(month).zfill(2)}-01"
            
            co_value = monthly_co_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point_geometry,
                scale=3000,
                maxPixels=1e8
            ).get('CO')
            
            ch4_value = monthly_ch4_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point_geometry,
                scale=3000,
                maxPixels=1e8
            ).get('methane')
            
            no2_value = monthly_no2_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point_geometry,
                scale=3000,
                maxPixels=1e8
            ).get('NO2')
            
            monthly_gas_data.append({
                "date": date,
                "CO_value": co_value.getInfo() if co_value else None,
                "methane_value": ch4_value.getInfo() if ch4_value else None,
                "NO2_value": no2_value.getInfo() if no2_value else None,
                "longitude": lon,
                "latitude": lat
            })
    
    return monthly_gas_data

# Interactive Map Setup
map = geemap.Map()
map.add_basemap("SATELLITE")
map.addLayer(admin_boundaries, {}, "Admin Boundaries")

# Function to handle user click
def handle_click(**kwargs):
    if kwargs.get('lat') and kwargs.get('lng'):
        lon, lat = kwargs['lng'], kwargs['lat']
        print(f"Location selected: Longitude={lon}, Latitude={lat}")
        
        # Fetch CO, Methane, and NO2 data for the selected point
        gas_results = get_gas_data(lon, lat)
        
        # Convert results to DataFrame and export as CSV
        gas_df = pd.DataFrame(gas_results)
        gas_df.to_csv("Gas_Emissions.csv", index=False)
        
        # Export results as GeoJSON
        gas_df.to_json("Gas_Emissions.geojson", orient="records")
        
        print("Gas emissions data exported successfully!")

# Add click event listener
map.on_interaction(handle_click)
map

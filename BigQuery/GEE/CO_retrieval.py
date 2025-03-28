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

# Sentinel-5P CO image collection
sentinel5p_co = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO")\
    .select(['CO_column_number_density'], ['CO'])\
    .filterDate(f"{analysis_start_year}-01-01", f"{analysis_end_year}-12-31")

# Function to extract monthly CO data at a given point
def get_co_data(lon, lat):
    point_geometry = ee.Geometry.Point(lon, lat)
    
    month_range = list(range(1, 13))
    years = list(range(analysis_start_year, analysis_end_year))
    
    monthly_co_data = []
    
    for year in years:
        for month in month_range:
            monthly_image = sentinel5p_co\
                .filter(ee.Filter.calendarRange(year, year, 'year'))\
                .filter(ee.Filter.calendarRange(month, month, 'month'))\
                .mean()
            
            date = f"{year}-{str(month).zfill(2)}-01"
            
            co_value = monthly_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point_geometry,
                scale=3000,
                maxPixels=1e8
            ).get('CO')
            
            monthly_co_data.append({
                "date": date,
                "CO_value": co_value.getInfo() if co_value else None,
                "longitude": lon,
                "latitude": lat
            })
    
    return monthly_co_data

# Interactive Map Setup
map = geemap.Map()
map.add_basemap("SATELLITE")
map.addLayer(admin_boundaries, {}, "Admin Boundaries")

# Function to handle user click
def handle_click(**kwargs):
    if kwargs.get('lat') and kwargs.get('lng'):
        lon, lat = kwargs['lng'], kwargs['lat']
        print(f"Location selected: Longitude={lon}, Latitude={lat}")
        
        # Fetch CO data for the selected point
        co_results = get_co_data(lon, lat)
        
        # Convert results to DataFrame and export as CSV
        co_df = pd.DataFrame(co_results)
        co_df.to_csv("CO_Emissions.csv", index=False)
        
        # Export results as GeoJSON
        co_df.to_json("CO_Emissions.geojson", orient="records")
        
        print("CO emissions data exported successfully!")

# Add click event listener
map.on_interaction(handle_click)
map

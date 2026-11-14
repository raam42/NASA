import ee
import pandas as pd
import datetime

def init_earth_engine():
    """
    Safely initializes the Google Earth Engine API.
    In a deployed Streamlit app, this requires a Service Account JSON.
    For local hackathon testing, it prompts a browser login if unauthenticated.
    """
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()

def mask_l89_clouds(image):
    """
    Masks clouds and cloud shadows in Landsat 8 & 9 Surface Reflectance images.
    This ensures your NDVI/NDWI data isn't corrupted by atmospheric noise.
    """
    qa = image.select('QA_PIXEL')
    # Bit 3 is cloud, Bit 4 is cloud shadow
    cloud_shadow_bit_mask = 1 << 4
    clouds_bit_mask = 1 << 3
    
    mask = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0) \
             .And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
    
    return image.updateMask(mask)

def add_indices(image):
    """
    Calculates and adds NDVI and NDWI bands to the image.
    For Landsat 8 and 9:
    - NIR is Band 5 (B5)
    - Red is Band 4 (B4)
    - Green is Band 3 (B3)
    """
    # NDVI: (NIR - Red) / (NIR + Red) -> Measures vegetation health/canopy loss
    ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
    
    # NDWI: (Green - NIR) / (Green + NIR) -> Measures water stress/desiccation
    ndwi = image.normalizedDifference(['B3', 'B5']).rename('NDWI')
    
    return image.addBands([ndvi, ndwi])

def get_satellite_timeseries(roi_geometry, start_date, end_date):
    """
    Extracts a time series of mean NDVI and NDWI over a specific geographical polygon.
    Returns a Pandas DataFrame.
    """
    # 1. Load Landsat 8 and 9 Surface Reflectance collections
    l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
    
    # Merge the collections to get a denser time series
    landsat = l8.merge(l9)
    
    # 2. Filter by location, date, and apply the cloud mask and indices
    collection = landsat.filterBounds(roi_geometry) \
                        .filterDate(start_date, end_date) \
                        .map(mask_l89_clouds) \
                        .map(add_indices)
                        
    # 3. Extract the data. We use a mapped function to reduce the region to a single mean value per date.
    def extract_mean(image):
        date = image.date().format('YYYY-MM-dd')
        means = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi_geometry,
            scale=30, # Landsat native resolution is 30 meters
            maxPixels=1e9
        )
        return ee.Feature(None, {
            'date': date,
            'NDVI': means.get('NDVI'),
            'NDWI': means.get('NDWI')
        })

    # Execute the extraction
    time_series_features = collection.map(extract_mean).getInfo()['features']
    
    # 4. Clean up the data into a Pandas DataFrame
    data = []
    for feat in time_series_features:
        props = feat['properties']
        # Filter out days where the entire polygon was masked by clouds (resulting in None)
        if props['NDVI'] is not None and props['NDWI'] is not None:
            data.append({
                'date': props['date'],
                'NDVI': props['NDVI'],
                'NDWI': props['NDWI']
            })
            
    df = pd.DataFrame(data)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
    return df

def analyze_canopy_stress(df, ndvi_threshold=0.30):
    """
    Flags dates where the NDVI drops below the critical threshold, 
    indicating mangrove canopy stress or death.
    """
    if df.empty:
        return df
        
    # Create a boolean column that flags if the NDVI is below the critical 0.30 mark
    df['critical_stress'] = df['NDVI'] < ndvi_threshold
    return df
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

def load_territorial_database(location="maracaibo"):
    """
    Loads the community-indexed territorial indicators.
    Returns a GeoDataFrame containing the Cultural Sky nodes.
    """
    if location == "maracaibo":
        # Data for Santa Rosa de Agua (Venezuela)
        data = [
            {
                "id": "anu_voice_01",
                "category": "Memory & Toponymy",
                "title": "Abuela Sabia - Canto del Manglar",
                "description": "Real Añú voice recording indexing historical water levels.",
                "indicator": "Audio",
                "audio_path": "data/audio/anu_canto_01.mp3",
                "lat": 10.7180, 
                "lon": -71.6020
            },
            {
                "id": "bio_crab_01",
                "category": "Biodiversity",
                "title": "Avistamiento: Cangrejo Azul",
                "description": "Direct community registry of blue crab absence (proxy for habitat fragmentation invisible to 30m satellites).",
                "indicator": "Blue Crab",
                "audio_path": None,
                "lat": 10.7205, 
                "lon": -71.6055
            },
            {
                "id": "socio_fish_01",
                "category": "Socioproduction",
                "title": "Zona de Pesca Artesanal",
                "description": "Current artisanal fishing status and daily catch reduction.",
                "indicator": "Fishing",
                "audio_path": None,
                "lat": 10.7150, 
                "lon": -71.6100
            }
        ]
    elif location == "donana":
        # Data for Doñana National Park (Spain)
        data = [
            {
                "id": "guard_mem_01",
                "category": "Memory & Toponymy",
                "title": "Memoria de Guardas Tradicionales",
                "description": "Historical water usage and seasonal marsh flooding memory.",
                "indicator": "Historical Water",
                "audio_path": "data/audio/donana_guarda_01.mp3",
                "lat": 36.9850, 
                "lon": -6.4450
            },
            {
                "id": "bio_lynx_01",
                "category": "Biodiversity",
                "title": "Avistamiento: Lince Ibérico",
                "description": "Direct registry of Iberian Lynx tracks, indicating shifting habitat edges.",
                "indicator": "Iberian Lynx",
                "audio_path": None,
                "lat": 37.0100, 
                "lon": -6.4200
            }
        ]
    else:
        data = []

    # Convert the raw dictionaries into a spatially-aware GeoDataFrame
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    return gdf

def create_multimodal_map(gdf, center_lat, center_lon, zoom_start=14):
    """
    Generates an interactive Folium map embedding the cultural nodes.
    Supports embedding HTML audio tags directly into the map popups.
    """
    # Initialize the base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles="CartoDB dark_matter")
    
    # Iterate through the GeoDataFrame and plot each cultural node
    for _, row in gdf.iterrows():
        # Define marker colors based on the category
        if row['category'] == 'Memory & Toponymy':
            color = 'purple'
            icon = 'volume-up'
        elif row['category'] == 'Biodiversity':
            color = 'green'
            icon = 'leaf'
        else:
            color = 'blue'
            icon = 'info-sign'
            
        # Build the HTML popup content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; width: 250px;">
            <h4 style="margin-top: 0; color: #333;">{row['title']}</h4>
            <p style="font-size: 12px; color: #666;"><strong>Category:</strong> {row['category']}</p>
            <p style="font-size: 13px;">{row['description']}</p>
        """
        
        # Inject the HTML audio player if an audio path exists
        if row.get('audio_path'):
            html_content += f"""
            <audio controls style="width: 100%; height: 30px; margin-top: 10px;">
              <source src="{row['audio_path']}" type="audio/mpeg">
              Your browser does not support the audio element.
            </audio>
            """
            
        html_content += "</div>"
        
        # Add the marker to the map
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(html_content, max_width=300),
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon'),
            tooltip=row['title']
        ).add_to(m)
        
    return m
import streamlit as st
import datetime
import ee
from streamlit_folium import st_folium

# Import our custom KATOUWA modules
from modules import (
    01_satellite as sat,
    02_territory as terr,
    03_engine as engine,
    04_synth as synth
)

# 1. Page Configuration & Setup
st.set_page_config(
    page_title="KATOUWA | NASA Space Apps", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Initialize Google Earth Engine (Cache this so it only runs once)
@st.cache_resource
def initialize_gee():
    sat.init_earth_engine()
    return True

initialize_gee()

# 2. Sidebar: The Geographical Switch & Controls
st.sidebar.image("data/assets/katouwa_logo.png", use_column_width=True) # Ensure you have a logo here!
st.sidebar.title("Conmutador Territorial")
st.sidebar.write("Demostración de Replicabilidad Global (NASA)")

location_choice = st.sidebar.radio(
    "Seleccione el Ecosistema:",
    ("Santa Rosa de Agua (Venezuela)", "Doñana (España)")
)

# Map the UI choice to the backend logic & GEE Geometries
if "Venezuela" in location_choice:
    loc_key = "maracaibo"
    # Polygon for Santa Rosa de Agua Mangroves
    roi = ee.Geometry.Polygon([[
        [-71.6200, 10.7100], [-71.5900, 10.7100], 
        [-71.5900, 10.7300], [-71.6200, 10.7300], 
        [-71.6200, 10.7100]
    ]])
    center_lat, center_lon = 10.7180, -71.6020
else:
    loc_key = "donana"
    # Polygon for Doñana National Park Marshes
    roi = ee.Geometry.Polygon([[
        [-6.4600, 36.9700], [-6.4000, 36.9700], 
        [-6.4000, 37.0300], [-6.4600, 37.0300], 
        [-6.4600, 36.9700]
    ]])
    center_lat, center_lon = 36.9950, -6.4300

# Date range for Landsat time series
start_date = st.sidebar.date_input("Fecha Inicio", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("Fecha Fin", datetime.date.today())

# 3. Data Processing (Backend Execution)
with st.spinner("Procesando Cielo Tecnológico (Landsat 8/9) y Cielo Cultural..."):
    # Module 1: Satellite
    sat_df = sat.get_satellite_timeseries(roi, str(start_date), str(end_date))
    sat_df = sat.analyze_canopy_stress(sat_df)
    
    # Module 2: Territory
    terr_gdf = terr.load_territorial_database(loc_key)
    map_obj = terr.create_multimodal_map(terr_gdf, center_lat, center_lon)
    
    # Module 3: Contrast Engine
    imct_results = engine.calculate_imct(sat_df, terr_gdf)
    ab_contrast = engine.generate_ab_contrast(imct_results)
    neruna_status = engine.trigger_neruna_deployment(imct_results['imct_score'])
    
    # Module 4: Sonification (Using the latest NDVI value)
    latest_ndvi = imct_results['ndvi_value']
    translation = synth.get_multimodal_translation(latest_ndvi)

# 4. Main UI Rendering
st.title("KATOUWA: Arquitectura de Continuidad Biocultural")
st.markdown("### Reto: Be An Earth System Trend Detective!")

# ROW 1: The Interactive Map
st.markdown("#### 1. Panel Territorial (Haga clic en los nodos para escuchar las voces)")
st_folium(map_obj, width=1200, height=450)

st.divider()

# ROW 2: The A/B Contrast (Live Pitch Demonstration)
st.markdown("#### 2. Demostración A/B: Detección de Zonas Críticas")
col1, col2 = st.columns(2)

with col1:
    st.info(f"**{ab_contrast['A']['title']}**")
    st.metric("Detección de Estrés (NDVI)", str(latest_ndvi), ab_contrast['A']['detection'])
    st.caption(f"⚠️ Punto Ciego: {ab_contrast['A']['blind_spot']}")

with col2:
    if imct_results['imct_score'] >= 3:
        st.error(f"**{ab_contrast['B']['title']}**")
    elif imct_results['imct_score'] > 0:
        st.warning(f"**{ab_contrast['B']['title']}**")
    else:
        st.success(f"**{ab_contrast['B']['title']}**")
        
    st.write(f"**Estado:** {ab_contrast['B']['detection']}")
    st.write(f"**Valor Añadido:** {ab_contrast['B']['added_value']}")

st.divider()

# ROW 3: Multimodal Translation & Hardware Deployment
st.markdown("#### 3. Traducción Multimodal Accesible (The Earth Information Jukebox)")
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("**Sonificación Matemática (Landsat -> Frecuencia)**")
    st.audio(translation['audio_bytes'], format="audio/wav")
    st.caption(f"Frecuencia base: {translation['frequency_hz']} Hz")
    st.caption("Si el NDVI es < 0.30, se inyecta un armónico disonante para indicar crisis de forma aural.")

with col4:
    st.markdown("**Patrón Vibracional Chladni (Accesibilidad Visual)**")
    st.pyplot(translation['chladni_figure'])

with col5:
    st.markdown("**Respuesta Territorial: Las Ñerunas**")
    if neruna_status['deploy']:
        st.error(f"🚨 {neruna_status['message']}")
        # Place a 3D render or schematic of the floating island here
        # st.image("data/assets/neruna_render.jpg", use_column_width=True) 
    else:
        st.success(f"✅ {neruna_status['message']}")
        
    # THE SCIENTIFIC SHIELD DISCLAIMER
    st.caption(f"*{neruna_status['scientific_disclaimer']}*")

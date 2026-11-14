import pandas as pd
import numpy as np

def calculate_imct(satellite_df, territorial_gdf, current_date=None):
    """
    Computes the contrast between spectral variables and community-indexed 
    territorial indicators to calculate the Multimodal Index (IMCT).
    
    CRITICAL SCIENTIFIC SHIELD: This algorithm does NOT "understand" indigenous 
    culture. It strictly computes the spatial/temporal overlap between biophysical 
    proxies (Landsat) and direct community registries (crabs, fishing).
    """
    if satellite_df.empty or territorial_gdf.empty:
        return None
        
    # Get the latest satellite data if no date is specified
    if current_date is None:
        latest_sat = satellite_df.iloc[-1]
    else:
        # Filter to the closest date
        latest_sat = satellite_df[satellite_df['date'] <= current_date].iloc[-1]

    # 1. Satellite Status (The Technological Sky)
    # Checks if the Landsat 30m proxy detected canopy stress (NDVI < 0.30)
    is_sat_stressed = latest_sat['critical_stress']
    sat_ndvi = latest_sat['NDVI']
    
    # 2. Territorial Status (The Cultural Sky)
    # Counts active community alerts (e.g., missing blue crabs, fishing reduction)
    active_alerts = len(territorial_gdf)
    
    # 3. IMCT Computation Logic
    # 0 = Healthy, 1 = Early Warning (Community Only), 2 = Spectral Anomaly (Sat Only), 3 = Biocultural Crisis (Both)
    imct_score = 0
    imct_status = "Equilibrio (Stable)"
    
    if is_sat_stressed and active_alerts > 0:
        imct_score = 3
        imct_status = "Crisis Biocultural Confirmada (Dual-Sky Alert)"
    elif is_sat_stressed and active_alerts == 0:
        imct_score = 2
        imct_status = "Anomalía Biofísica (Satellite Only)"
    elif not is_sat_stressed and active_alerts > 0:
        imct_score = 1
        imct_status = "Alerta Temprana Territorial (Invisible to 30m Satellite)"
        
    return {
        "date": latest_sat['date'].strftime('%Y-%m-%d'),
        "ndvi_value": round(sat_ndvi, 3),
        "satellite_stress": bool(is_sat_stressed),
        "community_alerts": active_alerts,
        "imct_score": imct_score,
        "imct_status": imct_status
    }

def generate_ab_contrast(imct_results):
    """
    Generates the exact payload needed for the live A/B demonstration in Streamlit.
    Contrasts the 'Satellite Only' view against the 'Multimodal' view.
    """
    if not imct_results:
        return {}

    # State A: What standard NASA Space Apps teams see (Satellite Only)
    sat_only_view = {
        "title": "Visión Unidimensional (Solo Satélite)",
        "detection": "Estrés detectado" if imct_results['satellite_stress'] else "Aparente normalidad",
        "blind_spot": "Incapaz de detectar fauna bajo el dosel o impacto socioeconómico (resolución 30m)."
    }
    
    # State B: What KATOUWA sees (Dual-Sky)
    multimodal_view = {
        "title": "Visión KATOUWA (Cielo Tecnológico + Cultural)",
        "detection": imct_results['imct_status'],
        "added_value": f"Integra {imct_results['community_alerts']} registros directos de la comunidad."
    }
    
    return {
        "A": sat_only_view,
        "B": multimodal_view
    }

def trigger_neruna_deployment(imct_score):
    """
    Activates the recommendation to deploy 'La Ñeruna' (floating island prototype).
    """
    # Only deploy the experimental prototype if we hit a Level 3 Biocultural Crisis
    deploy = imct_score >= 3
    
    message = "Despliegue Recomendado: Las Ñerunas" if deploy else "Monitoreo Pasivo Continuo"
    disclaimer = "Nota Científica: Prototipo experimental derivado de biomimética del mangle. Ingeniería hidrodinámica sujeta a validación post-hackatón."
    
    return {
        "deploy": deploy,
        "message": message,
        "scientific_disclaimer": disclaimer
    }

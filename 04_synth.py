import numpy as np
import scipy.io.wavfile as wav
import io
import matplotlib.pyplot as plt

def ndvi_to_frequency(ndvi_value, min_freq=200, max_freq=800):
    """
    Maps an NDVI value (-1.0 to 1.0) to an audible frequency range (Hz).
    Healthy mangrove (NDVI > 0.3) produces a higher, clearer tone.
    Degraded mangrove (NDVI < 0.3) drops into lower, more dissonant frequencies.
    """
    # Clamp NDVI to a logical range for vegetation (0.0 to 1.0) to avoid extreme outliers
    clamped_ndvi = max(0.0, min(1.0, ndvi_value))
    
    # Linear interpolation between min and max frequencies
    frequency = min_freq + (clamped_ndvi * (max_freq - min_freq))
    return frequency

def generate_sonification_audio(ndvi_value, duration=3.0, sample_rate=44100):
    """
    Uses NumPy and SciPy to synthesize a pure sine wave audio buffer based on the 
    satellite data, ready to be played natively in Streamlit.
    """
    frequency = ndvi_to_frequency(ndvi_value)
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate the sine wave
    wave = np.sin(frequency * t * 2 * np.pi)
    
    # Add a slight harmonic distortion if the mangrove is under stress (< 0.30)
    # to aurally communicate the 'crisis' without needing to look at the screen
    if ndvi_value < 0.30:
        wave += 0.5 * np.sin((frequency * 1.5) * t * 2 * np.pi) # Dissonant harmonic
        
    # Normalize and convert to 16-bit PCM integer
    audio_data = np.int16(wave / np.max(np.abs(wave)) * 32767)
    
    # Write to an in-memory bytes buffer (so Streamlit can play it without saving to disk)
    audio_buffer = io.BytesIO()
    wav.write(audio_buffer, sample_rate, audio_data)
    audio_buffer.seek(0)
    
    return audio_buffer, frequency

def generate_chladni_pattern(ndvi_value):
    """
    Generates a Chladni vibrational pattern (visual geometry of resonance).
    This provides an accessible visualization of the data for deaf users.
    The geometry's complexity shifts dynamically based on the NDVI health.
    """
    # Map NDVI to Chladni resonance nodes (m, n)
    # Healthy vegetation gets complex, harmonious geometry. Stress gets simpler/broken geometry.
    if ndvi_value >= 0.30:
        m, n = 5, 2
    else:
        m, n = 2, 1

    # Create a 2D grid
    x = np.linspace(-1, 1, 400)
    y = np.linspace(-1, 1, 400)
    X, Y = np.meshgrid(x, y)

    # Chladni 2D wave equation
    Z = np.cos(n * np.pi * X) * np.cos(m * np.pi * Y) - np.cos(m * np.pi * X) * np.cos(n * np.pi * Y)

    # Plotting the figure to pass

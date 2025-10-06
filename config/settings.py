"""Configuration settings for the AERONET Explorer app."""

# AERONET API settings
AERONET_BASE_URL = "https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3"
AERONET_SITES_URL = "https://aeronet.gsfc.nasa.gov/aeronet_locations_v3.txt"

# Data quality levels
DATA_LEVELS = {
    "1.0": "Level 1.0 (Unscreened)",
    "1.5": "Level 1.5 (Cloud-screened)", 
    "2.0": "Level 2.0 (Quality-assured)"
}

# Data averaging options
AVG_TYPES = {
    "10": "All Points",
    "20": "Daily Averages"
}

# AOD wavelengths (nanometers)
AOD_WAVELENGTHS = [340, 380, 440, 500, 675, 870, 1020]

# Default plot settings
DEFAULT_PLOT_CONFIG = {
    "theme": "plotly_white",
    "height": 500,
    "showlegend": True
}

# Rate limiting settings
REQUEST_DELAY = 1.0  # seconds between requests
MAX_REQUESTS_PER_MINUTE = 8

# Cache settings
CACHE_EXPIRY_HOURS = 24
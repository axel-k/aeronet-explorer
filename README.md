A Streamlit web application for downloading and visualizing AERONET (Aerosol Robotic Network) aerosol optical depth data.

## Features

- Interactive site selection with map visualization
- Flexible date range selection
- Multiple data quality levels (1.0, 1.5, 2.0)
- Wavelength-specific AOD plotting
- Data export functionality
- Responsive design

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd aeronet-explorer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

## Project Structure

- `app.py`: Main Streamlit application
- `src/`: Core application modules
- `data/`: Data files and cached downloads
- `config/`: Configuration settings
- `tests/`: Unit tests

## Data Sources

This application uses data from NASA's AERONET program:
- Website: https://aeronet.gsfc.nasa.gov/
- API Documentation: https://aeronet.gsfc.nasa.gov/print_web_data_help_v3.html
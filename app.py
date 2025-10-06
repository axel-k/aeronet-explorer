"""
AERONET Data Explorer - Streamlit Application

A web application for downloading and visualizing AERONET aerosol optical depth data.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import plotly.graph_objects as go
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from aeronet_api import AeronetAPI
from data_processor import AeronetDataProcessor
from plotting import AeronetPlotter
from config.settings import DATA_LEVELS, AVG_TYPES, AOD_WAVELENGTHS

# Page configuration
st.set_page_config(
    page_title="AERONET Data Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stSelectbox > label {
        font-weight: bold;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_clients():
    """Initialize API clients and data processor."""
    api = AeronetAPI()
    processor = AeronetDataProcessor()
    plotter = AeronetPlotter()
    return api, processor, plotter

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🌍 AERONET Data Explorer</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>Welcome to the AERONET Data Explorer!</b><br>
    Download and visualize aerosol optical depth (AOD) data from NASA's Aerosol Robotic Network (AERONET).
    Select a site, date range, and data parameters to get started.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize clients
    api, processor, plotter = initialize_clients()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("📊 Data Selection")
        
        # Load sites data
        with st.spinner("Loading AERONET sites..."):
            sites_df = api.get_sites_list()
        
        if sites_df.empty:
            st.error("Failed to load AERONET sites. Please check your internet connection.")
            return
        
        # Site selection
        site_names = sorted(sites_df['Site_Name'].unique())
        selected_site = st.selectbox(
            "🌐 Select AERONET Site",
            options=site_names,
            index=site_names.index("GSFC") if "GSFC" in site_names else 0,
            help="Choose an AERONET measurement site"
        )
        
        # Date range selection
        st.subheader("📅 Date Range")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                min_value=date(1993, 1, 1),
                max_value=date.today()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
                min_value=date(1993, 1, 1),
                max_value=date.today()
            )
        
        # Validation
        if start_date > end_date:
            st.error("Start date must be before end date!")
            return
        
        # Data parameters
        st.subheader("⚙️ Data Parameters")
        
        data_level = st.selectbox(
            "Data Quality Level",
            options=list(DATA_LEVELS.keys()),
            format_func=lambda x: DATA_LEVELS[x],
            index=1,  # Default to Level 1.5
            help="Level 1.5 (cloud-screened) is recommended for most users"
        )
        
        avg_type = st.selectbox(
            "Averaging Type",
            options=list(AVG_TYPES.keys()),
            format_func=lambda x: AVG_TYPES[x],
            help="All points shows individual measurements, daily averages shows daily means"
        )
        
        # Wavelength selection
        st.subheader("🌈 Wavelengths")
        selected_wavelengths = st.multiselect(
            "Select wavelengths (nm)",
            options=AOD_WAVELENGTHS,
            default=[440, 500, 675],
            help="Choose which AOD wavelengths to display"
        )
        
        if not selected_wavelengths:
            st.warning("Please select at least one wavelength.")
            return
        
        # Download button
        download_data = st.button(
            "📥 Download Data",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if not download_data and 'aod_data' not in st.session_state:
        # Show site information and map
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ AERONET Sites Map")
            map_fig = plotter.plot_site_map(sites_df, selected_site)
            st.plotly_chart(map_fig, use_container_width=True)
        
        with col2:
            if selected_site:
                site_info = sites_df[sites_df['Site_Name'] == selected_site].iloc[0]
                st.subheader("📍 Site Information")
                
                st.markdown(f"""
                **Site Name:** {site_info['Site_Name']}  
                **Latitude:** {site_info['Latitude']:.3f}°  
                **Longitude:** {site_info['Longitude']:.3f}°  
                **Elevation:** {site_info['Elevation']:.1f} m  
                """)
        
        # Instructions
        st.markdown("""
        ### 📖 How to Use
        1. **Select a site** from the dropdown in the sidebar
        2. **Choose your date range** (up to several months recommended)
        3. **Configure data parameters** (quality level, averaging type)
        4. **Select wavelengths** you want to analyze
        5. **Click "Download Data"** to retrieve and visualize the data
        
        ### 📊 Data Quality Levels
        - **Level 1.0**: Raw, unscreened data
        - **Level 1.5**: Cloud-screened and quality-controlled (recommended)
        - **Level 2.0**: Quality-assured data (highest quality, fewer points)
        """)
    
    # Download and display data
    if download_data or 'aod_data' in st.session_state:
        
        if download_data:
            # Download new data
            with st.spinner(f"Downloading data for {selected_site}..."):
                try:
                    raw_data = api.get_aod_data(
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        site=selected_site,
                        data_level=data_level,
                        avg_type=avg_type
                    )
                    
                    if raw_data.empty:
                        st.error(f"No data available for {selected_site} in the selected date range.")
                        return
                    
                    # Process data
                    clean_data = processor.clean_data(raw_data)
                    
                    # Store in session state
                    st.session_state['aod_data'] = clean_data
                    st.session_state['download_params'] = {
                        'site': selected_site,
                        'start_date': start_date,
                        'end_date': end_date,
                        'data_level': data_level,
                        'avg_type': avg_type,
                        'wavelengths': selected_wavelengths
                    }
                    
                    st.success(f"Successfully downloaded {len(clean_data)} data points!")
                    
                except Exception as e:
                    st.error(f"Error downloading data: {str(e)}")
                    return
        
        # Use cached data
        aod_data = st.session_state['aod_data']
        params = st.session_state.get('download_params', {})
        
        if aod_data.empty:
            st.warning("No data to display.")
            return
        
        # Extract AOD columns
        aod_columns = processor.extract_aod_columns(aod_data)
        
        # Display data summary
        st.subheader("📊 Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(aod_data))
        with col2:
            st.metric("Site", params.get('site', 'Unknown'))
        with col3:
            st.metric("Data Level", DATA_LEVELS.get(params.get('data_level', '15')))
        with col4:
            date_range = f"{params.get('start_date', 'N/A')} to {params.get('end_date', 'N/A')}"
            st.metric("Date Range", date_range)
        
        # Main visualization
        st.subheader("📈 AOD Time Series")
        
        # Create time series plot
        plot_title = f"Aerosol Optical Depth - {params.get('site', 'Unknown Site')}"
        timeseries_fig = plotter.plot_aod_timeseries(
            aod_data, aod_columns, selected_wavelengths, plot_title
        )
        st.plotly_chart(timeseries_fig, use_container_width=True)
        
        # Statistics section
        if len(selected_wavelengths) > 1:
            st.subheader("📊 Statistical Summary")
            
            # Calculate statistics for each wavelength
            stats_dict = {}
            for wavelength in selected_wavelengths:
                stats_dict[wavelength] = processor.calculate_statistics(aod_data, wavelength)
            
            # Display statistics table
            stats_rows = []
            for wavelength in selected_wavelengths:
                if wavelength in stats_dict and stats_dict[wavelength]:
                    stats = stats_dict[wavelength]
                    stats_rows.append({
                        'Wavelength (nm)': wavelength,
                        'Count': stats['count'],
                        'Mean': f"{stats['mean']:.3f}",
                        'Median': f"{stats['median']:.3f}",
                        'Std Dev': f"{stats['std']:.3f}",
                        'Min': f"{stats['min']:.3f}",
                        'Max': f"{stats['max']:.3f}"
                    })
            
            if stats_rows:
                stats_df = pd.DataFrame(stats_rows)
                st.dataframe(stats_df, use_container_width=True)
                
                # Box plot for statistics
                if len(selected_wavelengths) > 1:
                    stats_fig = plotter.plot_aod_statistics(stats_dict, selected_wavelengths)
                    st.plotly_chart(stats_fig, use_container_width=True)
        
        # Data table section
        with st.expander("🔍 View Raw Data", expanded=False):
            st.subheader("Raw Data Table")
            
            # Show relevant columns
            display_cols = ['datetime'] if 'datetime' in aod_data.columns else []
            display_cols.extend([aod_columns[w] for w in selected_wavelengths if w in aod_columns])
            
            if display_cols:
                display_data = aod_data[display_cols].copy()
                
                # Format datetime for display
                if 'datetime' in display_data.columns:
                    display_data['datetime'] = display_data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(display_data, use_container_width=True)
                
                # Download button for CSV
                csv_data = display_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv_data,
                    file_name=f"aeronet_{params.get('site', 'data')}_{params.get('start_date', '')}_to_{params.get('end_date', '')}.csv",
                    mime="text/csv"
                )
        
        # Analysis section
        with st.expander("🔬 Data Analysis", expanded=False):
            st.subheader("Data Quality Assessment")
            
            # Data completeness
            total_possible = len(aod_data)
            completeness_data = []
            
            for wavelength in selected_wavelengths:
                if wavelength in aod_columns:
                    col_name = aod_columns[wavelength]
                    valid_count = aod_data[col_name].notna().sum()
                    completeness = (valid_count / total_possible) * 100 if total_possible > 0 else 0
                    completeness_data.append({
                        'Wavelength (nm)': wavelength,
                        'Valid Measurements': valid_count,
                        'Total Possible': total_possible,
                        'Completeness (%)': f"{completeness:.1f}%"
                    })
            
            if completeness_data:
                completeness_df = pd.DataFrame(completeness_data)
                st.dataframe(completeness_df, use_container_width=True)
            
            # Temporal coverage
            if 'datetime' in aod_data.columns:
                st.subheader("Temporal Coverage")
                first_measurement = aod_data['datetime'].min()
                last_measurement = aod_data['datetime'].max()
                total_days = (last_measurement - first_measurement).days + 1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("First Measurement", first_measurement.strftime('%Y-%m-%d %H:%M'))
                with col2:
                    st.metric("Last Measurement", last_measurement.strftime('%Y-%m-%d %H:%M'))
                with col3:
                    st.metric("Time Span (days)", total_days)

if __name__ == "__main__":
    main()
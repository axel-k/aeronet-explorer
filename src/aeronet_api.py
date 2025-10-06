"""AERONET API client for downloading aerosol data."""

import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import time
import streamlit as st
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AeronetAPI:
    """Client for AERONET web service API."""
    
    def __init__(self, base_url: str = "https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AERONET-Explorer/1.0 (Streamlit App)'
        })
        self.last_request_time = 0
        
    def _respect_rate_limit(self, delay: float = 1.0):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request_time = time.time()
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_sites_list(_self) -> pd.DataFrame:
        """Download and parse AERONET sites list."""
        sites_url = "https://aeronet.gsfc.nasa.gov/aeronet_locations_v3.txt"
        
        try:
            response = requests.get(sites_url)
            response.raise_for_status()
            
            # Parse the sites file
            lines = response.text.strip().split('\n')
            sites_data = []
            
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 4:
                        sites_data.append({
                            'Site_Name': parts[0].strip(),
                            'Longitude': float(parts[1].strip()),
                            'Latitude': float(parts[2].strip()),
                            'Elevation': float(parts[3].strip()) if parts[3].strip() else 0.0
                        })
            
            return pd.DataFrame(sites_data)
            
        except Exception as e:
            logger.error(f"Error fetching sites list: {e}")
            # Return empty DataFrame if fetch fails
            return pd.DataFrame(columns=['Site_Name', 'Longitude', 'Latitude', 'Elevation'])
    
    def get_aod_data(self, start_date: str, end_date: str, site: str, 
                     data_level: str = "15", avg_type: str = "10") -> pd.DataFrame:
        """
        Download AERONET AOD data.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            site: AERONET site name
            data_level: Data quality level ('10', '15', '20')
            avg_type: Averaging type ('10'=all points, '20'=daily averages)
            
        Returns:
            DataFrame with AERONET data
        """
        self._respect_rate_limit()
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        params = {
            'site': site,
            'year': start_dt.year,
            'month': start_dt.month,
            'day': start_dt.day,
            'year2': end_dt.year,
            'month2': end_dt.month,
            'day2': end_dt.day,
            f'AOD{data_level}': 1,
            'AVG': avg_type,
            'if_no_html': 1
        }
        
        try:
            logger.info(f"Requesting data for {site} from {start_date} to {end_date}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            if not response.text.strip():
                return pd.DataFrame()
            
            # Parse CSV data
            lines = response.text.strip().split('\n')
            
            # Find the data start (skip metadata)
            data_start = 0
            for i, line in enumerate(lines):
                if line.startswith('Date(dd:mm:yyyy)') or line.startswith('Date_'):
                    data_start = i
                    break
            
            if data_start == 0:
                # No proper header found, assume data starts after first few lines
                data_start = min(6, len(lines) - 1)
            
            # Read the data
            data_text = '\n'.join(lines[data_start:])
            df = pd.read_csv(StringIO(data_text))
            
            # Clean up the dataframe
            if not df.empty:
                # Convert date columns to datetime
                if 'Date(dd:mm:yyyy)' in df.columns:
                    df['datetime'] = pd.to_datetime(df['Date(dd:mm:yyyy)'] + ' ' + df['Time(hh:mm:ss)'], 
                                                  format='%d:%m:%Y %H:%M:%S')
                elif any('Date_' in col for col in df.columns):
                    date_col = [col for col in df.columns if 'Date_' in col][0]
                    time_col = [col for col in df.columns if 'Time_' in col][0] if any('Time_' in col for col in df.columns) else None
                    if time_col:
                        df['datetime'] = pd.to_datetime(df[date_col] + ' ' + df[time_col])
                    else:
                        df['datetime'] = pd.to_datetime(df[date_col])
                
                # Sort by datetime
                if 'datetime' in df.columns:
                    df = df.sort_values('datetime')
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Failed to fetch data: {e}")
        except Exception as e:
            logger.error(f"Data parsing error: {e}")
            raise Exception(f"Failed to parse data: {e}")
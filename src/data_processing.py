"""Data processing utilities for AERONET data."""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import re

class AeronetDataProcessor:
    """Process and clean AERONET data."""
    
    def __init__(self):
        self.aod_wavelengths = [340, 380, 440, 500, 675, 870, 1020]
    
    def extract_aod_columns(self, df: pd.DataFrame) -> Dict[int, str]:
        """Extract AOD columns and map wavelengths to column names."""
        aod_columns = {}
        
        for col in df.columns:
            for wavelength in self.aod_wavelengths:
                # Look for columns like AOD_440nm, AOD500, etc.
                if str(wavelength) in col and 'AOD' in col.upper():
                    aod_columns[wavelength] = col
                    break
        
        return aod_columns
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate AERONET data."""
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Replace invalid values with NaN
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].replace([-999, -999.0, 'N/A'], np.nan)
        
        # Remove rows where all AOD values are NaN
        aod_cols = self.extract_aod_columns(df_clean)
        if aod_cols:
            aod_col_names = list(aod_cols.values())
            df_clean = df_clean.dropna(subset=aod_col_names, how='all')
        
        return df_clean
    
    def calculate_statistics(self, df: pd.DataFrame, wavelength: int) -> Dict:
        """Calculate basic statistics for AOD data at specific wavelength."""
        aod_cols = self.extract_aod_columns(df)
        
        if wavelength not in aod_cols:
            return {}
        
        col_name = aod_cols[wavelength]
        data = df[col_name].dropna()
        
        if data.empty:
            return {}
        
        return {
            'count': len(data),
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'q25': data.quantile(0.25),
            'q75': data.quantile(0.75)
        }
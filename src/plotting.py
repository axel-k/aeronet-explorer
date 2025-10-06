"""Plotting utilities for AERONET data visualization."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class AeronetPlotter:
    """Create plots for AERONET data."""
    
    def __init__(self):
        self.default_colors = px.colors.qualitative.Set1
        
    def plot_aod_timeseries(self, df: pd.DataFrame, aod_columns: Dict[int, str], 
                           selected_wavelengths: List[int], title: str = "") -> go.Figure:
        """Create time series plot of AOD data."""
        fig = go.Figure()
        
        if df.empty or not aod_columns:
            fig.add_annotation(
                text="No data available for the selected parameters",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Add traces for selected wavelengths
        for i, wavelength in enumerate(selected_wavelengths):
            if wavelength in aod_columns:
                col_name = aod_columns[wavelength]
                data = df[['datetime', col_name]].dropna()
                
                if not data.empty:
                    fig.add_trace(go.Scatter(
                        x=data['datetime'],
                        y=data[col_name],
                        mode='markers+lines',
                        name=f'AOD {wavelength}nm',
                        line=dict(color=self.default_colors[i % len(self.default_colors)]),
                        marker=dict(size=4),
                        hovertemplate=f'<b>AOD {wavelength}nm</b><br>' +
                                    'Date: %{x}<br>' +
                                    'AOD: %{y:.3f}<extra></extra>'
                    ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Aerosol Optical Depth",
            hovermode='x unified',
            height=500,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    def plot_aod_statistics(self, stats_dict: Dict, wavelengths: List[int]) -> go.Figure:
        """Create box plot showing AOD statistics."""
        fig = go.Figure()
        
        for wavelength in wavelengths:
            if wavelength in stats_dict and stats_dict[wavelength]:
                stats = stats_dict[wavelength]
                
                fig.add_trace(go.Box(
                    q1=[stats['q25']],
                    median=[stats['median']],
                    q3=[stats['q75']],
                    lowerfence=[stats['min']],
                    upperfence=[stats['max']],
                    mean=[stats['mean']],
                    name=f'{wavelength}nm',
                    boxpoints='outliers'
                ))
        
        fig.update_layout(
            title="AOD Statistics by Wavelength",
            xaxis_title="Wavelength (nm)",
            yaxis_title="Aerosol Optical Depth",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def plot_site_map(self, sites_df: pd.DataFrame, selected_site: Optional[str] = None) -> go.Figure:
        """Create map showing AERONET sites."""
        fig = go.Figure()
        
        # Add all sites
        fig.add_trace(go.Scattermapbox(
            lat=sites_df['Latitude'],
            lon=sites_df['Longitude'],
            mode='markers',
            marker=dict(size=8, color='lightblue'),
            text=sites_df['Site_Name'],
            name='AERONET Sites',
            hovertemplate='<b>%{text}</b><br>' +
                         'Lat: %{lat:.2f}<br>' +
                         'Lon: %{lon:.2f}<extra></extra>'
        ))
        
        # Highlight selected site
        if selected_site and selected_site in sites_df['Site_Name'].values:
            site_data = sites_df[sites_df['Site_Name'] == selected_site].iloc[0]
            fig.add_trace(go.Scattermapbox(
                lat=[site_data['Latitude']],
                lon=[site_data['Longitude']],
                mode='markers',
                marker=dict(size=12, color='red'),
                text=[selected_site],
                name='Selected Site',
                hovertemplate=f'<b>{selected_site}</b><br>' +
                             f'Lat: {site_data["Latitude"]:.2f}<br>' +
                             f'Lon: {site_data["Longitude"]:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=30, lon=0),
                zoom=1
            ),
            height=400,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        return fig
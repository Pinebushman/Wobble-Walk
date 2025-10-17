import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Title and instructions
st.set_page_config(page_title="BC Liquor License Map", layout="wide")
st.title("📍 BC Liquor License Map")
st.markdown("Tap a marker to view license info. This version uses open-source geocoding (Nominatim).")

# Load the Excel file (your file name is used here)
@st.cache_data
def load_data():
    return pd.read_excel("Copy of licenses.xlsx")

df = load_data()

# Build full address column if missing
if 'full_address' not in df.columns:
    df['full_address'] = df['Establishment Address Street'].astype(str) + ", " + \
                         df['Establishment Address City'].astype(str) + ", BC, Canada"

# Ensure Latitude and Longitude columns exist
if 'Latitude' not in df.columns:
    df['Latitude'] = None
if 'Longitude' not in df.columns:
    df['Longitude'] = None

# Only geocode rows missing Lat/Lon
missing_mask = df['Latitude'].isna() | df['Longitude'].isna()

if missing_mask.any():
    st.warning("⏳ Geocoding missing addresses... This may take time.")

    geolocator = Nominatim(user_agent="bc-liquor-map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    for idx in df[missing_mask].index:
        address = df.at[idx, 'full_address']
        try:
            location = geocode(address)
            if location:
                df.at[idx, 'Latitude'] = location.latitude
                df.at[idx, 'Longitude'] = location.longitude
        except:
            df.at[idx, 'Latitude'] = None
            df.at[idx, 'Longitude'] = None

        # Save progress after each lookup
        df.to_excel("licenses_progress.xlsx", index=False)

    st.success("✅ Geocoding complete! Progress saved as licenses_progress.xlsx")

# Drop rows still missing coordinates
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Create interactive map
m = folium.Map(location=[53.7267, -127.6476], zoom_start=5)

for _, row in df.iterrows():
    popup = f"""
    <b>{row['Establishment']}</b><br>
    License #: {row['Licence Number']}<br>
    Type: {row['Licence Type']}<br>
    Address: {row['Establishment Address Street']}, {row['Establishment Address City']}<br>
    Expiry: {row['Expiry Date']}<br>
    Licensee: {row['Licensee']}
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Display the map
st_folium(m, width=1000, height=600)

# Show raw data if desired
with st.expander("📋 Show raw license data"):
    st.dataframe(df)

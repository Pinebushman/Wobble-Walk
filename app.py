import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

st.set_page_config(page_title="BC Liquor License Map Agent", layout="wide")

st.title("📍 BC Liquor License Map Agent")
st.markdown("Allow GPS to show nearby licensed establishments. Tap markers for full details.")

# Load the Excel file and clean it
@st.cache_data
def load_data():
    xls = pd.read_excel("licenses.xlsx", sheet_name=None)  # Load all sheets
    sheet_names = list(xls.keys())

    # Try to find sheet with name containing 'licence'
    for name in sheet_names:
        if 'licence' in name.lower():
            df = xls[name]
            break
    else:
        st.error("No sheet with 'Licence' found.")
        return pd.DataFrame()

    df.columns = df.columns.str.strip()  # Clean up column names
    required_cols = ["Latitude", "Longitude", "Establishment Name", "Licence Number", "City", "Status"]
    if not all(col in df.columns for col in required_cols):
        st.error("Required columns missing.")
        return pd.DataFrame()

    df = df.dropna(subset=["Latitude", "Longitude"])
    return df

# Calculate distance (in km) using haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# Load data
df = load_data()
if df.empty:
    st.stop()

# Ask user for location
st.markdown("## 📡 Your Location (Required for distance filtering)")
lat = st.number_input("Latitude", value=49.2827, format="%.6f")
lon = st.number_input("Longitude", value=-123.1207, format="%.6f")
radius_km = st.slider("Search radius (km)", 0, 20, 5)

# Filter by radius
df["Distance (km)"] = df.apply(lambda row: haversine(lat, lon, row["Latitude"], row["Longitude"]), axis=1)
nearby = df[df["Distance (km)"] <= radius_km]

st.success(f"Showing {len(nearby)} locations within {radius_km} km")

# Display table
with st.expander("📋 Show table of nearby licenses"):
    st.dataframe(nearby[[
        "Establishment Name", "City", "Licence Number", "Status", "Distance (km)"
    ]].sort_values("Distance (km)"))

# Map
m = folium.Map(location=[lat, lon], zoom_start=14)

# Add your location
folium.Marker(
    location=[lat, lon],
    tooltip="You are here",
    icon=folium.Icon(color='blue')
).add_to(m)

# Add markers for establishments
for _, row in nearby.iterrows():
    popup = f"""
    <b>{row['Establishment Name']}</b><br>
    License #: {row['Licence Number']}<br>
    City: {row['City']}<br>
    Status: {row['Status']}<br>
    Distance: {row['Distance (km)']:.2f} km
    """
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=popup,
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# Show map
st_data = st_folium(m, width=700, height=500)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, sqrt, atan2

# App title
st.set_page_config(page_title="BC Liquor License Map", layout="wide")
st.title("📍 BC Liquor License Map Agent")
st.caption("Allow GPS to show nearby licensed establishments. Tap markers for full details.")

# Load the Excel data
@st.cache_data
def load_data():
    return pd.read_excel("licenses.xlsx", sheet_name="Liquor Web Stats Active Lic...")

df = load_data()

# Clean up columns
df.columns = df.columns.str.strip()
df = df.rename(columns={
    'Licence Number': 'License Number',
    'Establishment Name': 'Name',
    'Site Address': 'Address',
    'City': 'City',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Licence Type': 'Type'
})

# Remove rows without location data
df = df.dropna(subset=['Latitude', 'Longitude'])

# Get user location
user_lat = st.number_input("📡 Enter your latitude:", format="%.6f", value=49.2827)
user_lon = st.number_input("📡 Enter your longitude:", format="%.6f", value=-123.1207)

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# Filter to nearby licenses (within 5 km)
df["Distance (km)"] = df.apply(
    lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]), axis=1
)
nearby = df[df["Distance (km)"] <= 5].sort_values("Distance (km)")

# Show count
st.success(f"Found {len(nearby)} licensed establishments within 5 km.")

# Create map
m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
folium.Marker([user_lat, user_lon], tooltip="Your Location", icon=folium.Icon(color='blue')).add_to(m)

# Add markers for each establishment
for _, row in nearby.iterrows():
    popup_text = f"""
    <b>{row['Name']}</b><br>
    {row['Address']}, {row['City']}<br>
    License #: {row['License Number']}<br>
    Type: {row['Type']}<br>
    Distance: {row['Distance (km)']:.2f} km
    """
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        tooltip=row['Name'],
        popup=popup_text,
        icon=folium.Icon(color='green' if row['Type'] == 'Liquor Primary' else 'red')
    ).add_to(m)

# Display the map
st_data = st_folium(m, width=900, height=600)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# --- Title and Instructions ---
st.set_page_config(page_title="BC Liquor License Map", layout="wide")
st.title("📍 BC Liquor License Map Agent")
st.markdown("This map displays active liquor licenses in BC. Tap a marker for license details.")

# --- Load Excel ---
@st.cache_data
def load_data():
    return pd.read_excel("licenses.xlsx", sheet_name="Liquor Web Stats Active Lic...")

df = load_data()

# --- Load Google API key securely ---
GOOGLE_API_KEY = 
st.secrets["google_maps_api_key"]

# --- Google Geocoding Function ---
def google_geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return pd.Series([location["lat"], location["lng"]])
    else:
        return pd.Series([None, None])

# --- Geocode if missing ---
if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
    st.warning("Geocoding addresses with Google Maps API. This may take a few minutes.")
    full_addresses = df['Establishment Address Street'].astype(str) + ", " + \
                     df['Establishment Address City'].astype(str) + ", BC, Canada"
    coords = full_addresses.apply(google_geocode)
    df['Latitude'] = coords[0]
    df['Longitude'] = coords[1]
    # Optional: Save for next time
    df.to_csv("licenses_geocoded.csv", index=False)

# --- Drop rows with missing coordinates ---
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# --- Create Folium map ---
m = folium.Map(location=[53.7267, -127.6476], zoom_start=5)

for _, row in df.iterrows():
    popup = f"""
    <b>{row['Establishment']}</b><br>
    License #: {row['Licence Number']}<br>
    Type: {row['Licence Type']}<br>
    Address: {row['Establishment Address Street']}, {row['Establishment Address City']}<br>
    Expiry: {row['Expiry Date']}<br>
    Licensee: {row['Licensee']}<br>
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# --- Show Map ---
st_folium(m, width=1000, height=600)

# --- Show Data Table ---
with st.expander("📋 Show raw data table"):
    st.dataframe(df)

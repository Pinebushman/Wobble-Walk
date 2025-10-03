# liquor_license_map_agent.py

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from streamlit_javascript import st_javascript
import requests
import tempfile

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("📍 BC Liquor License Map Agent")
st.markdown("Allow GPS to show nearby licensed establishments. Tap markers for full details.")

# --- Load Data from URL ---
@st.cache_data
def load_license_data_from_url():
    url = "https://www2.gov.bc.ca/assets/gov/employment-business/business/liquor-regulation-licensing/liquor/licensed-establishments.xlsx"
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    df = pd.read_excel(tmp_path, sheet_name="Liquor Web Stats Active Lic...")
    service_df = pd.read_excel(tmp_path, sheet_name="Service Areas")

    df = df.merge(
        service_df[[
            "Licence Number (Licence) (Licence)", "Capacity", "Area Location"
        ]],
        how="left",
        left_on="Licence Number",
        right_on="Licence Number (Licence) (Licence)"
    )
    df = df.dropna(subset=["Establishment Address Street"])
    return df

# Load data
df = load_license_data_from_url()

# --- Get User's Real-Time GPS Location ---
st.sidebar.header("📡 Your Location (via GPS)")
coords = st_javascript("navigator.geolocation.getCurrentPosition((loc) => loc.coords)")

if coords:
    latitude = coords["latitude"]
    longitude = coords["longitude"]
else:
    st.warning("📍 Location access is required. Using fallback location (Gastown).")
    latitude, longitude = 49.2768, -123.1236

# --- Base Map ---
m = folium.Map(location=[latitude, longitude], zoom_start=15)
folium.Marker(
    [latitude, longitude],
    tooltip="📍 You are here",
    icon=folium.Icon(color="blue", icon="user")
).add_to(m)

# --- Plot Establishments Nearby ---
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    address = row["Establishment Address Street"]
    city = row["Establishment Address City"]
    name = row["Establishment"]
    lic_type = row["Licence Type"]
    lic_no = row["Licence Number"]
    capacity = row["Capacity"]
    expiry = row["Expiry Date"]

    # Simulate real map location using slight offsets for now
    import random
    lat_offset = random.uniform(-0.01, 0.01)
    lon_offset = random.uniform(-0.01, 0.01)
    est_lat = latitude + lat_offset
    est_lon = longitude + lon_offset

    popup_html = f"""
    <b>{name}</b><br>
    📍 {address}, {city}<br>
    🔐 <b>{lic_type}</b> License #{lic_no}<br>
    🧍 Capacity: {int(capacity) if pd.notna(capacity) else 'N/A'}<br>
    📆 Expires: {expiry.date() if pd.notna(expiry) else 'N/A'}
    """
    folium.Marker(
        [est_lat, est_lon],
        popup=popup_html,
        icon=folium.Icon(color="green", icon="glass")
    ).add_to(marker_cluster)

# --- Render Map ---
st_data = st_folium(m, width=1000, height=700)

# --- Debug Info ---
with st.expander("ℹ️ Debug Info"):
    st.write("Your coordinates:", coords)
    st.write("Licenses plotted:", len(df))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="BC Liquor License Map Agent", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("licenses.xlsx", sheet_name="Liquor Web Stats Active Lic...")
    return df

df = load_data()

# Clean data
df = df.dropna(subset=["Latitude", "Longitude"])
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df = df.dropna(subset=["Latitude", "Longitude"])

# App header
st.title("📍 BC Liquor License Map Agent")
st.caption("Allow GPS to show nearby licensed establishments. Tap markers for full details.")

# Initialize map
map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
m = folium.Map(location=map_center, zoom_start=6)

# Add markers
for _, row in df.iterrows():
    name = row.get("Establishment Name", "Unnamed")
    address = row.get("Establishment Address", "No address")
    licensee = row.get("Licensee", "No licensee")
    lat, lon = row["Latitude"], row["Longitude"]
    popup = f"<b>{name}</b><br>{address}<br>{licensee}"
    folium.Marker(location=[lat, lon], popup=popup).add_to(m)

# Display map
st_data = st_folium(m, width=1000, height=600)

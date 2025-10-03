import streamlit as st import pandas as pd import folium from streamlit_folium import st_folium from geopy.geocoders import Nominatim from geopy.extra.rate_limiter import RateLimiter

Load the Excel file and correct sheet

def load_data(): df = pd.read_excel("licenses.xlsx", sheet_name="Liquor Web Stats Active Lic...") df = df.dropna(subset=["Latitude", "Longitude"]) return df

Set up the page

st.set_page_config(page_title="BC Liquor License Map Agent", layout="wide") st.title("📍 BC Liquor License Map Agent") st.caption("Allow GPS to show nearby licensed establishments. Tap markers for full details.")

Load data

df = load_data()

Set default map center (e.g., Vancouver)

DEFAULT_LAT = 49.2827 DEFAULT_LON = -123.1207

Create folium map

m = folium.Map(location=[DEFAULT_LAT, DEFAULT_LON], zoom_start=12)

Add markers

for _, row in df.iterrows(): folium.Marker( location=[row["Latitude"], row["Longitude"]], popup=f""" <strong>{row['Establishment Name']}</strong><br> License: {row['Licence Number']}<br> Type: {row['Licence Type']}<br> Capacity: {row.get('Person Capacity', 'Unknown')}<br> Hours: {row.get('Hours of Sale', 'Unknown')}<br> Address: {row['Site Address']}<br> City: {row['City']} """, tooltip=row['Establishment Name'] ).add_to(m)

Display map

st_folium(m, width=800, height=600)

Optional: view data table

with st.expander("Show full license data"): st.dataframe(df)


import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
Title

st.title("📍 BC Liquor License Map Agent") 
st.markdown("Allow GPS to show nearby licensed establishments. Tap markers for full details.")

# Load data from uploaded Excel file

@st.cache_data
def load_data():
    df = pd.read_excel("licenses.xlsx", sheet_name="Liquor Web Stats Active Lic...")
    return df

df = load_data()

# Check for previously geocoded coordinates

if 'Latitude' not in df.columns or 'Longitude' not in df.columns: st.warning("Geocoding addresses. This may take a few moments.")

geolocator = Nominatim(user_agent="liquor-map")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_coords(address):
    try:
        location = geocode(address)
        return pd.Series([location.latitude, location.longitude]) if location else pd.Series([None, None])
    except:
        return pd.Series([None, None])

full_addresses = df['Establishment Address Street'].astype(str) + ", " + \
                 df['Establishment Address City'].astype(str) + ", BC, Canada"

coords = full_addresses.apply(get_coords)
df['Latitude'] = coords[0]
df['Longitude'] = coords[1]

# Drop missing coordinate rows

df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

Show map centered on BC

m = folium.Map(location=[53.7267, -127.6476], zoom_start=5)

for _, row in df.iterrows(): popup = f""" <b>{row['Establishment']}</b><br> License #: {row['Licence Number']}<br> Type: {row['Licence Type']}<br> Address: {row['Establishment Address Street']}, {row['Establishment Address City']}<br> Expiry: {row['Expiry Date']}<br> Licensee: {row['Licensee']}<br> """ folium.Marker( location=[row['Latitude'], row['Longitude']], popup=popup, icon=folium.Icon(color="blue", icon="info-sign") ).add_to(m)

st_folium(m, width=700, height=500)

Optional: display data table

with st.expander("Show raw data"): st.dataframe(df)


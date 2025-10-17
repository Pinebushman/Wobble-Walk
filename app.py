import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load your file
df = pd.read_excel("licenses_subset.xlsx")

# Create full address if not already present
if 'full_address' not in df.columns:
    df['full_address'] = df['Establishment Address Street'].astype(str) + ", " + \
                         df['Establishment Address City'].astype(str) + ", BC, Canada"

# Set up geocoder with delay
geolocator = Nominatim(user_agent="liquor-map")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Only geocode missing rows
missing_mask = df['Latitude'].isna() | df['Longitude'].isna()

for idx in df[missing_mask].index:
    address = df.at[idx, 'full_address']
    try:
        location = geocode(address)
        if location:
            df.at[idx, 'Latitude'] = location.latitude
            df.at[idx, 'Longitude'] = location.longitude
        else:
            df.at[idx, 'Latitude'] = None
            df.at[idx, 'Longitude'] = None
    except:
        df.at[idx, 'Latitude'] = None
        df.at[idx, 'Longitude'] = None

    # Save progress after each address (or batch if faster)
    df.to_excel("licenses_subset_progress.xlsx", index=False)

print("✅ Geocoding complete. File saved as licenses_subset_progress.xlsx")

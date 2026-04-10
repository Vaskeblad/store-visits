import googlemaps
import pandas as pd
from tqdm import tqdm
tqdm.pandas()
import gspread
from google.oauth2.service_account import Credentials
import gspread
from gspread_dataframe import set_with_dataframe

sheet_key = "1SL7mYtrgMmUdtvt6eykg4OOuefRtpRrUurvwfu_Jdck"
api_key = AIzaSyBZnop8B8WL81k8ctL6YrHmsYH11cdvhgg

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

#Read data
creds = Credentials.from_service_account_file("../credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key(sheet_key).worksheet("customers")

data = sheet.get_all_records()
df = pd.DataFrame(data)

#Add geo information
gmaps = googlemaps.Client(key=api_key)

def get_location_info(store_name):
    result = gmaps.geocode(store_name + ", Sweden")
    if not result:
        return None, None, None, None, None, None
    
    r = result[0]
    lat = r["geometry"]["location"]["lat"]
    lng = r["geometry"]["location"]["lng"]

    components = r["address_components"]
    street = next((c["long_name"] for c in components if "route" in c["types"]), None)
    number = next((c["long_name"] for c in components if "street_number" in c["types"]), None)
    postal = next((c["long_name"] for c in components if "postal_code" in c["types"]), None)
    city = next((c["long_name"] for c in components if "postal_town" in c["types"]), None)
    
    return city, street, number, postal, lat, lng

df[["city_google", "address_google", "address_number_google", "postal_code_google", "latitude_google", "longitude_google"]] = df["customer"].progress_apply(lambda x: pd.Series(get_location_info(x)))

#save data to new worksheet
try:
    worksheet = sheet.add_worksheet(title="customer_enriched", rows=1000, cols=20)
except:
    worksheet = sheet.worksheet("customer_enriched") 

set_with_dataframe(worksheet, df)
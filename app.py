import streamlit as st
import json
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# App Title
st.title("BATPATH Dashboard")

# ✅ Load Google Cloud credentials from Streamlit secrets
if "gcp_service_account" in st.secrets:
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
else:
    st.error("❌ No credentials found! Make sure to upload `secrets.toml` in Render.")
    st.stop()

st.success("✅ Google Service Account Loaded Successfully")

# ✅ Connect to Google Sheets API
def get_google_sheets_service():
    try:
        service = build("sheets", "v4", credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets API: {e}")
        return None

service = get_google_sheets_service()

# ✅ Fetch data from Google Sheets
SPREADSHEET_ID = "your-google-sheet-id"  # Replace with your actual Google Sheet ID
RANGE_NAME = "Sheet1!A1:D10"  # Adjust as needed

def fetch_sheet_data():
    if service:
        try:
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
            values = result.get("values", [])

            if not values:
                st.warning("No data found in the Google Sheet.")
                return None

            df = pd.DataFrame(values[1:], columns=values[0])  # Convert to DataFrame
            return df

        except Exception as e:
            st.error(f"Error fetching Google Sheets data: {e}")
            return None
    else:
        st.error("Google Sheets API service is not available.")
        return None

# ✅ Display data in Streamlit
st.subheader("Google Sheets Data")
df = fetch_sheet_data()
if df is not None:
    st.dataframe(df)

# ✅ Deployment confirmation
st.info("🚀 App is running on Render successfully!")

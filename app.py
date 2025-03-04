import streamlit as st
import json
import pandas as pd
import numpy as np
import plotly.express as px
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# -------------------------
# GOOGLE SHEETS INTEGRATION
# -------------------------

# Load Google Cloud credentials from local secrets.json
secrets_path = os.path.expanduser("~/.streamlit/secrets.json")

if os.path.exists(secrets_path):
    with open(secrets_path, "r") as f:
        creds_dict = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    st.success("✅ Google Service Account Loaded Successfully")
else:
    st.error("❌ No credentials found! Make sure to upload `secrets.json` on AWS Lightsail.")
    st.stop()

# Connect to Google Sheets API
def get_google_sheets_service():
    try:
        service = build("sheets", "v4", credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets API: {e}")
        return None

service = get_google_sheets_service()

# Fetch Data from Google Sheets
SPREADSHEET_ID = "your-google-sheet-id"  # Replace with your actual Google Sheet ID
RANGE_NAME = "Sheet1!A1:Z1000"  # Adjust as needed

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

df = fetch_sheet_data()
if df is not None:
    st.dataframe(df)

# -------------------------
# PLAYER SELECTION
# -------------------------

st.title("⚾ BATPATH Player Dashboard")

if df is not None:
    player_list = df["Player Name"].unique().tolist()
    selected_player = st.selectbox("Select a Player:", player_list)
    player_data = df[df["Player Name"] == selected_player]

# -------------------------
# PERFORMANCE VISUALIZATIONS
# -------------------------

if df is not None and not player_data.empty:
    st.subheader("📊 Performance Over Time")
    for metric in ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"]:
        if metric in player_data.columns:
            fig = px.line(player_data, x="Date", y=metric, title=f"{metric} Over Time", markers=True)
            st.plotly_chart(fig)

# -------------------------
# PERFORMANCE ALERTS 🚦
# -------------------------

st.subheader("🚦 Performance Alerts")
def get_alert_color(current, previous):
    if current < previous:
        return "🟢 Improving"
    elif current == previous:
        return "🟡 No Change"
    else:
        return "🔴 Declining"

if len(player_data) > 1:
    latest = player_data.iloc[-1]
    previous = player_data.iloc[-2]

    for metric in ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"]:
        if metric in player_data.columns:
            alert_status = get_alert_color(latest[metric], previous[metric])
            st.write(f"**{metric}:** {alert_status}")

# -------------------------
# AI-DRIVEN DRILL RECOMMENDATIONS 🤖
# -------------------------

st.subheader("🎯 Drill Recommendations")
drill_recommendations = {
    "Foundation": ["Basic Acceleration Drills", "Bodyweight Strength Work"],
    "Developing": ["Lateral Speed Drills", "Core Stability Training"],
    "Advanced": ["Explosive Plyometrics", "Sprint Mechanics Drills"],
    "Elite": ["High-Performance Speed Workouts", "Strength-Speed Training"]
}

def get_tier(metric, value):
    if metric == "40-Yard Dash":
        return "Elite" if value <= 5.0 else "Advanced" if value <= 5.5 else "Developing" if value <= 6.0 else "Foundation"
    elif metric == "Broad Jump":
        return "Elite" if value >= 80 else "Advanced" if value >= 70 else "Developing" if value >= 60 else "Foundation"
    return "Unknown"

for metric in ["40-Yard Dash", "Broad Jump"]:
    if metric in player_data.columns:
        tier = get_tier(metric, player_data.iloc[-1][metric])
        recommended_drills = drill_recommendations.get(tier, ["No drills assigned"])
        st.write(f"**{metric} Drills ({tier} Level):** {', '.join(recommended_drills)}")

# -------------------------
# SYSTEM-WIDE LEADERBOARD 🏆
# -------------------------

st.subheader("🌎 BATPATH Leaderboard")
ranking_metric = st.selectbox("Rank Players By:", ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"])

if df is not None and ranking_metric in df.columns:
    df["Tier"] = df[ranking_metric].apply(lambda x: get_tier(ranking_metric, x))
    rankings = df.sort_values(by=ranking_metric, ascending=False)[["Player Name", "Team", ranking_metric, "Tier"]]
    st.write(rankings)

# -------------------------
# VIDEO UPLOAD FOR COACHES 📹
# -------------------------

st.subheader("📹 Submit Training Video")
uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi"])
if uploaded_file:
    save_path = f"videos/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Video uploaded successfully: {uploaded_file.name}")

st.info("🚀 BATPATH is now fully operational & ready for AWS deployment!")


import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import json

# -------------------------
# GOOGLE SHEETS INTEGRATION
# -------------------------

# Load credentials securely from Streamlit secrets
creds_dict = json.loads(st.secrets["gcp"]["service_account"])
creds = Credentials.from_service_account_info(creds_dict)

# Authenticate Google Sheets API
client = gspread.authorize(creds)

# Open Google Sheet (Modify sheet name if needed)
try:
    sheet = client.open("BATPATH_Player_Data").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Error loading data: {e}")
    df = pd.DataFrame()  # Use empty DataFrame if loading fails

# Ensure Date column exists
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
else:
    df["Date"] = pd.NaT

# -------------------------
# STREAMLIT DASHBOARD
# -------------------------

st.set_page_config(page_title="BATPATH Player Dashboard", layout="wide")

# Title
st.title("⚾ BATPATH Player Dashboard")

# Check if data is available
if df.empty:
    st.warning("No data available. Please check the Google Sheet.")
    st.stop()

# Player Selection
player_list = df["Player Name"].unique().tolist() if "Player Name" in df.columns else []
selected_player = st.selectbox("Select a Player:", player_list)

# Filter Data for Selected Player
player_data = df[df["Player Name"] == selected_player] if not df.empty else pd.DataFrame()

# Display Latest Test Results
if not player_data.empty:
    st.subheader("📊 Latest Test Results")
    latest_test = player_data.iloc[-1]  # Get most recent test data
    st.write(latest_test)

    # -------------------------
    # LINE GRAPHS (Tracking Progress Over Time)
    # -------------------------

    st.subheader("📈 Performance Over Time")
    for metric in ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"]:
        if metric in player_data.columns:
            fig = px.line(player_data, x="Date", y=metric, title=f"{metric} Over Time", markers=True)
            st.plotly_chart(fig)

    # -------------------------
    # TEAM RANKINGS
    # -------------------------

    st.subheader("🏆 Team Rankings")
    ranking_metric = st.selectbox("Rank Players By:", ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"])

    if ranking_metric in df.columns and "Team" in df.columns:
        team_players = df[df["Team"] == latest_test["Team"]]
        team_rankings = team_players.sort_values(by=ranking_metric, ascending=False)[["Player Name", ranking_metric]]
        st.write(team_rankings)

    # -------------------------
    # BATPATH-WIDE RANKINGS
    # -------------------------

    st.subheader("🌎 BATPATH Leaderboard")
    if ranking_metric in df.columns:
        batpath_rankings = df.sort_values(by=ranking_metric, ascending=False)[["Player Name", "Team", ranking_metric]]
        st.write(batpath_rankings)

else:
    st.warning("No data found for the selected player.")

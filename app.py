import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

# -------------------------
# GOOGLE SHEETS INTEGRATION
# -------------------------

# Authenticate with Google Sheets using credentials stored in Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]  # No need for json.loads()
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

# Authorize with Google Sheets
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open("BATPATH_Player_Data").sheet1  # Change to your Google Sheet name
data = sheet.get_all_records()
df = pd.DataFrame(data)

# -------------------------
# STREAMLIT DASHBOARD
# -------------------------

# Title
st.title("⚾ BATPATH Player Dashboard")

# Player Selection
player_list = df["Player Name"].unique().tolist()
selected_player = st.selectbox("Select a Player:", player_list)

# Filter Data for Selected Player
player_data = df[df["Player Name"] == selected_player]

# Display Latest Test Results
st.subheader("📊 Latest Test Results")
if not player_data.empty:
    latest_test = player_data.iloc[-1]  # Get most recent test data
    st.write(latest_test)
else:
    st.write("No data available for this player.")

# -------------------------
# LINE GRAPHS (Tracking Progress Over Time)
# -------------------------

st.subheader("📈 Performance Over Time")

metrics = ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"]
for metric in metrics:
    if metric in player_data.columns:
        fig = px.line(player_data, x="Date", y=metric, title=f"{metric} Over Time", markers=True)
        st.plotly_chart(fig)
    else:
        st.write(f"No data for {metric}")

# -------------------------
# TEAM RANKINGS
# -------------------------

st.subheader("🏆 Team Rankings")
ranking_metric = st.selectbox("Rank Players By:", metrics)

if not df.empty and ranking_metric in df.columns:
    team_players = df[df["Team"] == player_data["Team"].values[0]]
    team_rankings = team_players.sort_values(by=ranking_metric, ascending=False)[["Player Name", ranking_metric]]
    st.write(team_rankings)
else:
    st.write("No ranking data available.")

# -------------------------
# BATPATH-WIDE RANKINGS
# -------------------------

st.subheader("🌎 BATPATH Leaderboard")
if not df.empty and ranking_metric in df.columns:
    batpath_rankings = df.sort_values(by=ranking_metric, ascending=False)[["Player Name", "Team", ranking_metric]]
    st.write(batpath_rankings)
else:
    st.write("No leaderboard data available.")

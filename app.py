import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import gspread
import json
import matplotlib.pyplot as plt
from google.oauth2.service_account import Credentials

# -------------------------
# GOOGLE SHEETS INTEGRATION
# -------------------------

# Authenticate Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = json.loads(st.secrets["gcp_service_account"])
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")  # Ensure correct key format

# Authenticate using Google Credentials
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
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
latest_test = player_data.iloc[-1]  # Get most recent test data
st.write(latest_test)

# -------------------------
# LINE GRAPHS (Tracking Progress Over Time)
# -------------------------

st.subheader("📈 Performance Over Time")

for metric in ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"]:
    fig = px.line(player_data, x="Date", y=metric, title=f"{metric} Over Time", markers=True)
    st.plotly_chart(fig)

# -------------------------
# TEAM RANKINGS
# -------------------------

st.subheader("🏆 Team Rankings")
ranking_metric = st.selectbox("Rank Players By:", ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"])

team_players = df[df["Team"] == latest_test["Team"]]
team_rankings = team_players.sort_values(by=ranking_metric, ascending=False)[["Player Name", ranking_metric]]

st.write(team_rankings)

# -------------------------
# BATPATH-WIDE RANKINGS
# -------------------------

st.subheader("🌎 BATPATH Leaderboard")
batpath_rankings = df.sort_values(by=ranking_metric, ascending=False)[["Player Name", "Team", ranking_metric]]
st.write(batpath_rankings)

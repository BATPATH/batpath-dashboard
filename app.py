import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import gspread
import json
from google.oauth2.service_account import Credentials
import os

# -------------------------
# GOOGLE SHEETS INTEGRATION
# -------------------------

# Load Google Credentials from Streamlit Secrets
creds_dict = json.loads(st.secrets["gcp_service_account"])
creds = Credentials.from_service_account_info(creds_dict, scopes=[
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])

client = gspread.authorize(creds)

# Open Google Sheet (Ensure this sheet exists & is shared with the service account)
sheet = client.open("BATPATH_Player_Data").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# -------------------------
# STREAMLIT DASHBOARD
# -------------------------

st.title("⚾ BATPATH Player Dashboard")

# Player Selection
player_list = df["Player Name"].unique().tolist()
selected_player = st.selectbox("Select a Player:", player_list)

# Filter Data for Selected Player
player_data = df[df["Player Name"] == selected_player]

# -------------------------
# Skill Progression Tier Calculation
# -------------------------

def get_tier(metric, value):
    """Assigns tier based on performance metric"""
    if metric == "40-Yard Dash":
        if value > 6.0:
            return "Foundation"
        elif value > 5.5:
            return "Developing"
        elif value > 5.0:
            return "Advanced"
        else:
            return "Elite"
    elif metric == "Broad Jump":
        if value < 60:
            return "Foundation"
        elif value < 70:
            return "Developing"
        elif value < 80:
            return "Advanced"
        else:
            return "Elite"
    return "Unknown"

# Apply tier ranking to key metrics
for metric in ["40-Yard Dash", "Broad Jump"]:
    if metric in player_data.columns:
        player_data[f"{metric} Tier"] = player_data[metric].apply(lambda x: get_tier(metric, x))

# -------------------------
# Color-Coded Performance Alerts
# -------------------------

st.subheader("🚦 Performance Alerts")
def get_alert_color(current, previous):
    """Color-coded performance tracking"""
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
# Drill Recommendations Based on Tiers
# -------------------------

st.subheader("🎯 Drill Recommendations")
drill_recommendations = {
    "Foundation": ["Basic Acceleration Drills", "Bodyweight Strength Work"],
    "Developing": ["Lateral Speed Drills", "Core Stability Training"],
    "Advanced": ["Explosive Plyometrics", "Sprint Mechanics Drills"],
    "Elite": ["High-Performance Speed Workouts", "Strength-Speed Training"]
}

for metric in ["40-Yard Dash", "Broad Jump"]:
    if f"{metric} Tier" in player_data.columns:
        tier = player_data.iloc[-1][f"{metric} Tier"]
        recommended_drills = drill_recommendations.get(tier, ["No drills assigned"])
        st.write(f"**{metric} Drills ({tier} Level):** {', '.join(recommended_drills)}")

# -------------------------
# Video Upload Feature for Coaches
# -------------------------

st.subheader("📹 Submit Training Video")
st.write("Coaches can upload training videos for review.")

uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi"])
if uploaded_file:
    save_path = f"videos/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Video uploaded successfully: {uploaded_file.name}")

# -------------------------
# Performance Trend Graphs
# -------------------------

st.subheader("📈 Performance Over Time")
for metric in ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"]:
    if metric in player_data.columns:
        fig = px.line(player_data, x="Date", y=metric, title=f"{metric} Over Time", markers=True)
        st.plotly_chart(fig)

# -------------------------
# Team & Global Rankings
# -------------------------

st.subheader("🏆 Team Rankings")
ranking_metric = st.selectbox("Rank Players By:", ["40-Yard Dash", "Broad Jump", "Push-Ups", "Wall Sit"])

team_players = df[df["Team"] == player_data.iloc[-1]["Team"]]
team_players["Tier"] = team_players[ranking_metric].apply(lambda x: get_tier(ranking_metric, x))
team_rankings = team_players.sort_values(by=ranking_metric, ascending=False)[["Player Name", ranking_metric, "Tier"]]

st.write(team_rankings)

st.subheader("🌎 BATPATH Leaderboard")
batpath_players = df.copy()
batpath_players["Tier"] = batpath_players[ranking_metric].apply(lambda x: get_tier(ranking_metric, x))
batpath_rankings = batpath_players.sort_values(by=ranking_metric, ascending=False)[["Player Name", "Team", ranking_metric, "Tier"]]

st.write(batpath_rankings)

# -------------------------
# Ensuring Streamlit Runs Correctly on Cloud
# -------------------------

port = int(os.environ.get("PORT", 8501))  # Streamlit default port

if __name__ == "__main__":
    st.run(port=port, host="0.0.0.0")

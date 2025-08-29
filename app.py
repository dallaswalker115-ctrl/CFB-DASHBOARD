import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Load dataset
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

df = load_data()

# ----------------------------
# Build game results
# ----------------------------
def build_game_results(df):
    results = []

    for game_id, group in df.groupby("gameid"):
        if group.shape[0] < 2:
            continue

        # home/away teams
        home = group[group["homeaway"] == "home"]
        away = group[group["homeaway"] == "away"]

        if home.empty or away.empty:
            continue

        home = home.iloc[0]
        away = away.iloc[0]

        spread = home["spread"]
        overunder = home["overunder"]

        # spread result (from home perspective)
        margin = home["points"] - away["points"]
        if margin + spread > 0:
            spread_result = "Home Covers"
        elif margin + spread < 0:
            spread_result = "Away Covers"
        else:
            spread_result = "Push"

        results.append({
            "gameid": game_id,
            "week": home["week"],
            "home_team": home["team"],
            "away_team": away["team"],
            "home_points": home["points"],
            "away_points": away["points"],
            "spread": spread,
            "overunder": overunder,
            "spread_result": spread_result
        })

    return pd.DataFrame(results)

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

confs = sorted(df["conference"].dropna().unique())
selected_conf = st.sidebar.selectbox("Select Conference", ["All"] + confs)

teams = sorted(df["team"].dropna().unique())
selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)

weeks = sorted(df["week"].dropna().unique())
selected_week = st.sidebar.selectbox("Select Week", ["All"] + [str(w) for w in weeks])

view_mode = st.sidebar.radio("View Mode", ["Game Results", "Team Stats"])

# ----------------------------
# Apply filters
# ----------------------------
filtered = df.copy()

if selected_conf != "All":
    filtered = filtered[filtered["conference"] == selected_conf]

if selected_team != "All":
    filtered = filtered[filtered["team"] == selected_team]

if selected_week != "All":
    filtered = filtered[filtered["week"] == int(selected_week)]

# ----------------------------
# Main View
# ----------------------------
st.title("🏈 College Football Dashboard (2024 Season)")

if view_mode == "Game Results":
    results_df = build_game_results(filtered)
    if results_df.empty:
        st.warning("No game results available for selection.")
    else:
        st.subheader("Game Results")
        st.dataframe(results_df)

        # Chart: Point Differentials
        st.subheader("Point Differentials by Game")
        plt.figure(figsize=(8,5))
        plt.bar(results_df["home_team"] + " vs " + results_df["away_team"],
                results_df["home_points"] - results_df["away_points"])
        plt.xticks(rotation=90)
        plt.ylabel("Point Differential (Home - Away)")
        st.pyplot(plt)

elif view_mode == "Team Stats":
    if filtered.empty:
        st.warning("No team stats available for selection.")
    else:
        st.subheader("Team Stats")
        st.dataframe(filtered)

        # Chart: Points per Team
        st.subheader("Points per Team")
        plt.figure(figsize=(8,5))
        avg_points = filtered.groupby("team")["points"].mean().sort_values(ascending=False)
        avg_points.plot(kind="bar")
        plt.ylabel("Average Points")
        st.pyplot(plt)











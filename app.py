import streamlit as st
import pandas as pd

# =============================
# Load Local CSV
# =============================
@st.cache_data
def load_data():
    return pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

df = load_data()
def build_game_results(df):
    """
    Build game-level results table from team-level stats.
    """
    games = []

    for game_id, group in df.groupby("gameid"):
        if len(group) != 2:
            continue  # skip bad data

        home = group[group["homeaway"] == "home"].iloc[0]
        away = group[group["homeaway"] == "away"].iloc[0]

        games.append({
            "year": home["year"],
            "week": home["week"],
            "gameid": game_id,
            "home_team": home["team"],
            "away_team": away["team"],
            "home_points": home["points"],
            "away_points": away["points"],
            "spread": home.get("spread", None),
            "overunder": home.get("overunder", None),
            "spread_result": home.get("spread_result", None)
        })

    results_df = pd.DataFrame(games)
    return results_df


st.title("🏈 College Football Dashboard (2024 Season)")

# =============================
# Sidebar Filters
# =============================

# Week filter
weeks = sorted(df["week"].dropna().unique()) if "week" in df.columns else []
week_choice = st.sidebar.selectbox("Select Week", ["All"] + list(map(str, weeks)))

# Conference filter
conferences = sorted(df["conference"].dropna().unique()) if "conference" in df.columns else []
conference_choice = st.sidebar.selectbox("Select Conference", ["All"] + conferences)

# ✅ Safe team filter (fix for missing columns)
team_sources = []
for col in ["home_team", "away_team", "team"]:
    if col in df.columns:
        team_sources.extend(df[col].dropna().unique())

teams = sorted(set(team_sources))
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)

# =============================
# Apply Filters
# =============================
filtered = df.copy()

if week_choice != "All":
    filtered = filtered[filtered["week"] == int(week_choice)]

if conference_choice != "All":
    filtered = filtered[filtered["conference"] == conference_choice]

if team_choice != "All":
    filtered = filtered[
        (filtered.get("home_team") == team_choice) |
        (filtered.get("away_team") == team_choice) |
        (filtered.get("team") == team_choice)
    ]

# =============================
# Game Results Table
# =============================
if {"home_team", "away_team", "home_points", "away_points"}.issubset(filtered.columns):
    st.subheader("📊 Game Results")
    results = filtered[["week", "home_team", "away_team", "home_points", "away_points"]].drop_duplicates()
    st.dataframe(results)
else:
    st.info("No game results available in this dataset.")

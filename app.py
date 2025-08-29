import streamlit as st
import pandas as pd

# =============================
# Load local CSV instead of API
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")
    return df


# =============================
# Streamlit App
# =============================
st.title("🏈 College Football Dashboard (2024 Season)")

df = load_data()

if df.empty:
    st.warning("⚠️ No data available")
    st.stop()

# Sidebar filters
view_choice = st.radio("Select View", ["Game Results", "Team Stats"])

weeks = sorted(df["week"].dropna().unique()) if "week" in df.columns else []
conferences = sorted(df["conference"].dropna().unique()) if "conference" in df.columns else []
teams = sorted(set(df["home_team"].dropna().unique()).union(df["away_team"].dropna().unique()).union(df["team"].dropna().unique()))

week_choice = st.sidebar.selectbox("Select Week", ["All"] + list(map(str, weeks)))
conference_choice = st.sidebar.selectbox("Select Conference", ["All"] + conferences)
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)

# ==========================================
# GAME RESULTS VIEW
# ==========================================
if view_choice == "Game Results":
    game_cols = [
        "year", "week", "home_team", "away_team",
        "home_points", "away_points",
        "spread", "overunder", "spread_result", "conference"
    ]
    existing_cols = [c for c in game_cols if c in df.columns]
    games = df[existing_cols].drop_duplicates()

    filtered = games.copy()
    if week_choice != "All":
        filtered = filtered[filtered["week"] == int(week_choice)]
    if conference_choice != "All":
        filtered = filtered[filtered["conference"] == conference_choice]
    if team_choice != "All":
        filtered = filtered[(filtered["home_team"] == team_choice) | (filtered["away_team"] == team_choice)]

    st.subheader("📊 Game Results")
    st.dataframe(filtered)

    if not filtered.empty:
        win_counts = {}
        for _, row in filtered.iterrows():
            if pd.notna(row["home_points"]) and pd.notna(row["away_points"]):
                if row["home_points"] > row["away_points"]:
                    win_counts[row["home_team"]] = win_counts.get(row["home_team"], 0) + 1
                elif row["away_points"] > row["home_points"]:
                    win_counts[row["away_team"]] = win_counts.get(row["away_team"], 0) + 1

        if win_counts:
            chart_df = pd.DataFrame(list(win_counts.items()), columns=["Team", "Wins"])
            st.subheader("🏆 Wins")
            st.bar_chart(chart_df.set_index("Team"))

# ==========================================
# TEAM STATS VIEW
# ==========================================
elif view_choice == "Team Stats":
    team_cols = [
        "year", "week", "team", "conference", "points",
        "rushingyards", "passingtds", "turnovers", "totalyards", "firstdowns"
    ]
    existing_cols = [c for c in team_cols if c in df.columns]
    teams_df = df[existing_cols].copy()

    filtered = teams_df.copy()
    if week_choice != "All":
        filtered = filtered[filtered["week"] == int(week_choice)]
    if conference_choice != "All":
        filtered = filtered[filtered["conference"] == conference_choice]
    if team_choice != "All":
        filtered = filtered[filtered["team"] == team_choice]

    st.subheader("📊 Team Statistics")
    st.dataframe(filtered)

    if not filtered.empty:
        st.subheader("📈 Average Points by Team")
        avg_points = filtered.groupby("team")["points"].mean().sort_values(ascending=False)
        st.bar_chart(avg_points)




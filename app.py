import streamlit as st
import pandas as pd

# Load CSV
@st.cache_data
def load_data():
    return pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

df = load_data()

# Sidebar Filters
conferences = sorted(df["conference"].dropna().unique())
conference_choice = st.sidebar.selectbox("Select Conference", ["All"] + conferences)

teams = sorted(df["team"].dropna().unique())
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)

filtered = df.copy()
if conference_choice != "All":
    filtered = filtered[filtered["conference"] == conference_choice]
if team_choice != "All":
    filtered = filtered[filtered["team"] == team_choice]

# Toggle between views
view = st.radio("📊 Select View", ["Game Results", "Team Stats"])

# ========================
# GAME RESULTS VIEW
# ========================
if view == "Game Results":
    def build_game_results(df):
        results = []
        for game_id, group in df.groupby("gameid"):
            if group.empty: 
                continue
            teams = group.set_index("homeaway")
            if "home" not in teams.index or "away" not in teams.index:
                continue

            home = teams.loc["home"]
            away = teams.loc["away"]

            results.append({
                "Week": home["week"],
                "Home Team": home["team"],
                "Home Points": home.get("points", None),
                "Away Team": away["team"],
                "Away Points": away.get("points", None),
                "Spread": home.get("spread", None),
                "O/U": home.get("overunder", None),
                "Spread Result": home.get("spread_result", None),
            })
        return pd.DataFrame(results)

    results_df = build_game_results(filtered)

    if results_df.empty:
        st.warning("No game results available for this filter.")
    else:
        st.subheader("🏆 Game Results")
        st.dataframe(results_df)

# ========================
# TEAM STATS VIEW
# ========================
elif view == "Team Stats":
    st.subheader("📈 Team Stats")
    st.dataframe(filtered)




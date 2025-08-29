import streamlit as st
import pandas as pd

# Load CSV
@st.cache_data
def load_data():
    df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")
    # normalize column names
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# Sidebar Filters
conferences = sorted(df["conference"].dropna().unique())
conference_choice = st.sidebar.selectbox("Select Conference", ["All"] + conferences)

teams = sorted(df["team"].dropna().unique())
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)

weeks = sorted(df["week"].dropna().unique())
week_choice = st.sidebar.selectbox("Select Week", ["All"] + [str(w) for w in weeks])

filtered = df.copy()
if conference_choice != "All":
    filtered = filtered[filtered["conference"] == conference_choice]
if team_choice != "All":
    filtered = filtered[filtered["team"] == team_choice]
if week_choice != "All":
    filtered = filtered[filtered["week"] == int(week_choice)]

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

        home_points = home.get("points", None)
        away_points = away.get("points", None)
        spread = home.get("spread", None)

        spread_result = None
        if pd.notnull(home_points) and pd.notnull(away_points) and pd.notnull(spread):
            margin = home_points - away_points
            spread_result = "Cover" if margin + spread > 0 else "No Cover"

        results.append({
            "Week": home["week"],
            "Home Team": home["team"],
            "Home Points": home_points,
            "Away Team": away["team"],
            "Away Points": away_points,
            "Spread": spread,
            "O/U": home.get("overunder", None),
            "Spread Result": spread_result,
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





import streamlit as st
import pandas as pd

# Load CSV
@st.cache_data
def load_data():
    return pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

df = load_data()

st.title("🏈 College Football Dashboard (2024 Season)")

# Sidebar filters
conferences = sorted(df["conference"].dropna().unique())
selected_conf = st.sidebar.selectbox("Select Conference", ["All"] + conferences)

teams = sorted(df["team"].dropna().unique())
selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)

view_mode = st.sidebar.radio("View Mode", ["Team Stats", "Game Results"])


# ----------------------------
# Build Game Results Function
# ----------------------------
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
        overunder = home.get("overunder", None)

        # Spread Result
        spread_result = None
        if pd.notnull(home_points) and pd.notnull(away_points) and pd.notnull(spread):
            margin = home_points - away_points
            spread_result = "Cover" if margin + spread > 0 else "No Cover"

        # Over/Under Result
        ou_result = None
        if pd.notnull(home_points) and pd.notnull(away_points) and pd.notnull(overunder):
            total = home_points + away_points
            if total > overunder:
                ou_result = "Over"
            elif total < overunder:
                ou_result = "Under"
            else:
                ou_result = "Push"

        results.append({
            "Week": home["week"],
            "Home Team": home["team"],
            "Home Points": home_points,
            "Away Team": away["team"],
            "Away Points": away_points,
            "Spread": spread,
            "Spread Result": spread_result,
            "O/U": overunder,
            "O/U Result": ou_result,
        })
    return pd.DataFrame(results)


# ----------------------------
# Apply Filters
# ----------------------------
filtered = df.copy()
if selected_conf != "All":
    filtered = filtered[filtered["conference"] == selected_conf]
if selected_team != "All":
    filtered = filtered[filtered["team"] == selected_team]


# ----------------------------
# Display
# ----------------------------
if view_mode == "Team Stats":
    st.subheader("📊 Team Stats")
    st.dataframe(filtered)

elif view_mode == "Game Results":
    st.subheader("🏆 Game Results")
    results_df = build_game_results(filtered)
    if not results_df.empty:
        st.dataframe(results_df)
    else:
        st.warning("No results available for your selection.")






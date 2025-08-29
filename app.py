import streamlit as st
import pandas as pd

# =============================
# Load CSV
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

    # Normalize column names: lowercase, strip spaces
    df.columns = df.columns.str.strip().str.lower()

    return df

df = load_data()

# =============================
# Build Game Results
# =============================
def build_game_results(df):
    """
    Build game-level results table from team-level stats.
    Each gameid has two rows: one home, one away.
    """

    # Try to detect correct game id column
    game_id_col = None
    for col in df.columns:
        if col in ["gameid", "game_id", "id"]:
            game_id_col = col
            break

    if not game_id_col:
        st.error("❌ No gameid column found in dataset.")
        return pd.DataFrame()

    games = []
    for game_id, group in df.groupby(game_id_col):
        if len(group) != 2:
            continue  # skip incomplete games

        home = group[group["homeaway"] == "home"].iloc[0]
        away = group[group["homeaway"] == "away"].iloc[0]

        games.append({
            "year": home.get("year"),
            "week": home.get("week"),
            "gameid": game_id,
            "home_team": home.get("team"),
            "away_team": away.get("team"),
            "home_points": home.get("points"),
            "away_points": away.get("points"),
            "spread": home.get("spread"),
            "overunder": home.get("overunder"),
            "spread_result": home.get("spread_result"),
        })

    return pd.DataFrame(games)

results_df = build_game_results(df)

# =============================
# Streamlit App
# =============================
st.title("🏈 College Football Dashboard (2024 Season)")

if results_df.empty:
    st.warning("⚠️ No game results available.")
    st.stop()

# Sidebar Filters
weeks = sorted(results_df["week"].dropna().unique())
conferences = sorted(df["conference"].dropna().unique())
teams = sorted(df["team"].dropna().unique())

week_choice = st.sidebar.selectbox("Select Week", ["All"] + list(map(str, weeks)))
conf_choice = st.sidebar.selectbox("Select Conference", ["All"] + conferences)
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)

filtered = results_df.copy()

if week_choice != "All":
    filtered = filtered[filtered["week"] == int(week_choice)]
if conf_choice != "All":
    valid_teams = df[df["conference"] == conf_choice]["team"].unique()
    filtered = filtered[(filtered["home_team"].isin(valid_teams)) | (filtered["away_team"].isin(valid_teams))]
if team_choice != "All":
    filtered = filtered[(filtered["home_team"] == team_choice) | (filtered["away_team"] == team_choice)]

# =============================
# Display Results
# =============================
st.subheader("📊 Game Results")
st.dataframe(filtered)



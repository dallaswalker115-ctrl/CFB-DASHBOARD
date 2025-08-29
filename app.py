import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Load dataset
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")
    df.columns = [c.lower() for c in df.columns]  # normalize names
    return df

df = load_data()

# ----------------------------
# Build game results
# ----------------------------
def build_game_results(df):
    results = []

    if "gameid" in df.columns:
        groups = df.groupby("gameid")
    else:
        groups = df.groupby("week")

    for key, group in groups:
        if group.shape[0] < 2:
            continue

        home = group[group["homeaway"] == "home"]
        away = group[group["homeaway"] == "away"]

        if home.empty or away.empty:
            continue

        home = home.iloc[0]
        away = away.iloc[0]

        spread = home.get("spread", None)
        overunder = home.get("overunder", None)

        # spread result (from home perspective)
        margin = home["points"] - away["points"]
        spread_result = None
        if pd.notna(spread):
            if margin + spread > 0:
                spread_result = "Home Covers"
            elif margin + spread < 0:
                spread_result = "Away Covers"
            else:
                spread_result = "Push"

        results.append({
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
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

weeks = sorted(df["week"].dropna().unique())
selected_week = st.sidebar.selectbox("Select Week", weeks)

conferences = sorted(df["conference"].dropna().unique())
selected_conf = st.sidebar.multiselect("Select Conference(s)", conferences)

teams = sorted(df["team"].dropna().unique())
selected_team = st.sidebar.selectbox("Select Team (optional)", ["All Teams"] + teams)

view_mode = st.sidebar.radio("View Mode", ["Team Stats", "Game Results"])

# ----------------------------
# Apply filters
# ----------------------------
filtered = df[df["week"] == selected_week]

if selected_conf:
    filtered = filtered[filtered["conference"].isin(selected_conf)]

# ----------------------------
# View: Team Stats
# ----------------------------
if view_mode == "Team Stats":
    st.header(f"Team Stats - Week {selected_week}")

    if selected_team != "All Teams":
        filtered = filtered[filtered["team"] == selected_team]

    st.dataframe(filtered)

# ----------------------------
# View: Game Results
# ----------------------------
else:
    results_df = build_game_results(filtered)

    if selected_team != "All Teams":
        results_df = results_df[
            (results_df["home_team"] == selected_team) |
            (results_df["away_team"] == selected_team)
        ]

    st.header(f"Game Results - Week {selected_week}")
    st.dataframe(results_df)

    # Spread chart per team
    if not results_df.empty and selected_team != "All Teams":
        spread_counts = results_df["spread_result"].value_counts()

        fig, ax = plt.subplots()
        spread_counts.plot(kind="bar", ax=ax)
        ax.set_title(f"{selected_team} Spread Results - Week {selected_week}")
        ax.set_ylabel("Games")
        st.pyplot(fig)












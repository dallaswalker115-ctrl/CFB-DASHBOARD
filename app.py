import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

df = load_data()

# ----------------------------
# Helper: Build game results
# ----------------------------
def build_game_results(df):
    results = []
    for game_id, group in df.groupby("gameid"):
        if {"homeaway", "team", "points"}.issubset(group.columns):
            home = group[group["homeaway"] == "home"]
            away = group[group["homeaway"] == "away"]

            if not home.empty and not away.empty:
                results.append({
                    "gameid": game_id,
                    "week": home["week"].iloc[0],
                    "home_team": home["team"].iloc[0],
                    "away_team": away["team"].iloc[0],
                    "home_points": home["points"].iloc[0],
                    "away_points": away["points"].iloc[0],
                    "spread": home["spread"].iloc[0] if "spread" in home else None,
                    "overunder": home["overunder"].iloc[0] if "overunder" in home else None,
                })

    results_df = pd.DataFrame(results)

    # Add spread result (vs. home team)
    if not results_df.empty and "spread" in results_df.columns:
        def outcome(row):
            if pd.isna(row["spread"]):
                return "No Line"
            margin = row["home_points"] - row["away_points"]
            if margin + row["spread"] > 0:
                return "Home Covers"
            elif margin + row["spread"] < 0:
                return "Away Covers"
            else:
                return "Push"

        results_df["spread_result"] = results_df.apply(outcome, axis=1)

    return results_df

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

weeks = sorted(df["week"].dropna().unique())
selected_week = st.sidebar.selectbox("Select Week", ["All Weeks"] + list(weeks))

conferences = sorted(df["conference"].dropna().unique())
selected_conf = st.sidebar.multiselect("Select Conference(s)", conferences)

teams = sorted(df["team"].dropna().unique())
selected_team = st.sidebar.selectbox("Select Team (optional)", ["All Teams"] + teams)

view_mode = st.sidebar.radio("View Mode", ["Team Stats", "Game Results"])

# ----------------------------
# Apply filters
# ----------------------------
filtered = df.copy()

if selected_week != "All Weeks":
    filtered = filtered[filtered["week"] == selected_week]

if selected_conf:
    filtered = filtered[filtered["conference"].isin(selected_conf)]

# ----------------------------
# View: Team Stats
# ----------------------------
if view_mode == "Team Stats":
    st.header(f"Team Stats - {selected_week if selected_week!='All Weeks' else 'All Weeks'}")

    if selected_team != "All Teams":
        team_stats = filtered[filtered["team"] == selected_team]
        st.dataframe(team_stats)
    else:
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

    st.header(f"Game Results - {selected_week if selected_week!='All Weeks' else 'All Weeks'}")
    st.dataframe(results_df)

    # ------------------------
    # Spread chart (cumulative across ALL WEEKS)
    # ------------------------
    if selected_team != "All Teams":
        # Build full results without week filter to get cumulative spread
        full_results = build_game_results(df)
        team_results = full_results[
            (full_results["home_team"] == selected_team) |
            (full_results["away_team"] == selected_team)
        ]

        if not team_results.empty:
            spread_counts = team_results["spread_result"].value_counts()

            fig, ax = plt.subplots()
            spread_counts.plot(kind="bar", ax=ax)
            ax.set_title(f"{selected_team} Spread Results (Cumulative)")
            ax.set_ylabel("Games")
            st.pyplot(fig)













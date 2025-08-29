import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
@st.cache_data
def load_data():
    df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

st.title("🏈 College Football Dashboard (2024 Season)")

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("Filters")

# Toggle between Team Stats and Game Results
view_mode = st.sidebar.radio("View Mode", ["Team Stats", "Game Results"])

# Conference filter
conferences = sorted(df["conference"].dropna().unique())
selected_conf = st.sidebar.selectbox("Select Conference", ["All"] + conferences)

# Team filter
teams = sorted(df["team"].dropna().unique())
selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)

# Week filter
weeks = sorted(df["week"].dropna().unique())
selected_week = st.sidebar.selectbox("Select Week", ["All"] + [str(w) for w in weeks])

# Apply filters
filtered = df.copy()

if selected_conf != "All":
    filtered = filtered[filtered["conference"] == selected_conf]

if selected_team != "All":
    filtered = filtered[filtered["team"] == selected_team]

if selected_week != "All":
    filtered = filtered[filtered["week"] == int(selected_week)]


# Apply filters
filtered = df.copy()

if selected_conf != "All":
    filtered = filtered[filtered["conference"] == selected_conf]

if selected_team != "All":
    # keep rows where selected team is either the 'team' column OR home/away
    filtered = filtered[
        (filtered["team"] == selected_team) |
        (filtered["home_team"] == selected_team) |
        (filtered["away_team"] == selected_team)
    ]

if selected_week != "All":
    filtered = filtered[filtered["week"] == int(selected_week)]



# ----------------------------
# Build Game Results Function
# ----------------------------
def build_game_results(df):
    if "gameid" not in df.columns:
        st.error("❌ The CSV does not contain a 'gameid' column.")
        return pd.DataFrame()

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
if selected_week != "All":
    filtered = filtered[filtered["week"] == selected_week]


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

        # ----------------------------
        # Charts
        # ----------------------------
        st.subheader("📈 Charts")

        # Points per Game (scatter plot home vs away)
        fig, ax = plt.subplots()
        ax.scatter(results_df["Home Points"], results_df["Away Points"])
        ax.set_xlabel("Home Points")
        ax.set_ylabel("Away Points")
        ax.set_title("Points Scored in Games")
        st.pyplot(fig)

        # Spread Results (bar chart)
        if "Spread Result" in results_df.columns:
            spread_counts = results_df["Spread Result"].value_counts()
            fig, ax = plt.subplots()
            spread_counts.plot(kind="bar", ax=ax)
            ax.set_title("Spread Result Distribution")
            ax.set_ylabel("Count")
            st.pyplot(fig)

        # Over/Under Results (bar chart)
        if "O/U Result" in results_df.columns:
            ou_counts = results_df["O/U Result"].value_counts()
            fig, ax = plt.subplots()
            ou_counts.plot(kind="bar", ax=ax)
            ax.set_title("Over/Under Result Distribution")
            ax.set_ylabel("Count")
            st.pyplot(fig)

    else:
        st.warning("No results available for your selection.")










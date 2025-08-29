import streamlit as st
import pandas as pd

# =============================
# Load Dataset
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")

    # Normalize columns
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Handle naming variations
    rename_map = {
        "home": "home_team",
        "away": "away_team",
        "hometeam": "home_team",
        "awayteam": "away_team",
        "homepoints": "home_points",
        "awaypoints": "away_points",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    return df


df = load_data()
st.sidebar.write("Columns:", list(df.columns))


# =============================
# Streamlit App
# =============================
st.title("🏈 College Football Dashboard (2024 Season)")

if df.empty:
    st.warning("⚠️ No data loaded.")
    st.stop()

# Sidebar filters
weeks = sorted(df["week"].dropna().unique()) if "week" in df.columns else []

# ✅ Directly grab team names from both home & away columns
teams = sorted(
    pd.concat([df["home_team"].dropna(), df["away_team"].dropna()]).unique()
)

conferences = sorted(df["conference"].dropna().unique()) if "conference" in df.columns else []

week_choice = st.sidebar.selectbox("Select Week", ["All"] + list(map(str, weeks)))
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)
conf_choice = st.sidebar.selectbox("Select Conference", ["All"] + conferences)

# Apply filters
filtered = df.copy()

if week_choice != "All":
    filtered = filtered[filtered["week"] == int(week_choice)]

if team_choice != "All":
    filtered = filtered[
        (filtered["home_team"] == team_choice) | 
        (filtered["away_team"] == team_choice)
    ]

if conf_choice != "All":
    filtered = filtered[filtered["conference"] == conf_choice]

# =============================
# Display Data
# =============================
st.subheader("📊 Games")
st.dataframe(filtered)

# Win/Loss summary chart (only if points exist)
if not filtered.empty and "home_points" in filtered.columns and "away_points" in filtered.columns:
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



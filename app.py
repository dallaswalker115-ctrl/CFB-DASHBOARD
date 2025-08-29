import streamlit as st
import pandas as pd

# =============================
# Load Dataset (from CSV file)
# =============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cfb_2024_week6on_stats_with_lines.csv")
    except FileNotFoundError:
        st.error("❌ Could not find cfb_2024_week6on_stats_with_lines.csv in the repo.")
        return pd.DataFrame()
    
    # Normalize column names (lowercase, strip spaces)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

# =============================
# Streamlit App
# =============================
st.title("🏈 College Football Dashboard (2024 Season - From CSV)")

df = load_data()
if df.empty:
    st.stop()

# Sidebar filters
weeks = sorted(df["week"].dropna().unique()) if "week" in df.columns else []
teams = sorted(set(df.get("home_team", pd.Series([])).unique())
               .union(df.get("away_team", pd.Series([])).unique()))

week_choice = st.sidebar.selectbox("Select Week", ["All"] + list(map(str, weeks)))
team_choice = st.sidebar.selectbox("Select Team", ["All"] + teams)

filtered = df.copy()
if week_choice != "All" and "week" in filtered.columns:
    filtered = filtered[filtered["week"] == int(week_choice)]
if team_choice != "All":
    filtered = filtered[(filtered.get("home_team") == team_choice) | 
                        (filtered.get("away_team") == team_choice)]

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

import streamlit as st
import pandas as pd

st.set_page_config(page_title="IPL Analytics Dashboard", layout="wide")

st.title("🏏 IPL Advanced Analytics Dashboard")

# Load datasets
@st.cache_data
def load_data():
    matches = pd.read_csv("Match_Info.csv")
    deliveries = pd.read_csv("Ball_By_Ball_Match_Data.csv")
    return matches, deliveries

matches, deliveries = load_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Team Analysis",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "🏆 Leaderboards"
])

st.write("Deliveries Columns:")
st.write(deliveries.columns)

st.subheader("📊 Dataset Overview")

col1, col2 = st.columns(2)

with col1:
    st.write("Match Data Shape:", matches.shape)
    st.dataframe(matches.head())

with col2:
    st.write("Ball-by-Ball Data Shape:", deliveries.shape)
    st.dataframe(deliveries.head())

st.markdown("---")
with tab1:

    st.header("📊 Team Performance Analysis")

    # Select Team
    teams = matches['team1'].unique()
    selected_team = st.selectbox("Select Team", sorted(teams))

    # Total matches played
    matches_played = matches[
        (matches['team1'] == selected_team) |
        (matches['team2'] == selected_team)
    ]

    total_matches = matches_played.shape[0]

    # Total wins
    total_wins = matches_played[matches_played['winner'] == selected_team].shape[0]

    win_percentage = (total_wins / total_matches) * 100 if total_matches > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches Played", total_matches)
    col2.metric("Matches Won", total_wins)
    col3.metric("Win Percentage", f"{win_percentage:.2f}%")

    # Toss impact
    toss_wins = matches_played[matches_played['toss_winner'] == selected_team]
    toss_and_match_wins = toss_wins[toss_wins['winner'] == selected_team].shape[0]

    toss_win_rate = (toss_and_match_wins / toss_wins.shape[0]) * 100 if toss_wins.shape[0] > 0 else 0

    st.subheader("🎯 Toss Impact")
    st.write(f"When {selected_team} wins toss, match win rate: {toss_win_rate:.2f}%")

    # Batting first vs chasing
    bat_first = matches_played[
        ((matches_played['team1'] == selected_team) & (matches_played['toss_decision'] == 'bat')) |
        ((matches_played['team2'] == selected_team) & (matches_played['toss_decision'] == 'field'))
    ]

    bat_first_wins = bat_first[bat_first['winner'] == selected_team].shape[0]

    chasing = matches_played[
        ((matches_played['team1'] == selected_team) & (matches_played['toss_decision'] == 'field')) |
        ((matches_played['team2'] == selected_team) & (matches_played['toss_decision'] == 'bat'))
    ]

    chasing_wins = chasing[chasing['winner'] == selected_team].shape[0]

    st.subheader("🏏 Strategy Analysis")
    st.write(f"Wins while Batting First: {bat_first_wins}")
    st.write(f"Wins while Chasing: {chasing_wins}")


# -----------------------------
# PLAYER BATTING ANALYSIS
# -----------------------------
st.markdown("---")
with tab2:
    st.header("🏏 Player Batting Analysis")

    batsmen = deliveries['Batter'].dropna().unique()
    selected_batsman = st.selectbox("Select Batter", sorted(batsmen))

    player_data = deliveries[deliveries['Batter'] == selected_batsman].copy()

    matches_played_player = player_data['ID'].nunique() 

    player_data['BatsmanRun'] = pd.to_numeric(player_data['BatsmanRun'], errors='coerce')

    total_runs = player_data['BatsmanRun'].sum()

    if 'ExtraType' in player_data.columns:
        balls_faced = player_data[player_data['ExtraType'] != 'wides'].shape[0]
    else:
        balls_faced = player_data.shape[0]

    strike_rate = (total_runs / balls_faced) * 100 if balls_faced > 0 else 0

    fours = player_data[player_data['BatsmanRun'] == 4].shape[0]
    sixes = player_data[player_data['BatsmanRun'] == 6].shape[0]

    dismissals = player_data[player_data['PlayerOut'] == selected_batsman].shape[0]

    average = (total_runs / dismissals) if dismissals > 0 else total_runs



    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Matches Played", matches_played_player)
    col2.metric("Total Runs", int(total_runs))
    col3.metric("Strike Rate", f"{strike_rate:.2f}")
    col4.metric("Batting Average", f"{average:.2f}")

    st.write(f"Fours: {fours}")
    st.write(f"Sixes: {sixes}")
    st.write(f"Dismissals: {dismissals}")


# -----------------------------
# BOWLER ANALYSIS
# -----------------------------
st.markdown("---")
with tab3:
    st.header("🎯 Bowler Performance Analysis")

    bowlers = deliveries['Bowler'].dropna().unique()
    selected_bowler = st.selectbox("Select Bowler", sorted(bowlers))

    bowler_data = deliveries[deliveries['Bowler'] == selected_bowler].copy()

    matches_played_bowler = bowler_data['ID'].nunique()

    # Convert numeric columns
    bowler_data['TotalRun'] = pd.to_numeric(bowler_data['TotalRun'], errors='coerce')
    bowler_data['IsWicketDelivery'] = pd.to_numeric(bowler_data['IsWicketDelivery'], errors='coerce')

    # Total wickets
    total_wickets = bowler_data['IsWicketDelivery'].sum()

    # Total runs conceded
    runs_conceded = bowler_data['TotalRun'].sum()

    # Balls bowled (excluding wides & no balls)
    if 'ExtraType' in bowler_data.columns:
        legal_deliveries = bowler_data[
            (bowler_data['ExtraType'] != 'wides') &
            (bowler_data['ExtraType'] != 'noballs')
        ]
        balls_bowled = legal_deliveries.shape[0]
    else:
        balls_bowled = bowler_data.shape[0]

    # Overs
    overs = balls_bowled / 6

    # Economy
    economy = (runs_conceded / overs) if overs > 0 else 0

    # Dot balls
    dot_balls = bowler_data[bowler_data['TotalRun'] == 0].shape[0]
    dot_ball_percentage = (dot_balls / balls_bowled) * 100 if balls_bowled > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Matches Bowled", matches_played_bowler)
    col2.metric("Wickets", int(total_wickets))
    col3.metric("Economy Rate", f"{economy:.2f}")
    col4.metric("Dot Ball %", f"{dot_ball_percentage:.2f}")

    st.write(f"Runs Conceded: {int(runs_conceded)}")
    st.write(f"Overs Bowled: {overs:.2f}")


# -----------------------------
# TOP 10 RUN SCORERS
# -----------------------------
st.markdown("---")
with tab4:
    st.header("🏆 Top 10 Run Scorers")

    # Ensure numeric
    deliveries['BatsmanRun'] = pd.to_numeric(deliveries['BatsmanRun'], errors='coerce')

    top_batsmen = (
        deliveries
        .groupby('Batter')['BatsmanRun']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.dataframe(top_batsmen, use_container_width=True)

    import matplotlib.pyplot as plt

    st.subheader("📊 Top 10 Run Scorers - Visualization")

    fig, ax = plt.subplots()
    ax.bar(top_batsmen['Batter'], top_batsmen['BatsmanRun'])
    ax.set_xlabel("Player")
    ax.set_ylabel("Total Runs")
    ax.set_title("Top 10 Run Scorers")

    plt.xticks(rotation=45)
    st.pyplot(fig)



    # -----------------------------
    # TOP 10 WICKET TAKERS
    # -----------------------------
    st.markdown("---")
    st.header("🎯 Top 10 Wicket Takers")

    deliveries['IsWicketDelivery'] = pd.to_numeric(deliveries['IsWicketDelivery'], errors='coerce')

    top_bowlers = (
        deliveries
        .groupby('Bowler')['IsWicketDelivery']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.dataframe(top_bowlers, use_container_width=True)

    import matplotlib.pyplot as plt

    st.subheader("📊 Top 10 Wicket Takers - Visualization")

    fig2, ax2 = plt.subplots()
    ax2.bar(top_bowlers['Bowler'], top_bowlers['IsWicketDelivery'])
    ax2.set_xlabel("Player")
    ax2.set_ylabel("Total Wickets")
    ax2.set_title("Top 10 Wicket Takers")

    plt.xticks(rotation=50)
    st.pyplot(fig)
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

st.write(deliveries.columns)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Team Analysis",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "🏆 Leaderboards"
])

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


 

    # PHASE-WISE ANALYSIS
    # -----------------------------
    st.markdown("---")
    st.subheader("📊 Phase-wise Performance")

    # Convert Overs to numeric
    player_data['Overs'] = pd.to_numeric(player_data['Overs'], errors='coerce')

    # Powerplay (1-6)
    powerplay = player_data[player_data['Overs'] <= 6]
    powerplay_runs = powerplay['BatsmanRun'].sum()

    # Middle Overs (7-15)
    middle = player_data[(player_data['Overs'] >= 7) & (player_data['Overs'] <= 15)]
    middle_runs = middle['BatsmanRun'].sum()

    # Death Overs (16-20)
    death = player_data[player_data['Overs'] >= 16]
    death_runs = death['BatsmanRun'].sum()

    # Death strike rate
    death_balls = death.shape[0]
    death_strike_rate = (death_runs / death_balls) * 100 if death_balls > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Powerplay Runs (1-6)", int(powerplay_runs))
    col2.metric("Middle Overs Runs (7-15)", int(middle_runs))
    col3.metric("Death Overs Runs (16-20)", int(death_runs))
    col4.metric("Death Strike Rate", f"{death_strike_rate:.2f}")

    import matplotlib.pyplot as plt

    st.subheader("📈 Phase Comparison Chart")

    phases = ["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"]
    runs = [powerplay_runs, middle_runs, death_runs]

    fig, ax = plt.subplots()
    ax.bar(phases, runs)
    ax.set_ylabel("Total Runs")
    ax.set_title("Runs by Match Phase")

    st.pyplot(fig)



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
    # PHASE-WISE BOWLING ANALYSIS
    # -----------------------------
    st.markdown("---")
    st.subheader("📊 Phase-wise Bowling Performance")

    # Convert Overs to numeric
    bowler_data['Overs'] = pd.to_numeric(bowler_data['Overs'], errors='coerce')

    # -------- Powerplay (1-6) --------
    powerplay = bowler_data[bowler_data['Overs'] <= 6]
    pp_wickets = powerplay['IsWicketDelivery'].sum()
    pp_runs = powerplay['TotalRun'].sum()
    pp_balls = powerplay.shape[0]
    pp_overs = pp_balls / 6
    pp_economy = (pp_runs / pp_overs) if pp_overs > 0 else 0

    # -------- Middle Overs (7-15) --------
    middle = bowler_data[(bowler_data['Overs'] >= 7) & (bowler_data['Overs'] <= 15)]
    mid_wickets = middle['IsWicketDelivery'].sum()
    mid_runs = middle['TotalRun'].sum()
    mid_balls = middle.shape[0]
    mid_overs = mid_balls / 6
    mid_economy = (mid_runs / mid_overs) if mid_overs > 0 else 0

    # -------- Death Overs (16-20) --------
    death = bowler_data[bowler_data['Overs'] >= 16]
    death_wickets = death['IsWicketDelivery'].sum()
    death_runs = death['TotalRun'].sum()
    death_balls = death.shape[0]
    death_overs = death_balls / 6
    death_economy = (death_runs / death_overs) if death_overs > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Powerplay Economy", f"{pp_economy:.2f}")
    col2.metric("Middle Overs Economy", f"{mid_economy:.2f}")
    col3.metric("Death Economy", f"{death_economy:.2f}")

    col4, col5, col6 = st.columns(3)

    col4.metric("PP Wickets", int(pp_wickets))
    col5.metric("Middle Wickets", int(mid_wickets))
    col6.metric("Death Wickets", int(death_wickets))

    # -----------------------------
# BOWLING PHASE CHART
# -----------------------------
# -----------------------------
# BOWLING PHASE WICKETS CHART
# -----------------------------
    st.markdown("---")
    st.subheader("📈 Wickets by Match Phase")

    import matplotlib.pyplot as plt

    phases = ["Powerplay", "Middle", "Death"]
    wickets = [pp_wickets, mid_wickets, death_wickets]

    fig, ax = plt.subplots()
    ax.bar(phases, wickets)
    ax.set_ylabel("Total Wickets")
    ax.set_title("Wickets by Match Phase")

    st.pyplot(fig)

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
        .head(11)
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
        .head(11)
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
    st.pyplot(fig2)

  


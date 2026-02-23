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



tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Team Analysis",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "🏆 Batters Leaderboards",
    "🏆 Bowlers Leaderboards",
    "🔥 Match-up Analysis"
])

st.markdown("---")
with tab1:
    

    st.header("📊 Team Performance Analysis")

    # Select Team
    teams = pd.concat([matches['team1'], matches['team2']]).unique()
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
    # CONSISTENCY INDEX
    # -----------------------------
    st.markdown("---")
    st.subheader("📊 Consistency Analysis")

    # Runs per match
    runs_per_match = (
        player_data
        .groupby('ID')['BatsmanRun']
        .sum()
    )

    if runs_per_match.shape[0] > 1:

        mean_runs = runs_per_match.mean()
        std_runs = runs_per_match.std()

        # Coefficient of Variation (CV)
        cv = (std_runs / mean_runs) if mean_runs > 0 else 0

        # Convert to consistency score (higher = better)
        consistency_index = (1 - cv) * 100 if cv < 1 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Average Runs per Match", f"{mean_runs:.2f}")
        col2.metric("Std Deviation", f"{std_runs:.2f}")
        col3.metric("Consistency Index (%)", f"{consistency_index:.2f}")

    else:
        st.info("Not enough matches to calculate consistency.")

        # -----------------------------
# BATTING IMPACT RATING
# -----------------------------
    st.markdown("---")
    st.subheader("🔥 Batting Impact Rating")

    if matches_played_player > 0:

        avg_runs = total_runs / matches_played_player

        boundary_runs = (fours * 4) + (sixes * 6)
        boundary_percentage = (boundary_runs / total_runs) if total_runs > 0 else 0

        impact_score = (
            0.5 * avg_runs +
            0.3 * (strike_rate / 100 * 50) +
            0.2 * (boundary_percentage * 100)
        )

        st.metric("Batting Impact Score", f"{impact_score:.2f} / 100")

    else:
        st.info("Not enough data to calculate impact.")


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
    # BOWLER CONSISTENCY INDEX
    # -----------------------------
    st.markdown("---")
    st.subheader("📊 Bowling Consistency Analysis")

    wickets_per_match = (
        bowler_data
        .groupby('ID')['IsWicketDelivery']
        .sum()
    )

    if wickets_per_match.shape[0] > 1:

        mean_wkts = wickets_per_match.mean()
        std_wkts = wickets_per_match.std()

        cv_wkts = (std_wkts / mean_wkts) if mean_wkts > 0 else 0

        consistency_index = (1 - cv_wkts) * 100 if cv_wkts < 1 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Avg Wickets per Match", f"{mean_wkts:.2f}")
        col2.metric("Std Deviation", f"{std_wkts:.2f}")
        col3.metric("Consistency Index (%)", f"{consistency_index:.2f}")

    else:
        st.info("Not enough matches to calculate consistency.")
        


            # -----------------------------
    # BOWLING IMPACT RATING
    # -----------------------------
    st.markdown("---")
    st.subheader("🔥 Bowling Impact Rating")

    if matches_played_bowler > 0:

        avg_wickets = total_wickets / matches_played_bowler

        # Economy inverse (lower economy = better score)
        economy_score = max(0, 10 - economy)  # scale around T20 avg economy

        impact_score = (
            0.5 * (avg_wickets * 20) +      # Wickets weight
            0.3 * (economy_score * 10) +    # Economy weight
            0.2 * dot_ball_percentage       # Dot ball weight
        )

        # Cap to 100
        impact_score = min(100, impact_score)

        st.metric("Bowling Impact Score", f"{impact_score:.2f} / 100")

    else:
        st.info("Not enough data to calculate impact.")

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
with tab5:
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
    st.pyplot(fig2)


    # -----------------------------
# MATCH-UP ANALYSIS TAB
# -----------------------------
st.markdown("---")
with tab6:
    st.header("🔥 Batter vs Bowler Match-up Analysis")

    batters = deliveries['Batter'].dropna().unique()
    selected_batter = st.selectbox(
    "Select Batter",
    sorted(batters),
    key="matchup_batter"
)

    # Show only bowlers who bowled to this batter
    bowlers_list = deliveries[
        deliveries['Batter'] == selected_batter
    ]['Bowler'].dropna().unique()

    selected_bowler = st.selectbox(
    "Select Bowler",
    sorted(bowlers_list),
    key="matchup_bowler"
)
    matchup_data = deliveries[
        (deliveries['Batter'] == selected_batter) &
        (deliveries['Bowler'] == selected_bowler)
    ].copy()

    if matchup_data.shape[0] > 0:

        matchup_data['BatsmanRun'] = pd.to_numeric(matchup_data['BatsmanRun'], errors='coerce')
        matchup_data['IsWicketDelivery'] = pd.to_numeric(matchup_data['IsWicketDelivery'], errors='coerce')

        total_runs = matchup_data['BatsmanRun'].sum()
        balls = matchup_data.shape[0]

        strike_rate = (total_runs / balls) * 100 if balls > 0 else 0

        dismissals = matchup_data[
            (matchup_data['IsWicketDelivery'] == 1) &
            (matchup_data['PlayerOut'] == selected_batter)
        ].shape[0]

        average = (total_runs / dismissals) if dismissals > 0 else total_runs

        fours = matchup_data[matchup_data['BatsmanRun'] == 4].shape[0]
        sixes = matchup_data[matchup_data['BatsmanRun'] == 6].shape[0]

        dot_balls = matchup_data[matchup_data['BatsmanRun'] == 0].shape[0]
        dot_percentage = (dot_balls / balls) * 100 if balls > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Runs Scored", int(total_runs))
        col2.metric("Balls Faced", balls)
        col3.metric("Strike Rate", f"{strike_rate:.2f}")
        col4.metric("Dismissals", dismissals)

        col5, col6, col7 = st.columns(3)
        col5.metric("Average", f"{average:.2f}")
        col6.metric("Fours / Sixes", f"{fours} / {sixes}")
        col7.metric("Dot Ball %", f"{dot_percentage:.2f}")

    else:
        st.info("No match-up data available.")





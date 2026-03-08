
# ---------------------------------------------
# IPL Advanced Analytics Dashboard
# ---------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go




# Page configuration
st.set_page_config(
    page_title="IPL Predictive Analytics & Match Intelligence Dashboard",
    page_icon="🏏",
    layout="wide"
)


# ---------------------------------------------
# Load Machine Learning Models
# ---------------------------------------------

model = pickle.load(open("models/win_predictor.pkl", "rb"))
score_model = pickle.load(open("models/final_score_model.pkl", "rb"))


# ---------------------------------------------
# Dashboard Title
# ---------------------------------------------

st.title("🏏 IPL Predictive Analytics & Match Intelligence Dashboard")

st.markdown("""
This dashboard explores **Indian Premier League match data** using  
**advanced analytics and predictive modeling**.

Features included:

• Team performance analysis  
• Player batting and bowling analytics  
• Venue based match insights  
• Match win probability prediction  
• Final score prediction  
• Batter vs Bowler matchup analysis
""")


# ---------------------------------------------
# Load Dataset
# ---------------------------------------------

@st.cache_data
def load_data():
    matches = pd.read_csv("data/Match_Info.csv")
    deliveries = pd.read_csv("data/Ball_By_Ball_Match_Data.csv")
    return matches, deliveries


matches, deliveries = load_data()


# ---------------------------------------------
# Clean Venue Names
# ---------------------------------------------

matches['venue'] = matches['venue'].str.lower()
matches['venue'] = matches['venue'].str.replace(',.*', '', regex=True)
matches['venue'] = matches['venue'].str.replace('.', ' ', regex=False)
matches['venue'] = matches['venue'].str.replace('\s+', ' ', regex=True).str.strip()
matches['venue'] = matches['venue'].str.title()


# ---------------------------------------------
# Main Dashboard Sections
# ---------------------------------------------

main_tab1, main_tab2 = st.tabs([
    "📊 Historical Analytics",
    "🔮 Predictive Analytics"
])


# ---------------------------------------------
# Historical Analytics
# ---------------------------------------------

with main_tab1:

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Team Analysis",
        "🏏 Batting Analysis",
        "🎯 Bowling Analysis",
        "🏆 Batters Leaderboards",
        "🏆 Bowlers Leaderboards",
        "🏟️ Venue Analysis",
        "🧤 Fielding Analysis"
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
# VENUE ANALYSIS
# -----------------------------
st.markdown("---")

with tab6:

    st.header("🏟️ Venue Analysis")

    venues = matches['venue'].dropna().unique()

    selected_venue = st.selectbox("Select Venue", sorted(venues))

    venue_matches = matches[matches['venue'] == selected_venue]

    total_matches = venue_matches.shape[0]

    batting_first_wins = venue_matches[
        venue_matches['toss_decision'] == 'bat'
    ]['winner'].count()

    chasing_wins = venue_matches[
        venue_matches['toss_decision'] == 'field'
    ]['winner'].count()

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches Played", total_matches)
    col2.metric("Batting First Wins", batting_first_wins)
    col3.metric("Chasing Wins", chasing_wins)

    # -----------------------------
    # Average Score at Venue
    # -----------------------------

    venue_match_ids = venue_matches['match_number'].unique()

    venue_deliveries = deliveries[
        deliveries['ID'].isin(venue_match_ids)
    ]

    venue_deliveries['TotalRun'] = pd.to_numeric(
        venue_deliveries['TotalRun'], errors='coerce'
    )

    match_scores = (
        venue_deliveries
        .groupby(['ID','Innings'])['TotalRun']
        .sum()
        .reset_index()
    )

    avg_score = match_scores['TotalRun'].mean()

    st.metric("Average Innings Score", f"{avg_score:.2f}")
# -----------------------------
# FIELDING & WICKETKEEPING ANALYSIS
# -----------------------------
with tab7:

    st.header("🧤 Fielding & Wicketkeeping Analysis")

    

    # Remove rows without fielders
    fielding_data = deliveries.dropna(subset=['FieldersInvolved']).copy()

    # Split multiple fielders
    fielding_data['FieldersInvolved'] = fielding_data['FieldersInvolved'].str.split(',')
    fielding_data = fielding_data.explode('FieldersInvolved')
    fielding_data['FieldersInvolved'] = fielding_data['FieldersInvolved'].str.strip()

    # -----------------------------
    # Identify Wicketkeepers
    # -----------------------------
    stumpings = fielding_data[fielding_data['Kind'] == 'stumped']

    wk_players = stumpings['FieldersInvolved'].unique()

    # -----------------------------
    # Separate WK vs Fielders
    # -----------------------------
    wk_events = fielding_data[fielding_data['FieldersInvolved'].isin(wk_players)]
    fielder_events = fielding_data[~fielding_data['FieldersInvolved'].isin(wk_players)]

    # =====================================================
    # 🧤 WICKETKEEPING ANALYSIS
    # =====================================================
    st.subheader("🧤 Wicketkeeping Performance")

    wk_catches = wk_events[wk_events['Kind'] == 'caught']

    wk_catches_table = (
        wk_catches
        .groupby('FieldersInvolved')
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name='WK Catches')
    )

    wk_runouts = wk_events[wk_events['Kind'] == 'run out']

    wk_runouts_table = (
        wk_runouts
        .groupby('FieldersInvolved')
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name='WK Run Outs')
    )

    wk_stumpings_table = (
        stumpings
        .groupby('FieldersInvolved')
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name='Stumpings')
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Top WK Catches")
        st.dataframe(wk_catches_table, use_container_width=True)

    with col2:
        st.write("WK Run Outs")
        st.dataframe(wk_runouts_table, use_container_width=True)

    with col3:
        st.write("Stumpings")
        st.dataframe(wk_stumpings_table, use_container_width=True)

    # =====================================================
    # 🏃 FIELDING ANALYSIS
    # =====================================================
    st.subheader("🏃 Fielding Performance")

    fielder_catches = fielder_events[fielder_events['Kind'] == 'caught']

    top_fielder_catches = (
        fielder_catches
        .groupby('FieldersInvolved')
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name='Catches')
    )

    fielder_runouts = fielder_events[fielder_events['Kind'] == 'run out']

    top_fielder_runouts = (
        fielder_runouts
        .groupby('FieldersInvolved')
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name='Run Outs')
    )

    col4, col5 = st.columns(2)

    with col4:
        st.write("Top Fielding Catches")
        st.dataframe(top_fielder_catches, use_container_width=True)

    with col5:
        st.write("Fielding Run Outs")
        st.dataframe(top_fielder_runouts, use_container_width=True)


with main_tab2:

    st.header("🔮 Match Prediction Center")

    predictor_tab1, predictor_tab2, predictor_tab3 = st.tabs([
    "🏆 Win Probability Predictor",
    "🎯 Final Score Predictor",
    "📈 Future Models"
])
with predictor_tab1:

    with st.container():

        st.header("🏆 IPL Win Probability Predictor")

        st.subheader("Match Setup")

        col_team1, col_team2 = st.columns(2)

        with col_team1:
            batting_team = st.selectbox(
                "Batting Team",
                teams,
                key="batting_team_predictor"
            )

        with col_team2:
            bowling_team = st.selectbox(
                "Bowling Team",
                teams,
                key="bowling_team_predictor"
            )

        # -----------------------------
        # Head to Head Record
        # -----------------------------
        if batting_team != bowling_team:

            head_to_head = matches[
                ((matches['team1'] == batting_team) & (matches['team2'] == bowling_team)) |
                ((matches['team1'] == bowling_team) & (matches['team2'] == batting_team))
            ]

            total_matches = head_to_head.shape[0]

            batting_team_wins = head_to_head[
                head_to_head['winner'] == batting_team
            ].shape[0]

            bowling_team_wins = head_to_head[
                head_to_head['winner'] == bowling_team
            ].shape[0]

            st.subheader("Head-to-Head Record")

            col_h1, col_h2, col_h3 = st.columns(3)

            col_h1.metric("Matches Played", total_matches)
            col_h2.metric(f"{batting_team} Wins", batting_team_wins)
            col_h3.metric(f"{bowling_team} Wins", bowling_team_wins)

        st.divider()

        st.markdown("Enter the current match situation to estimate the chasing team's chances of winning.")

        col1, col2 = st.columns(2)

        with col1:
            target = st.number_input("Target Score", min_value=1, value=180)

            overs = st.number_input(
                "Overs Completed",
                min_value=0.1,
                max_value=19.5,
                value=10.0,
                step=0.1
            )

        with col2:
            score = st.number_input("Current Score", min_value=0, value=90)

            wickets = st.number_input(
                "Wickets Fallen",
                min_value=0,
                max_value=10,
                value=2
            )

        predict = st.button("Predict Win Probability", use_container_width=True)

        if predict:

            runs_left = target - score
            balls_left = 120 - (overs * 6)
            wickets_left = 10 - wickets

            if balls_left <= 0:
                st.error("Match already finished!")

            else:

                # Run rate calculations
                crr = score / overs if overs > 0 else 0
                rrr = runs_left / (balls_left / 6)

                progress = (score / target) * 100

                st.markdown(
                    f"""
                    ### 🏏 Match Scenario

                    **{batting_team} vs {bowling_team}**

                    Target: **{target}**

                    Current Score: **{score}/{wickets}**

                    Overs Completed: **{overs}**
                    """
                )

                st.divider()

                # Match Pressure
                st.subheader("Match Pressure")

                col_p1, col_p2 = st.columns(2)

                with col_p1:
                    st.metric("Runs Needed", runs_left)

                with col_p2:
                    st.metric("Balls Remaining", int(balls_left))

                st.divider()

                # Run Rate Analysis
                st.subheader("Run Rate Analysis")

                col_rr1, col_rr2 = st.columns(2)

                with col_rr1:
                    st.info(f"Current Run Rate (CRR)\n\n{crr:.2f}")

                with col_rr2:
                    st.warning(f"Required Run Rate (RRR)\n\n{rrr:.2f}")

                st.divider()

                # Chase Progress
                st.subheader("Chase Progress")

                st.progress(progress / 100)

                st.caption(f"{score} runs scored out of {target} target ({progress:.1f}%)")

                st.divider()

                # -----------------------------
                # Historical Strength
                # -----------------------------
                head_to_head = matches[
                    ((matches['team1'] == batting_team) & (matches['team2'] == bowling_team)) |
                    ((matches['team1'] == bowling_team) & (matches['team2'] == batting_team))
                ]

                total_matches = head_to_head.shape[0]

                batting_team_wins = head_to_head[
                    head_to_head['winner'] == batting_team
                ].shape[0]

                if total_matches > 0:
                    historical_strength = batting_team_wins / total_matches
                else:
                    historical_strength = 0.5

                # -----------------------------
                # ML Prediction
                # -----------------------------
                input_data = np.array([[runs_left, balls_left, wickets_left, crr, rrr]])

                prediction = model.predict_proba(input_data)

                base_win_prob = prediction[0][1]

                # Combine ML + historical strength
                adjusted_win_prob = (base_win_prob * 0.8) + (historical_strength * 0.2)

                win_prob = adjusted_win_prob * 100
                lose_prob = 100 - win_prob

# -----------------------------
                # Prediction Visualization
                # -----------------------------
                st.subheader("🏆 Match Winning Probability")

                import plotly.graph_objects as go

                # Decide colors based on probability
                if win_prob > lose_prob:
                    colors = ["green", "red"]
                else:
                    colors = ["red", "green"]

                # Create bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=[batting_team, bowling_team],
                        y=[win_prob, lose_prob],
                        text=[f"{win_prob:.2f}%", f"{lose_prob:.2f}%"],
                        textposition="auto",
                        marker_color=colors
                    )
                ])

                fig.update_layout(
                    title="Predicted Match Winning Probability",
                    yaxis_title="Probability (%)",
                    xaxis_title="Teams"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Decide gauge color based on probability
                if win_prob < 40:
                    gauge_color = "red"
                elif win_prob < 60:
                    gauge_color = "yellow"
                else:
                    gauge_color = "green"

                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=win_prob,
                    title={'text': f"{batting_team} Win Probability"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': gauge_color},
                        'steps': [
                            {'range': [0, 40], 'color': "#ffcccc"},
                            {'range': [40, 60], 'color': "#fff2cc"},
                            {'range': [60, 100], 'color': "#ccffcc"}
                        ]
                    }
                ))


                

                                # -----------------------------
                # Match Pressure Indicator
                # -----------------------------
                st.subheader("Match Pressure Indicator")

                pressure = rrr - crr

                if pressure <= 0:
                    st.success("🟢 LOW PRESSURE – Batting team is comfortable")
                elif pressure <= 2:
                    st.warning("🟡 MEDIUM PRESSURE – Match is balanced")
                else:
                    st.error("🔴 HIGH PRESSURE – Bowling team has advantage")

                st.plotly_chart(gauge_fig, use_container_width=True)

                st.subheader("Prediction Result")

                col3, col4 = st.columns(2)

                st.subheader("🏆 Match Winning Probability")

                st.write(batting_team)
                st.progress(win_prob/100)

                st.write(bowling_team)
                st.progress(lose_prob/100)

                st.write(f"{batting_team}: {win_prob:.2f}%")
                st.write(f"{bowling_team}: {lose_prob:.2f}%")



with predictor_tab2:

    st.header("🎯 Final Score Predictor")

    col1, col2, col3 = st.columns(3)

    with col1:
        current_score = st.number_input("Current Score", value=80)

    with col2:
        overs = st.number_input("Overs Completed", value=10.0)

    with col3:
        wickets = st.number_input("Wickets Fallen", value=2)

    runs_last_5 = st.number_input("Runs in Last 5 Overs", value=40)
    wkts_last_5 = st.number_input("Wickets in Last 5 Overs", value=1)

    if st.button("Predict Final Score"):

        input_data = np.array([[current_score, overs, wickets, runs_last_5, wkts_last_5]])

        prediction = score_model.predict(input_data)

        predicted_score = int(prediction[0])

        st.divider()

        st.markdown("### 🧠 Predicted Final Score")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Predicted Score", predicted_score)

        with col_b:
            st.metric("Minimum Expected", predicted_score - 15)

        with col_c:
            st.metric("Maximum Expected", predicted_score + 15)

        st.divider()

        st.subheader("Projected Score Range")

        score_progress = predicted_score / 250

        st.progress(score_progress)

        st.caption(f"Projected IPL Score: {predicted_score} runs")


with predictor_tab3:

    st.subheader("⚔️ Batter vs Bowler Predictor")

    batters = deliveries['Batter'].dropna().unique()
    bowlers = deliveries['Bowler'].dropna().unique()

    colA, colB = st.columns(2)

    with colA:
        batter = st.selectbox(
            "Select Batter",
            sorted(batters),
            key="predictor_batter"
        )

    with colB:
        bowler = st.selectbox(
            "Select Bowler",
            sorted(bowlers),
            key="predictor_bowler"
        )

    # Matchup Header (NEW UI IMPROVEMENT)
    st.markdown(f"## 🏏 {batter} vs {bowler}")
    st.divider()

    matchup_data = deliveries[
        (deliveries['Batter'] == batter) &
        (deliveries['Bowler'] == bowler)
    ].copy()

    if matchup_data.shape[0] > 0:

        matchup_data['BatsmanRun'] = pd.to_numeric(matchup_data['BatsmanRun'], errors='coerce')
        matchup_data['IsWicketDelivery'] = pd.to_numeric(matchup_data['IsWicketDelivery'], errors='coerce')

        # Remove wides
        legal_balls = matchup_data[matchup_data['ExtraType'] != 'wides']

        runs = legal_balls['BatsmanRun'].sum()
        balls = legal_balls.shape[0]

        dot = legal_balls[legal_balls['BatsmanRun'] == 0].shape[0]
        ones = legal_balls[legal_balls['BatsmanRun'] == 1].shape[0]
        twos = legal_balls[legal_balls['BatsmanRun'] == 2].shape[0]
        fours = legal_balls[legal_balls['BatsmanRun'] == 4].shape[0]
        sixes = legal_balls[legal_balls['BatsmanRun'] == 6].shape[0]

        wickets = legal_balls[
            (legal_balls['IsWicketDelivery'] == 1) &
            (legal_balls['PlayerOut'] == batter)
        ].shape[0]

        dot_p = (dot / balls) * 100 if balls > 0 else 0
        one_p = (ones / balls) * 100 if balls > 0 else 0
        two_p = (twos / balls) * 100 if balls > 0 else 0
        four_p = (fours / balls) * 100 if balls > 0 else 0
        six_p = (sixes / balls) * 100 if balls > 0 else 0
        wicket_p = (wickets / balls) * 100 if balls > 0 else 0

        strike_rate = (runs / balls) * 100 if balls > 0 else 0
        dismissals = wickets
        average = runs / dismissals if dismissals > 0 else runs

        dot_percentage = (dot / balls) * 100 if balls > 0 else 0
        expected_runs = runs / balls if balls > 0 else 0
        dismissal_prob = (dismissals / balls) * 100 if balls > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Runs Scored", int(runs))
        col2.metric("Balls Faced", balls)
        col3.metric("Strike Rate", f"{strike_rate:.2f}")
        col4.metric("Dismissals", dismissals)

        col5, col6, col7 = st.columns(3)

        col5.metric("Average", f"{average:.2f}")
        col6.metric("Fours / Sixes", f"{fours} / {sixes}")
        col7.metric("Dot Ball %", f"{dot_percentage:.2f}")

        st.divider()

        st.subheader("Prediction Indicators")

        col8, col9 = st.columns(2)

        col8.metric("Expected Runs / Ball", f"{expected_runs:.2f}")
        col9.metric("Dismissal Probability", f"{dismissal_prob:.2f}%")

        st.divider()

        st.subheader("Ball Outcome Probability")

        outcome_df = pd.DataFrame({
            "Outcome": ["Dot Ball", "1 Run", "2 Runs", "Four", "Six", "Wicket"],
            "Probability": [dot_p, one_p, two_p, four_p, six_p, wicket_p]
        })

        fig = px.bar(
            outcome_df,
            x="Outcome",
            y="Probability",
            text="Probability",
            color="Outcome",
            title=f"{batter} vs {bowler} Ball Outcome Prediction"
        )

        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.warning("No historical matchup data available.")

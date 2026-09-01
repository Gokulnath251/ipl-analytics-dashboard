import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# IPL HISTORICAL ANALYTICS
# Data: IPL 2007/08 - 2026
# ============================================================

st.set_page_config(
    page_title="IPL Historical Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
.stApp { background: #0b1220; }
.block-container {
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(135deg, #111e33, #0d1728);
    border: 1px solid #29405f;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 18px;
}
.hero-label {
    color: #62a9ff !important;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
}
.hero-title {
    color: #ffffff !important;
    font-size: 38px;
    font-weight: 800;
    margin-top: 4px;
}
.hero-subtitle {
    color: #b9d0ed !important;
    font-size: 15px;
    margin-top: 6px;
}
.section-title {
    color: #ffffff !important;
    font-size: 25px;
    font-weight: 750;
    margin-top: 18px;
    margin-bottom: 13px;
}
.metric-card {
    background: #111e33;
    border: 1px solid #29405f;
    border-radius: 14px;
    padding: 16px;
    min-height: 105px;
}
.metric-label {
    color: #a9c7ee !important;
    font-size: 13px;
}
.metric-value {
    color: #ffffff !important;
    font-size: 28px;
    font-weight: 750;
    margin-top: 7px;
}
p, label { color: #e8eef7 !important; }
h1, h2, h3 { color: #ffffff !important; }
button[data-baseweb="tab"] { color: #e8eef7 !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
}
div[data-baseweb="select"] * { color: #18253a !important; }
div[data-testid="stDataFrame"] { border-radius: 10px; }

.nav-note { color: #8fa8c7; font-size: 12px; margin-top: -8px; }
div[role="radiogroup"] { gap: 4px; flex-wrap: wrap; }
div[role="radiogroup"] label {
    background: #111e33; border: 1px solid #29405f; border-radius: 8px;
    padding: 7px 10px; margin: 0;
}
div[role="radiogroup"] label:has(input:checked) {
    border-color: #ff4b4b; background: #18253a;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_data():
    matches = pd.read_csv(
        "data/Match_Info.csv",
        dtype=str
    ).fillna("")

    balls = pd.read_csv(
        "data/Ball_By_Ball_Match_Data.csv",
        dtype=str
    ).fillna("")

    matches = matches.rename(columns={
        "match_id": "ID",
        "season": "Season",
        "date": "Date",
        "venue": "Venue",
        "city": "City",
        "team1": "Team1",
        "team2": "Team2",
        "winner": "Winner",
        "toss_winner": "TossWinner",
        "toss_decision": "TossDecision",
        "player_of_match": "PlayerOfMatch",
    })

    for col in [
        "Innings", "BatsmanRun", "TotalRun", "Wides",
        "NoBalls", "Byes", "LegByes", "Penalty",
        "IsWicketDelivery"
    ]:
        if col in balls.columns:
            balls[col] = pd.to_numeric(
                balls[col], errors="coerce"
            ).fillna(0)

    return matches, balls


try:
    matches, balls = load_data()
except Exception as e:
    st.error(f"Unable to load IPL data: {e}")
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def fmt(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_teams(df):
    teams = set()
    for col in ["Team1", "Team2"]:
        if col in df.columns:
            teams.update(
                df[col].astype(str).str.strip().tolist()
            )
    return sorted(t for t in teams if t)


def get_players(df, col):
    if col not in df.columns:
        return []
    return sorted(
        str(x).strip()
        for x in df[col].dropna().unique()
        if str(x).strip()
    )


def team_strategy_summary(match_df, ball_df, team):
    """Return batting-first vs chasing record for one team."""
    if "BattingTeam" not in ball_df.columns or "Innings" not in ball_df.columns:
        return pd.DataFrame()

    team_balls = ball_df[ball_df["BattingTeam"] == team].copy()
    rows = []

    for match_id, group in team_balls.groupby("ID"):
        match_row = match_df[match_df["ID"].astype(str) == str(match_id)]
        if match_row.empty:
            continue

        innings = sorted(group["Innings"].dropna().unique())
        if not innings:
            continue

        first_innings = innings[0]
        situation = (
            "Batting First" if first_innings == 1
            else "Chasing" if first_innings == 2
            else None
        )

        if situation:
            rows.append({
                "Situation": situation,
                "Won": match_row.iloc[0]["Winner"] == team
            })

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .groupby("Situation")["Won"]
        .agg(Matches="count", Wins="sum")
        .reset_index()
        .assign(
            Losses=lambda d: d["Matches"] - d["Wins"],
            **{"Win %": lambda d: (d["Wins"] / d["Matches"] * 100).round(2)}
        )
    )


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-label">IPL • MATCH INTELLIGENCE</div>
    <div class="hero-title">🏏 IPL Historical Analytics</div>
    <div class="hero-subtitle">
        Explore IPL history from 2007/08 through 2026 using
        match-level and ball-by-ball data.
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SEASON FILTER
# ============================================================

seasons = sorted(
    matches["Season"].dropna().unique(),
    key=str
)

selected_season = st.selectbox(
    "📅 Select Season",
    ["All Seasons"] + list(seasons)
)

if selected_season == "All Seasons":
    fm = matches.copy()
    fb = balls.copy()
else:
    fm = matches[matches["Season"] == selected_season].copy()
    fb = balls[balls["Season"] == selected_season].copy()


# ============================================================
# NAVIGATION
# ============================================================

# Use a stateful horizontal navigation control instead of st.tabs().
# Streamlit reruns the script whenever a selectbox changes; st.tabs()
# does not preserve the active tab across those reruns, which caused
# the app to jump back to Team Analysis.
nav_options = [
    "📊 Team Analysis",
    "⚔️ Team Head-to-Head",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "⚔️ Player Head-to-Head",
    "🏆 Batters Leaderboards",
    "🏆 Bowlers Leaderboards",
    "🏟️ Venue Analysis",
    "🤜 Fielding Analysis",
    "🔥 Recent Form",
    "🪙 Toss Analysis",
]

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = nav_options[0]

active_tab = st.radio(
    "Navigation",
    nav_options,
    key="active_tab",
    horizontal=True,
    label_visibility="collapsed",
)


# ============================================================
# TEAM ANALYSIS
# ============================================================

if active_tab == "📊 Team Analysis":

    st.markdown(
        '<div class="section-title">📊 Team Performance Analysis</div>',
        unsafe_allow_html=True
    )

    teams = get_teams(fm)

    if teams:

        selected_team = st.selectbox(
            "Select Team",
            ["All Teams"] + teams,
            key="team_selector"
        )

        if selected_team == "All Teams":

            rows = []

            for team in teams:
                tm = fm[
                    (fm["Team1"] == team)
                    | (fm["Team2"] == team)
                ]

                played = len(tm)
                wins = (tm["Winner"] == team).sum()

                rows.append({
                    "Team": team,
                    "Matches Played": played,
                    "Matches Won": int(wins),
                    "Win %": round(
                        wins / played * 100, 2
                    ) if played else 0
                })

            table = pd.DataFrame(rows).sort_values(
                ["Matches Won", "Win %"],
                ascending=False
            )

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True
            )

            fig = px.bar(
                table.sort_values("Matches Won"),
                x="Matches Won",
                y="Team",
                orientation="h",
                title="Matches Won"
            )
            st.plotly_chart(fig, use_container_width=True)

            # --------------------------------------------------------
            # NEW: Chasing vs Batting-First comparison across all teams
            # --------------------------------------------------------
            st.markdown(
                '<div class="section-title">🏏 Batting First vs Chasing — All Teams</div>',
                unsafe_allow_html=True
            )

            strategy_rows = []

            for team in teams:
                strategy = team_strategy_summary(fm, fb, team)
                if strategy.empty:
                    continue

                row = {"Team": team}
                for _, r in strategy.iterrows():
                    prefix = "Batting First" if r["Situation"] == "Batting First" else "Chasing"
                    row[f"{prefix} Matches"] = int(r["Matches"])
                    row[f"{prefix} Wins"] = int(r["Wins"])
                    row[f"{prefix} Win %"] = float(r["Win %"])
                strategy_rows.append(row)

            if strategy_rows:
                strategy_table = pd.DataFrame(strategy_rows).fillna(0)

                for col in [
                    "Batting First Matches", "Batting First Wins",
                    "Chasing Matches", "Chasing Wins"
                ]:
                    if col in strategy_table.columns:
                        strategy_table[col] = strategy_table[col].astype(int)

                display_cols = [
                    "Team",
                    "Batting First Matches", "Batting First Wins", "Batting First Win %",
                    "Chasing Matches", "Chasing Wins", "Chasing Win %"
                ]
                display_cols = [c for c in display_cols if c in strategy_table.columns]

                st.dataframe(
                    strategy_table[display_cols].sort_values(
                        "Chasing Win %",
                        ascending=False
                    ),
                    use_container_width=True,
                    hide_index=True
                )

                if "Chasing Win %" in strategy_table.columns:
                    best_chaser = strategy_table.loc[
                        strategy_table["Chasing Win %"].idxmax()
                    ]
                    st.info(
                        f"🏃 **Best chasing record in the selected scope:** "
                        f"{best_chaser['Team']} — "
                        f"{best_chaser['Chasing Win %']:.2f}% win rate "
                        f"({int(best_chaser['Chasing Wins'])} wins from "
                        f"{int(best_chaser['Chasing Matches'])} chases)."
                    )

        else:

            tm = fm[
                (fm["Team1"] == selected_team)
                | (fm["Team2"] == selected_team)
            ].copy()

            played = len(tm)
            wins = (tm["Winner"] == selected_team).sum()
            losses = max(played - wins, 0)
            win_pct = wins / played * 100 if played else 0

            c1, c2, c3 = st.columns(3)

            with c1:
                metric("Matches Played", fmt(played))
            with c2:
                metric("Matches Won", fmt(wins))
            with c3:
                metric("Win Percentage", f"{win_pct:.2f}%")

            st.markdown(
                '<div class="section-title">🪙 Toss Impact</div>',
                unsafe_allow_html=True
            )

            toss_tm = tm[tm["TossWinner"] == selected_team]
            toss_wins = (
                toss_tm["Winner"] == selected_team
            ).sum()

            toss_rate = (
                toss_wins / len(toss_tm) * 100
                if len(toss_tm) else 0
            )

            st.write(
                f"When **{selected_team}** wins the toss, "
                f"they win **{toss_rate:.2f}%** of those matches."
            )

            st.markdown(
                '<div class="section-title">🏏 Batting First vs Chasing</div>',
                unsafe_allow_html=True
            )

            strategy = team_strategy_summary(fm, fb, selected_team)

            if not strategy.empty:
                st.dataframe(
                    strategy,
                    use_container_width=True,
                    hide_index=True
                )

            if selected_season == "All Seasons":

                st.markdown(
                    '<div class="section-title">📈 Season Performance</div>',
                    unsafe_allow_html=True
                )

                tm["Won"] = tm["Winner"] == selected_team

                season_table = (
                    tm.groupby("Season")["Won"]
                    .agg(
                        Matches="count",
                        Wins="sum"
                    )
                    .reset_index()
                )

                season_table["Win %"] = (
                    season_table["Wins"]
                    / season_table["Matches"]
                    * 100
                ).round(2)

                fig = px.line(
                    season_table,
                    x="Season",
                    y="Win %",
                    markers=True,
                    title=f"{selected_team} — Win % by Season"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

    else:
        st.info("No teams available for this season.")


# ============================================================
# TEAM HEAD-TO-HEAD
# ============================================================

if active_tab == "⚔️ Team Head-to-Head":

    st.markdown(
        '<div class="section-title">⚔️ Team Head-to-Head</div>',
        unsafe_allow_html=True
    )

    teams = get_teams(fm)

    if len(teams) >= 2:

        c1, c2 = st.columns(2)

        with c1:
            team_a = st.selectbox(
                "Select Team A",
                teams,
                key="h2h_team_a"
            )

        with c2:
            team_b = st.selectbox(
                "Select Team B",
                [t for t in teams if t != team_a],
                key="h2h_team_b"
            )

        h2h = fm[
            (
                (fm["Team1"] == team_a)
                & (fm["Team2"] == team_b)
            )
            |
            (
                (fm["Team1"] == team_b)
                & (fm["Team2"] == team_a)
            )
        ].copy()

        matches_count = len(h2h)
        a_wins = int((h2h["Winner"] == team_a).sum())
        b_wins = int((h2h["Winner"] == team_b).sum())
        other = max(matches_count - a_wins - b_wins, 0)

        a_win_pct = (
            a_wins / matches_count * 100
            if matches_count else 0
        )
        b_win_pct = (
            b_wins / matches_count * 100
            if matches_count else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric("Matches", fmt(matches_count))
        with c2:
            metric(f"{team_a} Wins", fmt(a_wins))
        with c3:
            metric(f"{team_b} Wins", fmt(b_wins))
        with c4:
            metric("Other Results", fmt(other))

        if matches_count:

            # Win-rate comparison makes the H2H easier to interpret.
            comparison = pd.DataFrame({
                "Team": [team_a, team_b],
                "Wins": [a_wins, b_wins],
                "Win %": [round(a_win_pct, 2), round(b_win_pct, 2)]
            })

            st.markdown(
                '<div class="section-title">📊 Head-to-Head Win Rate</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

            fig = px.bar(
                comparison,
                x="Team",
                y="Wins",
                text="Wins",
                title=f"{team_a} vs {team_b} — Wins"
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

            # Toss impact for this specific rivalry.
            if "TossWinner" in h2h.columns:
                toss_a = int((h2h["TossWinner"] == team_a).sum())
                toss_b = int((h2h["TossWinner"] == team_b).sum())

                toss_insight = pd.DataFrame({
                    "Team": [team_a, team_b],
                    "Toss Wins": [toss_a, toss_b]
                })

                st.markdown(
                    '<div class="section-title">🪙 Toss Impact</div>',
                    unsafe_allow_html=True
                )

                if "Winner" in h2h.columns:
                    toss_insight["Toss → Match Win %"] = [
                        round(
                            ((h2h["TossWinner"] == team_a) &
                             (h2h["Winner"] == team_a)).sum()
                            / toss_a * 100, 2
                        ) if toss_a else 0,
                        round(
                            ((h2h["TossWinner"] == team_b) &
                             (h2h["Winner"] == team_b)).sum()
                            / toss_b * 100, 2
                        ) if toss_b else 0
                    ]

                st.dataframe(
                    toss_insight,
                    use_container_width=True,
                    hide_index=True
                )

            # Most recent meetings, newest first when a date is available.
            recent = h2h.copy()
            if "Date" in recent.columns:
                recent["_sort_date"] = pd.to_datetime(
                    recent["Date"], errors="coerce"
                )
                recent = recent.sort_values(
                    "_sort_date", ascending=False
                ).drop(columns="_sort_date")

            # Let the user choose how much of the rivalry history to see.
            meeting_options = [10, 20, 50]
            if len(recent) not in meeting_options:
                meeting_options.append(len(recent))
            meeting_options = sorted(set(meeting_options))
            meeting_labels = [str(n) for n in meeting_options[:-1]] + (["All"] if meeting_options and meeting_options[-1] == len(recent) and len(recent) not in [10, 20, 50] else [])

            st.selectbox(
                "Show meetings",
                meeting_labels,
                index=0,
                key="h2h_meeting_limit"
            )
            selected_meetings = st.session_state["h2h_meeting_limit"]
            if selected_meetings == "All":
                recent = recent.copy()
            else:
                recent = recent.head(int(selected_meetings)).copy()

            if "Winner" in recent.columns:
                recent["Result"] = recent["Winner"].apply(
                    lambda winner:
                        team_a if winner == team_a
                        else team_b if winner == team_b
                        else "Other"
                )

            cols = [
                c for c in
                ["ID", "Season", "Date", "Venue",
                 "Team1", "Team2", "Winner", "Result"]
                if c in recent.columns
            ]

            st.markdown(
                '<div class="section-title">🕒 Recent Meetings</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                recent[cols],
                use_container_width=True,
                hide_index=True
            )

            if a_wins > b_wins:
                st.success(
                    f"🏆 **{team_a} lead this rivalry:** "
                    f"{a_wins} wins to {b_wins} "
                    f"({a_win_pct:.2f}% vs {b_win_pct:.2f}%)."
                )
            elif b_wins > a_wins:
                st.success(
                    f"🏆 **{team_b} lead this rivalry:** "
                    f"{b_wins} wins to {a_wins} "
                    f"({b_win_pct:.2f}% vs {a_win_pct:.2f}%)."
                )
            else:
                st.info(
                    f"⚖️ **The rivalry is level:** "
                    f"{a_wins} wins each."
                )

        else:
            st.info("No matches found for this pairing.")

    else:
        st.info("At least two teams are required.")


# ============================================================
# BATTING ANALYSIS

if active_tab == "🏏 Batting Analysis":
    st.markdown('<div class="section-title">🏏 Batting Analysis</div>', unsafe_allow_html=True)
    batters = get_players(fb, "Batter")

    if batters:
        previous_batter = st.session_state.get("batting_analysis_batter")
        if previous_batter in batters:
            st.session_state["batting_analysis_batter"] = previous_batter
        elif previous_batter is not None:
            st.session_state["batting_analysis_batter"] = batters[0]

        batter = st.selectbox("Select Batter", batters, key="batting_analysis_batter")
        bd = fb[fb["Batter"] == batter].copy()
        bd["LegalBall"] = bd["Wides"] == 0
        bd["Dismissed"] = bd["PlayerOut"].astype(str).str.strip() == batter

        matches_played = bd["ID"].nunique()
        batting_innings = (bd["ID"].astype(str) + "_" + bd["Innings"].astype(str)).nunique()
        runs = bd["BatsmanRun"].sum()
        balls_faced = int(bd["LegalBall"].sum())
        outs = int(bd["Dismissed"].sum())
        fours = int((bd["BatsmanRun"] == 4).sum())
        sixes = int((bd["BatsmanRun"] == 6).sum())
        best_score = int(bd.groupby("ID")["BatsmanRun"].sum().max()) if matches_played else 0
        sr = runs / balls_faced * 100 if balls_faced else 0
        avg = runs / outs if outs else runs

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric("Matches", fmt(matches_played))
        with c2: metric("Innings", fmt(batting_innings))
        with c3: metric("Runs", fmt(runs))
        with c4: metric("Best Score", fmt(best_score))
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric("Average", f"{avg:.2f}")
        with c2: metric("Balls", fmt(balls_faced))
        with c3: metric("Strike Rate", f"{sr:.2f}")
        with c4: metric("4s / 6s", f"{fours} / {sixes}")
        c1, c2 = st.columns(2)
        with c1: metric("Outs", fmt(outs))
        with c2: metric("Dot Balls", fmt(int(((bd["BatsmanRun"] == 0) & (bd["Wides"] == 0) & (bd["NoBalls"] == 0)).sum())))

        st.markdown('<div class="section-title">📈 Season-wise Batting Performance</div>', unsafe_allow_html=True)
        season_batting = bd.groupby("Season").agg(Runs=("BatsmanRun", "sum"), Balls=("LegalBall", "sum")).reset_index()
        if not season_batting.empty:
            season_batting["Strike Rate"] = (season_batting["Runs"] / season_batting["Balls"].replace(0, pd.NA) * 100).round(2).fillna(0)
            st.dataframe(season_batting, use_container_width=True, hide_index=True)
            fig = px.line(season_batting, x="Season", y="Runs", markers=True, title=f"{batter} — Runs by Season")
            st.plotly_chart(fig, use_container_width=True)

        st.info(f"🏏 **{batter}: {int(runs)} runs in {matches_played} matches | Best: {best_score} | SR: {sr:.2f} | Average: {avg:.2f}.**")
    else:
        st.info("No batting data available.")


# BOWLING ANALYSIS

if active_tab == "🎯 Bowling Analysis":
    st.markdown('<div class="section-title">🎯 Bowling Analysis</div>', unsafe_allow_html=True)
    bowlers = get_players(fb, "Bowler")

    if bowlers:
        previous_bowler = st.session_state.get("bowling_analysis_bowler")
        if previous_bowler in bowlers:
            st.session_state["bowling_analysis_bowler"] = previous_bowler
        elif previous_bowler is not None:
            st.session_state["bowling_analysis_bowler"] = bowlers[0]

        bowler = st.selectbox("Select Bowler", bowlers, key="bowling_analysis_bowler")
        bd = fb[fb["Bowler"] == bowler].copy()
        for col in ["TotalRun", "Wides", "NoBalls", "Byes", "LegByes", "Penalty", "IsWicketDelivery"]:
            if col not in bd.columns: bd[col] = 0
            bd[col] = pd.to_numeric(bd[col], errors="coerce").fillna(0)
        bd["RunsConceded"] = (bd["TotalRun"] - bd["Byes"] - bd["LegByes"] - bd["Penalty"]).clip(lower=0)
        bd["LegalBall"] = ((bd["Wides"] == 0) & (bd["NoBalls"] == 0)).astype(int)
        non_bowler_dismissals = {"run out", "retired hurt", "retired out", "obstructing the field", "retired not out"}
        if "Kind" in bd.columns:
            bd["KindClean"] = bd["Kind"].astype(str).str.strip().str.lower()
            bd["BowlerWicket"] = ((bd["IsWicketDelivery"] == 1) & (~bd["KindClean"].isin(non_bowler_dismissals))).astype(int)
        else:
            bd["BowlerWicket"] = bd["IsWicketDelivery"].astype(int)

        matches_bowled = bd["ID"].nunique()
        bowling_innings = (bd["ID"].astype(str) + "_" + bd["Innings"].astype(str)).nunique()
        wickets = int(bd["BowlerWicket"].sum())
        runs_conceded = int(bd["RunsConceded"].sum())
        legal_balls = int(bd["LegalBall"].sum())
        overs = legal_balls // 6 + (legal_balls % 6) / 10
        economy = runs_conceded / (legal_balls / 6) if legal_balls else 0
        bowling_sr = legal_balls / wickets if wickets else 0

        match_figures = bd.groupby("ID").agg(Wickets=("BowlerWicket", "sum"), Runs=("RunsConceded", "sum")).reset_index()
        if not match_figures.empty:
            best_row = match_figures.sort_values(["Wickets", "Runs"], ascending=[False, True]).iloc[0]
            best_figures = f"{int(best_row['Wickets'])}/{int(best_row['Runs'])}"
        else:
            best_figures = "0/0"

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric("Matches", fmt(matches_bowled))
        with c2: metric("Innings", fmt(bowling_innings))
        with c3: metric("Wickets", fmt(wickets))
        with c4: metric("Best Figures", best_figures)
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric("Runs Conceded", fmt(runs_conceded))
        with c2: metric("Overs", f"{overs:.1f}")
        with c3: metric("Economy", f"{economy:.2f}")
        with c4: metric("Strike Rate", f"{bowling_sr:.2f}")
        c1 = st.columns(1)[0]
        with c1: metric("Legal Balls", fmt(legal_balls))

        st.markdown('<div class="section-title">📈 Season-wise Bowling Performance</div>', unsafe_allow_html=True)
        season_bowling = bd.groupby("Season").agg(Matches=("ID", "nunique"), Wickets=("BowlerWicket", "sum"), Balls=("LegalBall", "sum"), Runs=("RunsConceded", "sum")).reset_index()
        if not season_bowling.empty:
            season_bowling["Economy"] = (season_bowling["Runs"] / (season_bowling["Balls"] / 6).replace(0, pd.NA)).round(2).fillna(0)
            st.dataframe(season_bowling, use_container_width=True, hide_index=True)
            fig = px.line(season_bowling, x="Season", y="Wickets", markers=True, title=f"{bowler} — Wickets by Season")
            st.plotly_chart(fig, use_container_width=True)

        st.info(f"🎯 **{bowler}: {wickets} wickets in {matches_bowled} matches | Best figures: {best_figures} | Economy: {economy:.2f} | Strike rate: {bowling_sr:.2f}.**")
    else:
        st.info("No bowling data available.")


# PLAYER HEAD-TO-HEAD
# ============================================================

if active_tab == "⚔️ Player Head-to-Head":

    st.markdown(
        '<div class="section-title">⚔️ Player Head-to-Head</div>',
        unsafe_allow_html=True
    )

    batters = get_players(fb, "Batter")
    bowlers = get_players(fb, "Bowler")

    if batters and bowlers:

        c1, c2 = st.columns(2)

        # Preserve both matchup selections across season changes.
        previous_h2h_batter = st.session_state.get("player_h2h_batter")
        if previous_h2h_batter in batters:
            st.session_state["player_h2h_batter"] = previous_h2h_batter
        elif previous_h2h_batter is not None:
            st.session_state["player_h2h_batter"] = batters[0]

        previous_h2h_bowler = st.session_state.get("player_h2h_bowler")
        if previous_h2h_bowler in bowlers:
            st.session_state["player_h2h_bowler"] = previous_h2h_bowler
        elif previous_h2h_bowler is not None:
            st.session_state["player_h2h_bowler"] = bowlers[0]

        with c1:
            batter = st.selectbox(
                "Select Batter",
                batters,
                key="player_h2h_batter"
            )

        with c2:
            bowler = st.selectbox(
                "Select Bowler",
                bowlers,
                key="player_h2h_bowler"
            )

        matchup = fb[
            (fb["Batter"] == batter)
            & (fb["Bowler"] == bowler)
        ].copy()

        if not matchup.empty:

            balls_faced = len(
                matchup[matchup["Wides"] == 0]
            )
            runs = matchup["BatsmanRun"].sum()
            fours = (matchup["BatsmanRun"] == 4).sum()
            sixes = (matchup["BatsmanRun"] == 6).sum()

            dots = (
                (matchup["BatsmanRun"] == 0)
                & (matchup["Wides"] == 0)
                & (matchup["NoBalls"] == 0)
            ).sum()

            sr = (
                runs / balls_faced * 100
                if balls_faced else 0
            )

            dismissals = 0

            if "IsWicketDelivery" in matchup.columns:

                wk = matchup[
                    matchup["IsWicketDelivery"] == 1
                ]

                if "Kind" in wk.columns:

                    valid_kinds = {
                        "bowled",
                        "caught",
                        "caught and bowled",
                        "lbw",
                        "stumped",
                        "hit wicket"
                    }

                    dismissals = (
                        wk["Kind"]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(valid_kinds)
                        .sum()
                    )
                else:
                    dismissals = len(wk)

            dot_pct = (
                dots / balls_faced * 100
                if balls_faced else 0
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                metric("Balls", fmt(balls_faced))
            with c2:
                metric("Runs", fmt(runs))
            with c3:
                metric("Dismissals", fmt(dismissals))
            with c4:
                metric("Strike Rate", f"{sr:.2f}")

            c1, c2, c3 = st.columns(3)

            with c1:
                metric("4s / 6s", f"{fours} / {sixes}")
            with c2:
                metric("Dot Balls", fmt(dots))
            with c3:
                metric("Dot Ball %", f"{dot_pct:.2f}%")

            # --------------------------------------------------------
            # NEW: Plain-language matchup summary
            # --------------------------------------------------------
            boundary_runs = (fours * 4) + (sixes * 6)
            boundary_pct = (
                boundary_runs / runs * 100
                if runs else 0
            )

            st.markdown(
                '<div class="section-title">📌 Matchup Summary</div>',
                unsafe_allow_html=True
            )

            st.info(
                f"🏏 **{batter} scored {int(runs)} runs from {int(balls_faced)} balls "
                f"against {bowler}, with {int(dismissals)} dismissal(s) and a "
                f"strike rate of {sr:.2f}.**"
            )

            st.caption(
                f"Boundary contribution: **{int(boundary_runs)} runs** "
                f"({boundary_pct:.2f}% of total runs) from "
                f"{int(fours)} fours and {int(sixes)} sixes."
            )

        else:
            st.warning(
                f"No recorded {batter} vs {bowler} deliveries "
                f"for the selected season."
            )

    else:
        st.info("Player data is not available.")


# ============================================================
# BATTERS LEADERBOARD

if active_tab == "🏆 Batters Leaderboards":
    st.markdown('<div class="section-title">🏆 Batters Leaderboard</div>', unsafe_allow_html=True)
    batting = fb.copy()
    batting["LegalBall"] = batting["Wides"] == 0
    batting["IsBatterOut"] = batting["PlayerOut"].astype(str).str.strip() == batting["Batter"].astype(str).str.strip()
    batting["InningsKey"] = batting["ID"].astype(str) + "_" + batting["Innings"].astype(str)
    table = batting.groupby("Batter").agg(Matches=("ID", "nunique"), Innings=("InningsKey", "nunique"), Runs=("BatsmanRun", "sum"), Balls=("LegalBall", "sum"), Outs=("IsBatterOut", "sum"), Fours=("BatsmanRun", lambda x: (x == 4).sum()), Sixes=("BatsmanRun", lambda x: (x == 6).sum())).reset_index()
    best_scores = batting.groupby(["Batter", "ID"])["BatsmanRun"].sum().groupby(level=0).max().rename("Best Score")
    table = table.join(best_scores, on="Batter")
    table["Average"] = (table["Runs"] / table["Outs"].mask(table["Outs"] == 0)).astype(float).round(2)
    table["Strike Rate"] = (table["Runs"] / table["Balls"].mask(table["Balls"] == 0) * 100).astype(float).round(2)
    min_runs = st.slider("Minimum Runs", 0, 5000, 100, 50, key="batting_leaderboard_min_runs")
    sort_by = st.selectbox("Rank By", ["Runs", "Best Score", "Average", "Strike Rate", "Fours", "Sixes"], key="batting_leaderboard_sort")
    table = table[table["Runs"] >= min_runs].sort_values(sort_by, ascending=False, na_position="last").head(25).copy()
    table[["Average", "Strike Rate"]] = table[["Average", "Strike Rate"]].fillna(0)
    st.dataframe(table[["Batter", "Matches", "Innings", "Runs", "Best Score", "Outs", "Average", "Balls", "Strike Rate", "Fours", "Sixes"]], use_container_width=True, hide_index=True)
    if not table.empty:
        leader = table.iloc[0]
        value = leader[sort_by]
        text = f"{value:.2f}" if sort_by in ["Average", "Strike Rate"] else f"{int(value)}"
        st.success(f"🏏 **{leader['Batter']} leads by {sort_by}: {text}.**")
    else:
        st.info("No batters match the selected minimum-runs filter.")


# BOWLERS LEADERBOARD

if active_tab == "🏆 Bowlers Leaderboards":
    st.markdown('<div class="section-title">🏆 Bowlers Leaderboard</div>', unsafe_allow_html=True)
    bowling = fb.copy()
    for col in ["TotalRun", "Wides", "NoBalls", "Byes", "LegByes", "Penalty", "IsWicketDelivery"]:
        if col not in bowling.columns: bowling[col] = 0
        bowling[col] = pd.to_numeric(bowling[col], errors="coerce").fillna(0)
    bowling["RunsConceded"] = (bowling["TotalRun"] - bowling["Byes"] - bowling["LegByes"] - bowling["Penalty"]).clip(lower=0)
    bowling["LegalBall"] = ((bowling["Wides"] == 0) & (bowling["NoBalls"] == 0)).astype(int)
    non_bowler_dismissals = {"run out", "retired hurt", "retired out", "obstructing the field", "retired not out"}
    if "Kind" in bowling.columns:
        bowling["KindClean"] = bowling["Kind"].astype(str).str.strip().str.lower()
    else:
        bowling["KindClean"] = ""
    bowling["BowlerWicket"] = ((bowling["IsWicketDelivery"] == 1) & (~bowling["KindClean"].isin(non_bowler_dismissals))).astype(int)
    bowling["InningsKey"] = bowling["ID"].astype(str) + "_" + bowling["Innings"].astype(str)
    table = bowling.groupby("Bowler").agg(Matches=("ID", "nunique"), Innings=("InningsKey", "nunique"), Balls=("LegalBall", "sum"), Runs=("RunsConceded", "sum"), Wickets=("BowlerWicket", "sum")).reset_index()
    figures = bowling.groupby(["Bowler", "ID"]).agg(Wickets=("BowlerWicket", "sum"), Runs=("RunsConceded", "sum")).reset_index().sort_values(["Bowler", "Wickets", "Runs"], ascending=[True, False, True]).drop_duplicates("Bowler")
    figures["Best Figures"] = figures["Wickets"].astype(int).astype(str) + "/" + figures["Runs"].astype(int).astype(str)
    table = table.merge(figures[["Bowler", "Best Figures"]], on="Bowler", how="left")
    table["Overs"] = table["Balls"] // 6 + (table["Balls"] % 6) / 10
    table["Economy"] = (table["Runs"] / (table["Balls"] / 6).mask(table["Balls"] == 0)).astype(float).round(2)
    table["Bowling Average"] = (table["Runs"] / table["Wickets"].mask(table["Wickets"] == 0)).astype(float).round(2)
    table["Strike Rate"] = (table["Balls"] / table["Wickets"].mask(table["Wickets"] == 0)).astype(float).round(2)
    min_balls = st.number_input("Minimum legal balls", min_value=0, value=60, step=6)
    ranking = st.selectbox("Rank by", ["Wickets", "Best Figures", "Economy", "Bowling Average", "Strike Rate", "Runs"])
    filtered = table[table["Balls"] >= min_balls].copy()
    if ranking == "Best Figures": filtered = filtered.sort_values(["Wickets", "Runs"], ascending=[False, True])
    elif ranking in ["Economy", "Bowling Average", "Strike Rate"]: filtered = filtered.sort_values(ranking, ascending=True, na_position="last")
    else: filtered = filtered.sort_values(ranking, ascending=False)
    filtered = filtered.head(25)
    st.dataframe(filtered[["Bowler", "Matches", "Innings", "Balls", "Overs", "Runs", "Wickets", "Best Figures", "Economy", "Bowling Average", "Strike Rate"]], use_container_width=True, hide_index=True)
    if not filtered.empty:
        leader = filtered.iloc[0]
        if ranking == "Best Figures": st.success(f"🎯 **Best figures leader: {leader['Bowler']} ({leader['Best Figures']}).**")
        else:
            value = leader[ranking]
            text = f"{value:.2f}" if pd.notna(value) else "N/A"
            st.success(f"🎯 **{leader['Bowler']} leads by {ranking}: {text}.**")
    else: st.info("No bowlers match the selected minimum-balls filter.")


# VENUE ANALYSIS
# ============================================================

if active_tab == "🏟️ Venue Analysis":

    st.markdown(
        '<div class="section-title">🏟️ Venue Analysis</div>',
        unsafe_allow_html=True
    )

    venues = sorted(
        str(v).strip()
        for v in fm["Venue"].dropna().unique()
        if str(v).strip()
    )

    if venues:

        venue = st.selectbox(
            "Select Venue",
            venues,
            key="venue_selector"
        )

        vm = fm[fm["Venue"] == venue]
        vb = fb[fb["Venue"] == venue]

        if "Innings" in vb.columns:

            innings_scores = (
                vb.groupby(["ID", "Innings"])["TotalRun"]
                .sum()
            )

            average_score = (
                innings_scores.mean()
                if not innings_scores.empty else 0
            )

        else:
            average_score = 0

        c1, c2 = st.columns(2)

        with c1:
            metric("Matches", fmt(len(vm)))

        with c2:
            metric(
                "Average Innings Score",
                f"{average_score:.1f}"
            )

        cols = [
            c for c in
            ["ID", "Season", "Date", "Team1", "Team2", "Winner"]
            if c in vm.columns
        ]

        st.dataframe(
            vm[cols],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No venues available.")


# ============================================================
# FIELDING ANALYSIS
# ============================================================

if active_tab == "🤜 Fielding Analysis":

    st.markdown(
        '<div class="section-title">🤜 Fielding Analysis</div>',
        unsafe_allow_html=True
    )

    wickets = fb[
        fb["IsWicketDelivery"] == 1
    ].copy()

    metric(
        "Wicket Deliveries",
        fmt(len(wickets))
    )

    if "FieldersInvolved" in wickets.columns:

        f = wickets[
            wickets["FieldersInvolved"]
            .astype(str)
            .str.strip() != ""
        ]

        if not f.empty:

            fielders = (
                f["FieldersInvolved"]
                .astype(str)
                .str.split(",")
                .explode()
                .str.strip()
            )

            fielders = fielders[fielders != ""]

            table = (
                fielders.value_counts()
                .head(20)
                .reset_index()
            )

            table.columns = [
                "Fielder",
                "Fielding Involvements"
            ]

            st.markdown(
                '<div class="section-title">🧤 Fielders Involved</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True
            )

    if "Kind" in wickets.columns:

        dismissal = (
            wickets["Kind"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .reset_index()
        )

        dismissal.columns = [
            "Dismissal Type",
            "Count"
        ]

        if not dismissal.empty:

            st.markdown(
                '<div class="section-title">🎯 Dismissal Types</div>',
                unsafe_allow_html=True
            )

            fig = px.bar(
                dismissal,
                x="Dismissal Type",
                y="Count"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# RECENT FORM
# ============================================================

if active_tab == "🔥 Recent Form":

    st.markdown(
        '<div class="section-title">🔥 Recent Team Form</div>',
        unsafe_allow_html=True
    )

    teams = get_teams(fm)

    if teams:

        team = st.selectbox(
            "Select Team",
            teams,
            key="form_team"
        )

        tm = fm[
            (fm["Team1"] == team)
            | (fm["Team2"] == team)
        ].copy()

        if not tm.empty:

            if "Date" in tm.columns:

                tm["_date"] = pd.to_datetime(
                    tm["Date"],
                    errors="coerce"
                )

                tm = tm.sort_values(
                    ["_date", "ID"]
                )

            last5 = tm.tail(5)

            rows = []

            for _, row in last5.iterrows():

                winner = str(
                    row.get("Winner", "")
                ).strip()

                result = (
                    "W" if winner == team
                    else "L" if winner
                    else "NR"
                )

                opponent = (
                    row["Team2"]
                    if row["Team1"] == team
                    else row["Team1"]
                )

                rows.append({
                    "Season": row.get("Season", ""),
                    "Date": row.get("Date", ""),
                    "Opponent": opponent,
                    "Result": result
                })

            form = pd.DataFrame(rows)

            st.dataframe(
                form,
                use_container_width=True,
                hide_index=True
            )

            wins = (form["Result"] == "W").sum()
            losses = (form["Result"] == "L").sum()

            rate = (
                wins / len(form) * 100
                if len(form) else 0
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                metric("Last 5 Wins", fmt(wins))
            with c2:
                metric("Last 5 Losses", fmt(losses))
            with c3:
                metric("Recent Win %", f"{rate:.2f}%")

    else:
        st.info("No teams available.")


# ============================================================
# TOSS ANALYSIS
# ============================================================

if active_tab == "🪙 Toss Analysis":

    st.markdown(
        '<div class="section-title">🪙 Toss Analysis</div>',
        unsafe_allow_html=True
    )

    required = {
        "TossWinner",
        "TossDecision",
        "Winner"
    }

    if required.issubset(fm.columns):

        td = fm[
            fm["TossWinner"].astype(str).str.strip() != ""
        ].copy()

        total = len(td)

        toss_winner_wins = (
            td["TossWinner"] == td["Winner"]
        ).sum()

        rate = (
            toss_winner_wins / total * 100
            if total else 0
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric("Tosses Recorded", fmt(total))
        with c2:
            metric(
                "Toss Winner Also Won",
                fmt(toss_winner_wins)
            )
        with c3:
            metric(
                "Toss-to-Match Win %",
                f"{rate:.2f}%"
            )

        rows = []

        for decision, group in td.groupby(
            "TossDecision"
        ):

            wins = (
                group["TossWinner"] == group["Winner"]
            ).sum()

            rows.append({
                "Toss Decision": decision,
                "Tosses": len(group),
                "Match Wins": int(wins),
                "Win %": round(
                    wins / len(group) * 100,
                    2
                ) if len(group) else 0
            })

        decision_table = pd.DataFrame(rows)

        if not decision_table.empty:

            st.markdown(
                '<div class="section-title">🎯 Toss Decision Impact</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                decision_table,
                use_container_width=True,
                hide_index=True
            )

            fig = px.bar(
                decision_table,
                x="Toss Decision",
                y="Win %",
                title="Match Win % After Winning the Toss"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.warning("Toss data is not available.")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏏 IPL Historical Analytics • 19 Seasons • 2007/08 → 2026"
)

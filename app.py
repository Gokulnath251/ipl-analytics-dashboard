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

            recent = recent.head(10).copy()

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
# ============================================================

if active_tab == "🏏 Batting Analysis":

    st.markdown(
        '<div class="section-title">🏏 Batting Analysis</div>',
        unsafe_allow_html=True
    )

    batters = get_players(fb, "Batter")

    if batters:

        # Keep the previously selected batter when the global season changes.
        # If that player is not present in the new season, fall back safely.
        previous_batter = st.session_state.get("batting_analysis_batter")
        if previous_batter in batters:
            st.session_state["batting_analysis_batter"] = previous_batter
        elif previous_batter is not None:
            st.session_state["batting_analysis_batter"] = batters[0]

        batter = st.selectbox(
            "Select Batter",
            batters,
            key="batting_analysis_batter"
        )

        bd = fb[fb["Batter"] == batter]

        runs = bd["BatsmanRun"].sum()
        balls_faced = len(
            bd[bd["Wides"] == 0]
        )
        fours = (bd["BatsmanRun"] == 4).sum()
        sixes = (bd["BatsmanRun"] == 6).sum()

        sr = (
            runs / balls_faced * 100
            if balls_faced else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric("Runs", fmt(runs))
        with c2:
            metric("Balls", fmt(balls_faced))
        with c3:
            metric("Strike Rate", f"{sr:.2f}")
        with c4:
            metric("4s / 6s", f"{fours} / {sixes}")

        # --------------------------------------------------------
        # NEW: Season-wise batting performance
        # --------------------------------------------------------
        st.markdown(
            '<div class="section-title">📈 Season-wise Batting Performance</div>',
            unsafe_allow_html=True
        )

        season_batting = (
            bd.groupby("Season")
            .agg(
                Runs=("BatsmanRun", "sum"),
                Balls=("Wides", lambda s: (s == 0).sum())
            )
            .reset_index()
        )

        if not season_batting.empty:
            season_batting["Strike Rate"] = (
                season_batting["Runs"]
                / season_batting["Balls"]
                * 100
            ).round(2)

            season_batting = season_batting.sort_values("Season")

            st.dataframe(
                season_batting,
                use_container_width=True,
                hide_index=True
            )

            fig = px.line(
                season_batting,
                x="Season",
                y="Runs",
                markers=True,
                title=f"{batter} — Runs by Season"
            )
            st.plotly_chart(fig, use_container_width=True)

        top = (
            fb.groupby("Batter")["BatsmanRun"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
        )

        top.columns = ["Batter", "Runs"]

        st.markdown(
            '<div class="section-title">📊 Top Run Scorers</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            top,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No batting data available.")


# ============================================================
# BOWLING ANALYSIS
# ============================================================

if active_tab == "🎯 Bowling Analysis":

    st.markdown(
        '<div class="section-title">🎯 Bowling Analysis</div>',
        unsafe_allow_html=True
    )

    bowlers = get_players(fb, "Bowler")

    if bowlers:

        previous_bowler = st.session_state.get("bowling_analysis_bowler")
        if previous_bowler in bowlers:
            st.session_state["bowling_analysis_bowler"] = previous_bowler
        elif previous_bowler is not None:
            st.session_state["bowling_analysis_bowler"] = bowlers[0]

        bowler = st.selectbox(
            "Select Bowler",
            bowlers,
            key="bowling_analysis_bowler"
        )

        bd = fb[fb["Bowler"] == bowler]

        wickets = bd["IsWicketDelivery"].sum()
        runs_conceded = bd["TotalRun"].sum()

        legal = bd[
            (bd["Wides"] == 0)
            & (bd["NoBalls"] == 0)
        ]

        overs = len(legal) / 6

        economy = (
            runs_conceded / overs
            if overs else 0
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric("Wickets", fmt(wickets))
        with c2:
            metric("Runs Conceded", fmt(runs_conceded))
        with c3:
            metric("Economy", f"{economy:.2f}")

        top = (
            fb.groupby("Bowler")["IsWicketDelivery"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
        )

        top.columns = ["Bowler", "Wickets"]

        st.markdown(
            '<div class="section-title">📊 Top Wicket Takers</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            top,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No bowling data available.")


# ============================================================
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
# ============================================================

if active_tab == "🏆 Batters Leaderboards":

    st.markdown(
        '<div class="section-title">🏆 Batters Leaderboard</div>',
        unsafe_allow_html=True
    )

    table = (
        fb.groupby("Batter")
        .agg(
            Runs=("BatsmanRun", "sum"),
            Fours=(
                "BatsmanRun",
                lambda x: (x == 4).sum()
            ),
            Sixes=(
                "BatsmanRun",
                lambda x: (x == 6).sum()
            )
        )
        .sort_values("Runs", ascending=False)
        .head(25)
        .reset_index()
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# BOWLERS LEADERBOARD
# ============================================================

if active_tab == "🏆 Bowlers Leaderboards":

    st.markdown(
        '<div class="section-title">🏆 Bowlers Leaderboard</div>',
        unsafe_allow_html=True
    )

    table = (
        fb.groupby("Bowler")
        .agg(
            Wickets=("IsWicketDelivery", "sum"),
            RunsConceded=("TotalRun", "sum")
        )
        .sort_values("Wickets", ascending=False)
        .head(25)
        .reset_index()
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
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

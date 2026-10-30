import streamlit as st
import pandas as pd

from src.stats import (
    load_data,
    prepare_data,
    game_move_stats,
    basic_game_stats,
    average_cp_loss,
    mistake_stats,
    win_rate_by_color,
    cp_loss_by_phase,
    blunders_by_phase,
    stats_by_time_control,
    stats_by_time_class,
    best_worst_games,
    opening_stats,
)


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Chess Analyzer",
    page_icon="♟️",
    layout="wide"
)

st.title("♟️ Chess Analyzer")
st.caption(
    "Stockfish analysis of my Chess.com games"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

games, moves = load_data()

games, my_moves = prepare_data(games, moves)


# Convert dates for filtering and charts
games["date"] = pd.to_datetime(
    games["date"],
    format="%Y.%m.%d"
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")


# Time class
time_classes = sorted(
    games["time_class"]
    .dropna()
    .unique()
)

selected_time_classes = st.sidebar.multiselect(
    "Time Class",
    time_classes,
    default=time_classes
)


# Color
colors = sorted(
    games["my_color"]
    .dropna()
    .unique()
)

selected_colors = st.sidebar.multiselect(
    "Color",
    colors,
    default=colors
)


# Date range
min_date = games["date"].min().date()
max_date = games["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_games = games[
    games["time_class"].isin(
        selected_time_classes
    )
]

filtered_games = filtered_games[
    filtered_games["my_color"].isin(
        selected_colors
    )
]


if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_games = filtered_games[
        (
            filtered_games["date"].dt.date
            >= start_date
        )
        &
        (
            filtered_games["date"].dt.date
            <= end_date
        )
    ]


# Only keep moves from filtered games
filtered_moves = moves[
    moves["game_id"].isin(
        filtered_games["id"]
    )
]


# Recreate derived move statistics
filtered_games, filtered_my_moves = (
    prepare_data(
        filtered_games,
        filtered_moves
    )
)

game_stats = game_move_stats(
    filtered_games,
    filtered_my_moves
)


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

summary = basic_game_stats(
    filtered_games
)

mistakes = mistake_stats(
    filtered_my_moves,
    len(filtered_games)
)

avg_cp = average_cp_loss(
    filtered_my_moves
)


st.subheader("Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Games",
    summary["total_games"]
)

col2.metric(
    "Win Rate",
    f'{summary["win_rate"]}%'
)

col3.metric(
    "Avg CP Loss",
    round(avg_cp, 2)
)

col4.metric(
    "Blunders / Game",
    mistakes["blunders_per_game"]
)

col5.metric(
    "Current Rating",
    int(
        filtered_games
        .sort_values("date")
        ["my_rating"]
        .iloc[-1]
    )
)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

st.divider()

st.subheader("Results")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Wins",
    summary["wins"]
)

col2.metric(
    "Losses",
    summary["losses"]
)

col3.metric(
    "Draws",
    summary["draws"]
)


# --------------------------------------------------
# RATING OVER TIME
# --------------------------------------------------

st.divider()

st.subheader("Rating Over Time")

rating_data = (
    filtered_games[
        [
            "date",
            "my_rating"
        ]
    ]
    .sort_values("date")
    .set_index("date")
)

st.line_chart(
    rating_data
)


# --------------------------------------------------
# COLOR PERFORMANCE
# --------------------------------------------------

st.divider()

st.subheader("Performance by Color")

color_stats = (
    win_rate_by_color(
        filtered_games
    )
    .reset_index()
)

color_stats.columns = [
    "Color",
    "Win Rate"
]

st.bar_chart(
    color_stats,
    x="Color",
    y="Win Rate"
)


# --------------------------------------------------
# GAME PHASE ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("Game Phase Analysis")

col1, col2 = st.columns(2)


with col1:
    st.write(
        "### Average Centipawn Loss"
    )

    phase_cp = (
        cp_loss_by_phase(
            filtered_my_moves
        )
        .reset_index()
    )

    phase_cp.columns = [
        "Phase",
        "Average CP Loss"
    ]

    st.bar_chart(
        phase_cp,
        x="Phase",
        y="Average CP Loss"
    )


with col2:
    st.write(
        "### Blunders"
    )

    phase_blunders = (
        blunders_by_phase(
            filtered_my_moves
        )
        .reset_index()
    )

    phase_blunders.columns = [
        "Phase",
        "Blunders"
    ]

    st.bar_chart(
        phase_blunders,
        x="Phase",
        y="Blunders"
    )


# --------------------------------------------------
# OPENING ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("Opening Analysis")

opening_data = opening_stats(
    game_stats
)

# Avoid drawing conclusions from tiny samples
opening_data = opening_data[
    opening_data["games"] >= 10
]


opening_display = (
    opening_data
    .reset_index()
    .rename(
        columns={
            "opening_name": "Opening",
            "games": "Games",
            "wins": "Wins",
            "losses": "Losses",
            "draws": "Draws",
            "win_rate": "Win Rate",
            "avg_cp_loss": "Avg CP Loss",
            "avg_blunders": "Avg Blunders",
        }
    )
)


st.dataframe(
    opening_display,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# MOST PLAYED OPENINGS
# --------------------------------------------------

st.write("### Most Played Openings")

most_played = (
    opening_display
    .sort_values(
        "Games",
        ascending=False
    )
    .head(10)
)

st.bar_chart(
    most_played,
    x="Opening",
    y="Games"
)


# --------------------------------------------------
# BEST / WORST OPENINGS
# --------------------------------------------------

eligible_openings = opening_display[
    opening_display["Games"] >= 10
]

if len(eligible_openings) > 0:

    best_opening = (
        eligible_openings
        .sort_values(
            "Win Rate",
            ascending=False
        )
        .iloc[0]
    )

    worst_opening = (
        eligible_openings
        .sort_values(
            "Win Rate",
            ascending=True
        )
        .iloc[0]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            "### Best Opening"
        )

        st.metric(
            best_opening["Opening"],
            f'{best_opening["Win Rate"]}% win rate'
        )

        st.write(
            f'{int(best_opening["Games"])} games'
        )

    with col2:
        st.write(
            "### Worst Opening"
        )

        st.metric(
            worst_opening["Opening"],
            f'{worst_opening["Win Rate"]}% win rate'
        )

        st.write(
            f'{int(worst_opening["Games"])} games'
        )


# --------------------------------------------------
# TIME CONTROL
# --------------------------------------------------

st.divider()

st.subheader("Time Control Performance")

time_control_data = (
    stats_by_time_control(
        filtered_games
    )
    .reset_index()
)

time_control_data.columns = [
    "Time Control",
    "Games",
    "Average Rating",
    "Win Rate"
]

st.dataframe(
    time_control_data,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# BEST / WORST GAME
# --------------------------------------------------

st.divider()

st.subheader("Best & Worst Games")

best_game, worst_game = (
    best_worst_games(
        game_stats
    )
)


if best_game is not None:

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            "### Best Game"
        )

        st.write(
            f'**Result:** {best_game["my_result"]}'
        )

        st.write(
            f'**Avg CP Loss:** '
            f'{best_game["avg_cp_loss"]:.2f}'
        )

        st.write(
            f'**Blunders:** '
            f'{int(best_game["blunders"])}'
        )

        st.link_button(
            "View Game",
            best_game["url"]
        )

    with col2:
        st.write(
            "### Worst Game"
        )

        st.write(
            f'**Result:** {worst_game["my_result"]}'
        )

        st.write(
            f'**Avg CP Loss:** '
            f'{worst_game["avg_cp_loss"]:.2f}'
        )

        st.write(
            f'**Blunders:** '
            f'{int(worst_game["blunders"])}'
        )

        st.link_button(
            "View Game",
            worst_game["url"]
        )
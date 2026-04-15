"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
from pathlib import Path

# Ensure src/ is on the path so `from recommender import ...` resolves
# whether the script is run as:
#   python -m src.main       (from project root)
#   python -m main           (from src/)
#   python src/main.py       (from project root)
_SRC = Path(__file__).parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from tabulate import tabulate
from recommender import load_songs, recommend_songs, RANKING_MODES  # noqa: E402

# Resolve data path relative to this file — works from any working directory.
DATA_PATH = Path(__file__).parent.parent / "data" / "songs.csv"


# ---------------------------------------------------------------------------
# Standard profiles — clear, coherent taste clusters
# ---------------------------------------------------------------------------
USER_PROFILES = {
    "amara": {
        "name": "Amara",
        "genre": "afrobeat",
        "mood": "joyful",
        "energy": 0.85,
        "acousticness": 0.20,
        "instrumentalness": 0.08,
        "popularity": 75,
        "preferred_decade": 2020,
    },
    "jordan": {
        "name": "Jordan",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "acousticness": 0.82,
        "instrumentalness": 0.85,
        "popularity": 55,
        "preferred_decade": 2020,
    },
    "marcus": {
        "name": "Marcus",
        "genre": "gospel",
        "mood": "uplifting",
        "energy": 0.72,
        "acousticness": 0.55,
        "instrumentalness": 0.04,
        "popularity": 62,
        "preferred_decade": 2010,
    },
    "taylor": {
        "name": "Taylor  [High-Energy Pop]",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.88,
        "acousticness": 0.12,
        "instrumentalness": 0.03,
        "popularity": 82,
        "preferred_decade": 2020,
    },
    "rex": {
        "name": "Rex  [Deep Intense Rock]",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "acousticness": 0.10,
        "instrumentalness": 0.12,
        "popularity": 70,
        "preferred_decade": 2010,
    },
}

# ---------------------------------------------------------------------------
# Adversarial / edge-case profiles — designed to expose scoring weaknesses
# ---------------------------------------------------------------------------
ADVERSARIAL_PROFILES = {
    "zara": {
        # Conflict: high energy (0.90) but melancholy mood.
        # Energy pulls toward Gym Hero / Storm Runner; mood only matches
        # Midnight Rain (blues, energy 0.44). Does genre+mood weight (0.50)
        # beat a near-perfect energy match (0.18)?
        "name": "Zara  [Conflicted: high-energy + melancholy]",
        "genre": "blues",
        "mood": "melancholy",
        "energy": 0.90,
        "acousticness": 0.20,
        "instrumentalness": 0.15,
        "popularity": 50,
        "preferred_decade": 2010,
    },
    "ghost": {
        # Ghost genre: 'metal' does not exist in the catalogue.
        # Every song scores 0 on genre. The system must fall back entirely
        # on mood, energy, and audio features to rank results.
        "name": "Ghost  [Unknown genre: metal]",
        "genre": "metal",
        "mood": "intense",
        "energy": 0.94,
        "acousticness": 0.05,
        "instrumentalness": 0.10,
        "popularity": 65,
        "preferred_decade": 2010,
    },
    "zen": {
        # Omnivore: all continuous features set to midpoint (0.5).
        # No strong pull in any direction — tests whether the scorer
        # produces a meaningful ranking or a near-flat score distribution.
        "name": "Zen  [Neutral omnivore: all features at midpoint]",
        "genre": "classical",
        "mood": "peaceful",
        "energy": 0.50,
        "acousticness": 0.50,
        "instrumentalness": 0.50,
        "popularity": 50,
        "preferred_decade": 2000,
    },
}


WIDTH = 62


def _score_bar(score: float, width: int = 16) -> str:
    """Return a compact ASCII progress bar proportional to score (0.0–1.0)."""
    filled = round(score * width)
    return "#" * filled + "-" * (width - filled)


def _top_reason(explanation: str) -> str:
    """Return only the single highest-weighted reason for the table column."""
    return explanation.split(",")[0].strip()


def _print_profile_header(user_prefs: dict) -> None:
    print(f"\n{'=' * WIDTH}")
    print(f"  MUSIC RECOMMENDER  |  {user_prefs['name'].upper()}")
    print(
        f"  Profile : {user_prefs['genre']} | {user_prefs['mood']} | "
        f"energy {user_prefs['energy']} | {user_prefs['preferred_decade']}s"
    )
    print(f"{'=' * WIDTH}")


def _print_recommendations_table(recommendations: list) -> None:
    """Render recommendations as a formatted tabulate table."""
    headers = ["#", "Title", "Artist", "Genre", "Score", "Bar", "Top Reason"]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([
            rank,
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f}",
            _score_bar(score),
            _top_reason(explanation),
        ])
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def _run_profiles(songs: list, profiles: dict, section_title: str) -> None:
    """Print a labelled section header then run every profile in the dict."""
    print(f"\n{'*' * WIDTH}")
    print(f"  {section_title}")
    print(f"{'*' * WIDTH}")
    for user_prefs in profiles.values():
        _print_profile_header(user_prefs)
        recommendations = recommend_songs(user_prefs, songs, k=5)
        _print_recommendations_table(recommendations)
        print()


def _run_mode_comparison(songs: list, user_prefs: dict) -> None:
    """Show how each ranking mode changes the top-5 for a single profile."""
    print(f"\n{'*' * WIDTH}")
    print(f"  RANKING MODE COMPARISON  |  {user_prefs['name'].upper()}")
    print(f"{'*' * WIDTH}")
    for mode in RANKING_MODES:
        print(f"\n  Mode: {mode.upper()}")
        recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)
        _print_recommendations_table(recommendations)


def main() -> None:
    songs = load_songs(str(DATA_PATH))
    _run_profiles(songs, USER_PROFILES, "STANDARD PROFILES")
    _run_profiles(songs, ADVERSARIAL_PROFILES, "ADVERSARIAL / EDGE-CASE PROFILES")
    _run_mode_comparison(songs, USER_PROFILES["jordan"])


if __name__ == "__main__":
    main()

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

from recommender import load_songs, recommend_songs  # noqa: E402

# Resolve data path relative to this file — works from any working directory.
DATA_PATH = Path(__file__).parent.parent / "data" / "songs.csv"


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
}


WIDTH = 62


def _score_bar(score: float, width: int = 20) -> str:
    """Return an ASCII progress bar proportional to score (0.0–1.0)."""
    filled = round(score * width)
    return "#" * filled + "-" * (width - filled)


def _top_reasons(explanation: str, n: int = 3) -> str:
    """Return the top-n reasons from the comma-separated explanation string."""
    parts = [p.strip() for p in explanation.split(",")]
    return "  |  ".join(parts[:n])


def _print_profile_header(user_prefs: dict) -> None:
    print(f"\n{'=' * WIDTH}")
    print(f"  MUSIC RECOMMENDER  |  {user_prefs['name'].upper()}")
    print(
        f"  Profile : {user_prefs['genre']} | {user_prefs['mood']} | "
        f"energy {user_prefs['energy']} | {user_prefs['preferred_decade']}s"
    )
    print(f"{'=' * WIDTH}")


def _print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    bar = _score_bar(score)
    reasons = _top_reasons(explanation)
    print(f"\n  #{rank}  {song['title']} by {song['artist']}")
    print(f"       Score  : {score:.2f}  [{bar}]")
    print(f"       Genre  : {song['genre']}  |  Mood : {song['mood']}")
    print(f"       Why    : {reasons}")


def main() -> None:
    songs = load_songs(str(DATA_PATH))

    for user_prefs in USER_PROFILES.values():
        _print_profile_header(user_prefs)
        recommendations = recommend_songs(user_prefs, songs, k=5)
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            _print_recommendation(rank, song, score, explanation)
        print(f"\n  {'-' * (WIDTH - 2)}")


if __name__ == "__main__":
    main()

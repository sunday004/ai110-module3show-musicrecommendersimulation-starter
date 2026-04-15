from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    popularity: int
    release_decade: int

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_acousticness: float = 0.5
    target_instrumentalness: float = 0.5
    target_popularity: int = 60
    preferred_decade: int = 2020

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the song catalogue that this recommender will rank against."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given UserProfile."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why this song was recommended."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def _to_float(value: str) -> float:
    """Convert a CSV cell to float, returning 0.0 for empty or invalid cells."""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return 0.0


def _to_int(value: str) -> int:
    """Convert a CSV cell to int, returning 0 for empty or invalid cells."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return 0


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               _to_int(row["id"]),
                "title":            row["title"].strip(),
                "artist":           row["artist"].strip(),
                "genre":            row["genre"].strip(),
                "mood":             row["mood"].strip(),
                "energy":           _to_float(row["energy"]),
                "tempo_bpm":        _to_float(row["tempo_bpm"]),
                "valence":          _to_float(row["valence"]),
                "danceability":     _to_float(row["danceability"]),
                "acousticness":     _to_float(row["acousticness"]),
                "instrumentalness": _to_float(row["instrumentalness"]),
                "popularity":       _to_int(row["popularity"]),
                "release_decade":   _to_int(row["release_decade"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

# ---------------------------------------------------------------------------
# Scoring weights — must sum to 1.0
# Tier 1 (core taste signals)
_W_GENRE            = 0.28
_W_MOOD             = 0.22
_W_ENERGY           = 0.18
_W_ACOUSTICNESS     = 0.12
# Tier 2 (supporting audio features)
_W_INSTRUMENTALNESS = 0.08
_W_TEMPO            = 0.05
_W_DANCEABILITY     = 0.04
# Tier 3 (catalogue metadata)
_W_POPULARITY       = 0.02
_W_DECADE           = 0.01
# ---------------------------------------------------------------------------
_TEMPO_MIN, _TEMPO_MAX   = 52, 152   # BPM range across the current catalogue
_DECADE_MAX_GAP          = 50        # years between oldest (1970) and newest (2020)


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """
    Score a single song against a user preference profile.

    Returns (score, explanation) where:
      - score is a float in [0.0, 1.0]
      - explanation is an ordered list of weighted contributions, highest first,
        e.g. "genre match (+0.28), mood match (+0.22), energy close (+0.15)"
    """
    # --- Tier 1: categorical match (binary 0 or 1) --------------------------
    genre_score = 1.0 if song["genre"] == user_prefs["genre"] else 0.0
    genre_contrib = _W_GENRE * genre_score
    genre_label = (
        f"genre match (+{genre_contrib:.2f})"
        if genre_score
        else f"genre mismatch (+{genre_contrib:.2f})"
    )

    mood_score = 1.0 if song["mood"] == user_prefs["mood"] else 0.0
    mood_contrib = _W_MOOD * mood_score
    mood_label = (
        f"mood match (+{mood_contrib:.2f})"
        if mood_score
        else f"mood mismatch (+{mood_contrib:.2f})"
    )

    # --- Tier 1: continuous similarity (1 - normalised distance) ------------
    energy_score   = 1.0 - abs(song["energy"] - user_prefs["energy"])
    energy_contrib = _W_ENERGY * energy_score
    energy_label   = f"energy {song['energy']:.2f} (+{energy_contrib:.2f})"

    acoustic_score   = 1.0 - abs(song["acousticness"] - user_prefs["acousticness"])
    acoustic_contrib = _W_ACOUSTICNESS * acoustic_score
    acoustic_label   = f"acousticness {song['acousticness']:.2f} (+{acoustic_contrib:.2f})"

    # --- Tier 2: supporting audio features ----------------------------------
    inst_score   = 1.0 - abs(song["instrumentalness"] - user_prefs["instrumentalness"])
    inst_contrib = _W_INSTRUMENTALNESS * inst_score
    inst_label   = f"instrumentalness {song['instrumentalness']:.2f} (+{inst_contrib:.2f})"

    tempo_norm   = (song["tempo_bpm"] - _TEMPO_MIN) / (_TEMPO_MAX - _TEMPO_MIN)
    tempo_score  = 1.0 - abs(tempo_norm - user_prefs["energy"])
    tempo_contrib = _W_TEMPO * tempo_score
    tempo_label  = f"tempo {song['tempo_bpm']:.0f}bpm (+{tempo_contrib:.2f})"

    dance_score   = 1.0 - abs(song["danceability"] - user_prefs["energy"])
    dance_contrib = _W_DANCEABILITY * dance_score
    dance_label   = f"danceability {song['danceability']:.2f} (+{dance_contrib:.2f})"

    # --- Tier 3: catalogue metadata -----------------------------------------
    pop_score   = 1.0 - abs(song["popularity"] - user_prefs["popularity"]) / 100
    pop_contrib = _W_POPULARITY * pop_score
    pop_label   = f"popularity {song['popularity']} (+{pop_contrib:.2f})"

    decade_gap    = abs(song["release_decade"] - user_prefs["preferred_decade"])
    decade_score  = 1.0 - (decade_gap / _DECADE_MAX_GAP)
    decade_contrib = _W_DECADE * decade_score
    decade_label  = f"decade {song['release_decade']} (+{decade_contrib:.2f})"

    # --- Weighted sum --------------------------------------------------------
    score = (
        genre_contrib + mood_contrib + energy_contrib + acoustic_contrib
        + inst_contrib + tempo_contrib + dance_contrib + pop_contrib + decade_contrib
    )

    # Sort reasons by contribution (highest first) so the explanation leads
    # with the features that drove the score most
    all_reasons = sorted(
        [
            (genre_contrib,   genre_label),
            (mood_contrib,    mood_label),
            (energy_contrib,  energy_label),
            (acoustic_contrib, acoustic_label),
            (inst_contrib,    inst_label),
            (tempo_contrib,   tempo_label),
            (dance_contrib,   dance_label),
            (pop_contrib,     pop_label),
            (decade_contrib,  decade_label),
        ],
        key=lambda x: x[0],
        reverse=True,
    )
    explanation = ", ".join(label for _, label in all_reasons)

    return round(score, 4), explanation


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Rank all songs against a user profile and return the top-k results.

    Steps:
      1. Score  — use score_song as a judge for every song in the catalogue,
                  producing a list of (song, score, explanation) tuples.
      2. Rank   — sorted() creates a new list ordered by score descending;
                  the original `songs` list is never mutated.
      3. Slice  — [:k] returns only the top-k results.

    Uses sorted() instead of list.sort() so the input catalogue is not
    modified in-place; the caller's list remains unchanged after the call.

    Returns a list of (song_dict, score, explanation) tuples.
    Required by src/main.py
    """
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]

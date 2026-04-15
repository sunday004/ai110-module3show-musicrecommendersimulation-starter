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

# Experiment result (genre halved, energy doubled): #1 rankings unchanged
# across all profiles — genre+mood lock-in persists even at half weight.
# Weights are now managed via RANKING_MODES presets below.
# ---------------------------------------------------------------------------
_TEMPO_MIN, _TEMPO_MAX   = 52, 152   # BPM range across the current catalogue
_DECADE_MAX_GAP          = 50        # years between oldest (1970) and newest (2020)

# ---------------------------------------------------------------------------
# Ranking mode presets — each is a complete weight configuration summing to 1.0
# Switch modes by passing mode="genre_first" etc. to recommend_songs().
# ---------------------------------------------------------------------------
RANKING_MODES = {
    "balanced": {          # default — current production weights
        "genre": 0.28, "mood": 0.22, "energy": 0.18, "acousticness": 0.12,
        "instrumentalness": 0.08, "tempo": 0.05, "danceability": 0.04,
        "popularity": 0.02, "decade": 0.01,
    },
    "genre_first": {       # heavy genre bias — surfaces catalogue clusters
        "genre": 0.45, "mood": 0.22, "energy": 0.12, "acousticness": 0.08,
        "instrumentalness": 0.05, "tempo": 0.03, "danceability": 0.03,
        "popularity": 0.01, "decade": 0.01,
    },
    "mood_first": {        # mood dominates — useful for context/activity matching
        "genre": 0.15, "mood": 0.42, "energy": 0.18, "acousticness": 0.12,
        "instrumentalness": 0.06, "tempo": 0.03, "danceability": 0.03,
        "popularity": 0.01, "decade": 0.00,
    },
    "energy_focused": {    # audio-driven — good for workout/focus playlists
        "genre": 0.10, "mood": 0.10, "energy": 0.42, "acousticness": 0.18,
        "instrumentalness": 0.10, "tempo": 0.06, "danceability": 0.03,
        "popularity": 0.01, "decade": 0.00,
    },
}


def score_song(user_prefs: Dict, song: Dict, weights: Dict = None) -> Tuple[float, str]:
    """
    Score a single song against a user preference profile.

    Returns (score, explanation) where:
      - score is a float in [0.0, 1.0]
      - explanation is an ordered list of weighted contributions, highest first,
        e.g. "genre match (+0.28), mood match (+0.22), energy close (+0.15)"
    """
    if weights is None:
        weights = RANKING_MODES["balanced"]
    w_genre  = weights["genre"]
    w_mood   = weights["mood"]
    w_energy = weights["energy"]
    w_acoustic = weights["acousticness"]
    w_inst   = weights["instrumentalness"]
    w_tempo  = weights["tempo"]
    w_dance  = weights["danceability"]
    w_pop    = weights["popularity"]
    w_decade = weights["decade"]

    # --- Tier 1: categorical match (binary 0 or 1) --------------------------
    genre_score = 1.0 if song["genre"] == user_prefs["genre"] else 0.0
    genre_contrib = w_genre * genre_score
    genre_label = (
        f"genre match (+{genre_contrib:.2f})"
        if genre_score
        else f"genre mismatch (+{genre_contrib:.2f})"
    )

    mood_score = 1.0 if song["mood"] == user_prefs["mood"] else 0.0
    mood_contrib = w_mood * mood_score
    mood_label = (
        f"mood match (+{mood_contrib:.2f})"
        if mood_score
        else f"mood mismatch (+{mood_contrib:.2f})"
    )

    # --- Tier 1: continuous similarity (1 - normalised distance) ------------
    energy_score   = 1.0 - abs(song["energy"] - user_prefs["energy"])
    energy_contrib = w_energy * energy_score
    energy_label   = f"energy {song['energy']:.2f} (+{energy_contrib:.2f})"

    acoustic_score   = 1.0 - abs(song["acousticness"] - user_prefs["acousticness"])
    acoustic_contrib = w_acoustic * acoustic_score
    acoustic_label   = f"acousticness {song['acousticness']:.2f} (+{acoustic_contrib:.2f})"

    # --- Tier 2: supporting audio features ----------------------------------
    inst_score   = 1.0 - abs(song["instrumentalness"] - user_prefs["instrumentalness"])
    inst_contrib = w_inst * inst_score
    inst_label   = f"instrumentalness {song['instrumentalness']:.2f} (+{inst_contrib:.2f})"

    tempo_norm   = (song["tempo_bpm"] - _TEMPO_MIN) / (_TEMPO_MAX - _TEMPO_MIN)
    tempo_score  = 1.0 - abs(tempo_norm - user_prefs["energy"])
    tempo_contrib = w_tempo * tempo_score
    tempo_label  = f"tempo {song['tempo_bpm']:.0f}bpm (+{tempo_contrib:.2f})"

    dance_score   = 1.0 - abs(song["danceability"] - user_prefs["energy"])
    dance_contrib = w_dance * dance_score
    dance_label   = f"danceability {song['danceability']:.2f} (+{dance_contrib:.2f})"

    # --- Tier 3: catalogue metadata -----------------------------------------
    pop_score   = 1.0 - abs(song["popularity"] - user_prefs["popularity"]) / 100
    pop_contrib = w_pop * pop_score
    pop_label   = f"popularity {song['popularity']} (+{pop_contrib:.2f})"

    decade_gap    = abs(song["release_decade"] - user_prefs["preferred_decade"])
    decade_score  = 1.0 - (decade_gap / _DECADE_MAX_GAP)
    decade_contrib = w_decade * decade_score
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


def _apply_diversity_penalty(
    ranked: List[Tuple[Dict, float, str]],
    penalty: float = 0.15,
) -> List[Tuple[Dict, float, str]]:
    """
    Reduce the score of any song whose artist already appears earlier
    in the ranked list by `penalty` points, then re-sort.

    This prevents the same artist dominating multiple slots in the
    top-k results and improves catalogue diversity.
    """
    seen_artists: set = set()
    adjusted = []
    for song, score, explanation in ranked:
        if song["artist"] in seen_artists:
            score = round(max(0.0, score - penalty), 4)
        seen_artists.add(song["artist"])
        adjusted.append((song, score, explanation))
    return sorted(adjusted, key=lambda x: x[1], reverse=True)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    diversity_penalty: float = 0.15,
    mode: str = "balanced",
) -> List[Tuple[Dict, float, str]]:
    """
    Rank all songs against a user profile and return the top-k results.

    Steps:
      1. Score  — score_song judges every song using the chosen weight preset.
      2. Rank   — sorted() orders by score descending without mutating the input list.
      3. Diversity — _apply_diversity_penalty reduces scores for repeated artists.
      4. Slice  — [:k] returns the top-k after diversity adjustment.

    Args:
        user_prefs: dict of user preference values.
        songs: full catalogue as a list of song dicts.
        k: number of results to return (default 5).
        diversity_penalty: score reduction applied to each repeated artist (default 0.15).
        mode: weight preset key from RANKING_MODES (default "balanced").

    Returns a list of (song_dict, score, explanation) tuples.
    Required by src/main.py
    """
    weights = RANKING_MODES.get(mode, RANKING_MODES["balanced"])
    scored = [(song, *score_song(user_prefs, song, weights=weights)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    diversified = _apply_diversity_penalty(ranked, penalty=diversity_penalty)
    return diversified[:k]

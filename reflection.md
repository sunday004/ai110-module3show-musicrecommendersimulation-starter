# Profile Comparison Reflections

Plain-language notes on what changed between profile pairs and why it makes
sense. Written for a non-programmer audience.

---

## Pair 1 — Amara (afrobeat / joyful) vs Jordan (lofi / chill)

These two profiles sit at opposite ends of the energy scale. Amara wants
high-energy, joyful afrobeat (energy 0.85). Jordan wants calm, instrumental
lofi music for studying (energy 0.38). The system gave each of them a
completely different top five with no overlap at all.

Amara got Lagos Sunrise at #1 (score 0.99) — a song that matches her genre,
mood, energy, and acoustic fingerprint almost perfectly. Jordan got Library
Rain and Midnight Coding at the top — quiet, piano-heavy lofi tracks made for
late-night focus sessions.

**Why this makes sense:** The genre and mood signals act like a hard filter.
Afrobeat and lofi have nothing in common as categories, so there is zero
chance of a song crossing over from one list to the other through audio
features alone. The energy gap (0.85 vs 0.38) reinforces the separation —
a high-BPM afrobeat track would score nearly zero on energy similarity for
Jordan, and vice versa. The system correctly keeps these two listeners in
entirely separate worlds.

---

## Pair 2 — Taylor (pop / happy) vs Rex (rock / intense)

Taylor and Rex both want high-energy music (0.88 and 0.92) with very similar
tempo and danceability preferences. The key difference is mood: Taylor wants
happy, Rex wants intense. Both genres — pop and rock — have different songs
at the top.

Taylor got Sunrise City (#1, score 0.97). Rex got Storm Runner (#1, score
0.98). But look at slot #2: Taylor got Gym Hero (pop / intense) and Rex got
Gym Hero (pop / intense) as well — the same song in both lists.

**Why this makes sense:** Once the one unique genre song fills #1, the
remaining slots are competed for purely on audio similarity. Gym Hero has
energy 0.93, acousticness 0.05, and a driving tempo — numbers that look
nearly identical to what both Taylor and Rex declared as preferences. The
system does not know that "happy pop workout anthems" and "intense rock" are
culturally different experiences. It only sees that the numbers match. This
is a real limitation: the same song bleeding into two very different profiles
is a sign that the catalogue does not have enough variety in the high-energy
range to serve these two listeners differently.

---

## Pair 3 — Marcus (gospel / uplifting) vs Zara (blues / melancholy + high energy)

This is the most interesting pair because Zara was designed to be
contradictory. Marcus has a clear, coherent profile: gospel, uplifting mood,
mid-energy. Zara has a conflict built in: she declared blues and melancholy
as her genre and mood, but also said she wants very high energy (0.90) — the
musical equivalent of asking for a quiet, sad acoustic ballad that also makes
you want to run a marathon.

Marcus got Higher Ground at #1 (score 0.98). Everything worked as expected —
one gospel song, it wins by default.

Zara got Midnight Rain at #1 (score 0.79) — a quiet, slow blues track with
energy 0.44. This is despite her energy target being 0.90. Songs like Gym
Hero and Storm Runner, which match her energy target almost perfectly, came
in at positions 3–5.

**Why this makes sense:** The system correctly prioritised emotional fit over
physical energy. Blues and melancholy together are worth 0.50 points before
any other signal is considered. The energy mismatch for Midnight Rain costs
only about 0.08 points. So emotional context won. This actually reflects how
most people listen to music: when you are in a melancholy mood you want sad
music, not a high-BPM pump-up track, even if you normally enjoy high-energy
songs. The system got this right — and it is one of the few cases where the
genre+mood dominance is a feature, not a bug.

---

## Pair 4 — Ghost (genre not in catalogue) vs Zen (neutral midpoint)

Both of these profiles have no meaningful genre match in the catalogue. Ghost
asked for "metal" which does not exist. Zen asked for "classical" and got one
match, but then all remaining preferences were set to exactly 0.5 — perfectly
neutral on every dimension.

Ghost got Gym Hero and Storm Runner tied at the top (scores 0.70 each in the
original run). These are the two most sonically intense songs in the catalogue
— high energy, low acoustic, driving tempo. They are the closest approximation
to metal that a 20-song catalogue without a metal section can offer.

Zen got Still Waters at #1 (score 0.82, the one classical song) and then a
cluster of four very different songs — reggae, r&b, country, blues — all
scoring between 0.41 and 0.44.

**Why this makes sense:** Ghost shows the system doing the right thing under
failure conditions — it cannot give you metal, but it tries to approximate
it. Zen exposes the system's weakness under uncertainty — when you give it no
signal to work with, it cannot distinguish between reggae and blues because
all their audio numbers are equally close to 0.5. In real life, a user who
says "I like a bit of everything" is actually very hard to serve, and this
simulation makes that visible.

---

## Why Does Gym Hero Keep Appearing in Everyone's List?

If you ran this recommender for several very different profiles and noticed
Gym Hero (a pop workout anthem) popping up in the results for afrobeat fans,
rock fans, and even a conflicted blues listener — here is why.

Think of each song as a point on a map, and each user profile as a pin dropped
on the map. The recommender finds the five songs whose "locations" on the map
are closest to the user's pin.

Gym Hero sits at a very specific location: high energy (0.93), very low
acoustic texture (0.05), low instrumentalness (0.02), high danceability (0.88).
Those are extreme values — Gym Hero is in the corner of the map where "loud,
electronic, beat-driven" songs live.

The problem is that many user profiles also have pins in roughly that corner
— anyone who says they like high energy, low acoustic music will find Gym Hero
nearby, even if their declared genre is completely different. The system cannot
tell that a rock fan and a pop fan would find Gym Hero equally annoying for
different reasons. It only sees numbers.

This is what researchers call a **filter bubble** — the system keeps
recommending the same small cluster of songs because they happen to be
numerically central in the feature space, not because they are genuinely
right for each user. The fix is more songs in the catalogue so that each
corner of the map has many options to choose from, not just one or two.

---

*Personal reflection moved to [README.md](README.md).*

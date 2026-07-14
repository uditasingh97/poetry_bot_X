"""
Romance Poetry Bot
------------------
Posts one public-domain romance verse per run to X (Twitter).

Selection is deterministic by date (day-of-year modulo corpus size),
so no state file or database is needed between runs. Add or remove
verses in verses.json freely; the rotation adjusts automatically.

Required environment variables (set as GitHub Actions secrets):
    X_API_KEY            (a.k.a. consumer key)
    X_API_SECRET         (a.k.a. consumer secret)
    X_ACCESS_TOKEN
    X_ACCESS_SECRET
"""

import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import tweepy

MAX_TWEET_LEN = 280
VERSES_FILE = Path(__file__).parent / "verses.json"


def load_verses() -> list[dict]:
    with open(VERSES_FILE, encoding="utf-8") as f:
        verses = json.load(f)
    if not verses:
        sys.exit("verses.json is empty — nothing to post.")
    return verses


def pick_verse(verses: list[dict]) -> dict:
    """Deterministic daily rotation: same date -> same verse."""
    today = date.today()
    # Combine year and day-of-year so the cycle doesn't repeat
    # identically every year if the corpus grows.
    index = (today.toordinal()) % len(verses)
    return verses[index]


def format_tweet(v: dict) -> str:
    attribution = f'\u2014 {v["poet"]}, "{v["poem"]}" ({v["year"]})'
    tweet = f'{v["verse"]}\n\n{attribution}'

    if len(tweet) <= MAX_TWEET_LEN:
        return tweet

    # Trim the verse line-by-line from the end until it fits.
    lines = v["verse"].splitlines()
    while lines and len(tweet) > MAX_TWEET_LEN:
        lines = lines[:-1]
        tweet = "\n".join(lines) + " \u2026\n\n" + attribution
    if not lines:
        sys.exit(f'Verse by {v["poet"]} cannot fit in a tweet even truncated. '
                 f'Shorten it in verses.json.')
    return tweet


def post(tweet: str) -> None:
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )
    response = client.create_tweet(text=tweet)
    tweet_id = response.data["id"]
    print(f"Posted tweet {tweet_id} at {datetime.now(timezone.utc).isoformat()}")


def main() -> None:
    verses = load_verses()
    verse = pick_verse(verses)

    # Safety net: never post an entry still flagged for source verification.
    if "REPLACE BEFORE USE" in verse.get("note", ""):
        sys.exit(f'Skipping "{verse["poem"]}" by {verse["poet"]}: '
                 f'translation source not yet verified as public domain. '
                 f'Fix the entry in verses.json.')

    tweet = format_tweet(verse)
    print("Tweet preview:\n" + "-" * 40 + f"\n{tweet}\n" + "-" * 40)

    if os.environ.get("DRY_RUN") == "1":
        print("DRY_RUN=1 — not posting.")
        return

    post(tweet)


if __name__ == "__main__":
    main()

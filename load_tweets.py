import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import pymongo

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = "eurovision"
COL_NAME  = "tweets"
BATCH_SIZE = 500  # insert 500 at a time — safe for Atlas free tier

# Fields inside the user object we don't need for any query
USER_FIELDS_TO_DROP = [
    "profile_background_color", "profile_background_image_url",
    "profile_background_image_url_https", "profile_background_tile",
    "profile_link_color", "profile_sidebar_border_color",
    "profile_sidebar_fill_color", "profile_text_color",
    "profile_use_background_image", "profile_image_url",
    "profile_image_url_https", "profile_banner_url",
    "utc_offset", "time_zone", "contributors_enabled",
    "is_translator", "translator_type", "following",
    "follow_request_sent", "notifications",
]

# ── Cleaning helpers ───────────────────────────────────────────────────────────
def parse_twitter_date(s):
    """Convert Twitter's date string to a Python datetime."""
    try:
        return datetime.strptime(s, "%a %b %d %H:%M:%S +0000 %Y")
    except Exception:
        return s  # leave as-is if it fails

def clean_user(user):
    if not isinstance(user, dict):
        return user
    for field in USER_FIELDS_TO_DROP:
        user.pop(field, None)
    user.pop("id", None)  # drop float id — we keep id_str
    if isinstance(user.get("created_at"), str):
        user["created_at"] = parse_twitter_date(user["created_at"])
    return user

def clean_tweet(tweet):
    if not isinstance(tweet, dict):
        return tweet

    # Drop float id, keep id_str (floats lose precision for large tweet IDs)
    tweet.pop("id", None)

    # Parse date string → datetime object
    if isinstance(tweet.get("created_at"), str):
        tweet["created_at"] = parse_twitter_date(tweet["created_at"])

    # Convert timestamp_ms string → integer
    if "timestamp_ms" in tweet:
        tweet["timestamp_ms"] = int(tweet["timestamp_ms"])

    # Drop null geo fields we'll never query
    for field in ["geo", "coordinates", "contributors"]:
        if tweet.get(field) is None:
            tweet.pop(field, None)

    # Clean the author
    if "user" in tweet:
        tweet["user"] = clean_user(tweet["user"])

    # Recursively clean nested tweet objects
    if "retweeted_status" in tweet:
        tweet["retweeted_status"] = clean_tweet(tweet["retweeted_status"])
    if "quoted_status" in tweet:
        tweet["quoted_status"] = clean_tweet(tweet["quoted_status"])

    return tweet

# ── Index creation ─────────────────────────────────────────────────────────────
def create_indexes(collection):
    print("Creating indexes...")
    collection.create_index("id_str", unique=True)           # dedup guard
    collection.create_index("timestamp_ms")
    collection.create_index("entities.hashtags.text")
    collection.create_index("user.id_str")
    collection.create_index("user.screen_name")
    collection.create_index("in_reply_to_status_id_str")
    collection.create_index("retweeted_status.id_str")
    collection.create_index("lang")
    collection.create_index([("retweet_count", pymongo.DESCENDING)])
    collection.create_index([("entities.hashtags.text", pymongo.ASCENDING),
                             ("timestamp_ms", pymongo.ASCENDING)])
    collection.create_index([("text", pymongo.TEXT)])
    print("Indexes created.")

# ── Main loader ────────────────────────────────────────────────────────────────
def load_file(filepath, collection):
    print(f"\nLoading {filepath} ...")

    total    = 0
    inserted = 0
    skipped  = 0
    batch    = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip blank lines

            try:
                tweet = json.loads(line)  # parse one line = one tweet
            except json.JSONDecodeError as e:
                print(f"\n  Skipping bad line {total+1}: {e}")
                continue

            batch.append(clean_tweet(tweet))
            total += 1

            if len(batch) == BATCH_SIZE:
                try:
                    result = collection.insert_many(batch, ordered=False)
                    inserted += len(result.inserted_ids)
                except pymongo.errors.BulkWriteError as e:
                    inserted += e.details.get("nInserted", 0)
                    skipped  += len(e.details.get("writeErrors", []))
                batch = []
                print(f"  Processed {total} tweets so far...", end="\r")

        # Final partial batch
        if batch:
            try:
                result = collection.insert_many(batch, ordered=False)
                inserted += len(result.inserted_ids)
            except pymongo.errors.BulkWriteError as e:
                inserted += e.details.get("nInserted", 0)
                skipped  += len(e.details.get("writeErrors", []))

    print(f"\n  Done — inserted: {inserted}, skipped (duplicates): {skipped}")
    return inserted

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not MONGO_URI:
        print("ERROR: MONGO_URI not found. Check your .env file.")
        sys.exit(1)

    # Accept file paths as command-line arguments, default to Eurovision3.json
    files = sys.argv[1:] if len(sys.argv) > 1 else ["data/Eurovision3.json"]

    print(f"Connecting to MongoDB...")
    client = pymongo.MongoClient(MONGO_URI)
    db     = client[DB_NAME]
    col    = db[COL_NAME]
    print(f"Connected. Database: '{DB_NAME}', Collection: '{COL_NAME}'")

    create_indexes(col)

    total_inserted = 0
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"WARNING: File not found — {filepath}, skipping.")
            continue
        total_inserted += load_file(filepath, col)

    print(f"\nAll done! Total tweets inserted: {total_inserted}")
    print(f"Collection count: {col.count_documents({})}")
    client.close()
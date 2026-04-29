import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import pymongo

load_dotenv()

app = Flask(__name__)

# ── DB Connection ──────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI")
client    = pymongo.MongoClient(MONGO_URI)
db        = client["eurovision"]
col       = db["tweets"]


def serialize(doc):
    """Recursively convert ObjectId and datetime to JSON-safe types."""
    if isinstance(doc, list):
        return [serialize(d) for d in doc]
    if isinstance(doc, dict):
        return {k: serialize(v) for k, v in doc.items()}
    if isinstance(doc, datetime):
        return doc.replace(tzinfo=timezone.utc).isoformat()
    return str(doc) if not isinstance(doc, (str, int, float, bool, type(None))) else doc


# ── Endpoint 1 – Health check ──────────────────────────────────────────────────
@app.route("/ping", methods=["GET"])
def ping():
    tweet = col.find_one({}, {"_id": 0, "id_str": 1, "text": 1, "user.screen_name": 1})
    if not tweet:
        return jsonify({"error": "No tweets found"}), 404
    return jsonify({"status": "ok", "sample_tweet": serialize(tweet)})


# ── Query 1 – Top retweeted ────────────────────────────────────────────────────
@app.route("/top-retweeted", methods=["GET"])
def top_retweeted():
    pipeline = [
        {"$match": {"retweeted_status": {"$exists": False}}},
        {"$sort":  {"retweet_count": -1}},
        {"$limit": 10},
        {"$project": {
            "_id": 0,
            "id_str": 1,
            "text": 1,
            "retweet_count": 1,
            "user.screen_name": 1,
            "created_at": 1,
        }},
    ]
    results = list(col.aggregate(pipeline))
    return jsonify({"data": serialize(results)})


# ── Query 2 – Most active users ────────────────────────────────────────────────
@app.route("/most-active-users", methods=["GET"])
def most_active_users():
    pipeline = [
        {
            "$group": {
                "_id": "$user.id_str",
                "screen_name": {"$first": "$user.screen_name"},
                "tweet_count": {"$sum": 1}
            }
        },
        {"$sort": {"tweet_count": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "user_id": "$_id",
                "screen_name": 1,
                "tweet_count": 1
            }
        }
    ]

    results = list(col.aggregate(pipeline))
    return jsonify({"data": serialize(results)})


# ── Query 3 – Tweets by hashtag ───────────────────────────────────────────────
@app.route("/tweets-by-hashtag")
def tweets_by_hashtag():
    hashtag = request.args.get("hashtag")

    results = list(col.find(
        {"entities.hashtags.text": hashtag},
        {
            "_id": 0,
            "text": 1,
            "user.screen_name": 1,
            "created_at": 1,
            "timestamp_ms": 1,
            "retweet_count": 1,
            "id_str": 1
        }
    ).sort("timestamp_ms", 1).limit(50))

    return jsonify(serialize(results))


# ── Query 4 – Replies to a tweet ──────────────────────────────────────────────
@app.route("/replies-to-tweet")
def replies_to_tweet():
    tweet_id = request.args.get("tweet_id")

    results = list(col.find(
        {"in_reply_to_status_id_str": tweet_id},
        {
            "_id": 0,
            "text": 1,
            "user.screen_name": 1,
            "created_at": 1,
            "timestamp_ms": 1,
            "retweet_count": 1,
            "id_str": 1
        }
    ).sort("timestamp_ms", 1))

    return jsonify(serialize(results))


# ── Optional – Sample hashtags ────────────────────────────────────────────────
@app.route("/sample-hashtags")
def sample_hashtags():
    pipeline = [
        {"$unwind": "$entities.hashtags"},
        {"$group": {"_id": "$entities.hashtags.text"}},
        {"$limit": 20}
    ]

    results = list(col.aggregate(pipeline))
    hashtags = [r["_id"] for r in results if r["_id"]]

    return jsonify(hashtags)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
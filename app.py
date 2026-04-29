import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, jsonify
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


# ── Endpoint 1 – Health check / sample tweet ──────────────────────────────────
@app.route("/ping", methods=["GET"])
def ping():
    """Returns one tweet to confirm the server and DB are alive."""
    tweet = col.find_one({}, {"_id": 0, "id_str": 1, "text": 1, "user.screen_name": 1})
    if not tweet:
        return jsonify({"error": "No tweets found in collection"}), 404
    return jsonify({"status": "ok", "sample_tweet": serialize(tweet)})


# ── Endpoint 2 – Query 1: Top 10 most retweeted original tweets ───────────────
@app.route("/top-retweeted", methods=["GET"])
def top_retweeted():
    """
    Find the top 10 most retweeted tweets (original tweets only).
    Filters out retweets by checking retweeted_status does not exist,
    then sorts by retweet_count descending using the retweet_count index.
    """
    pipeline = [
        {"$match": {"retweeted_status": {"$exists": False}}},
        {"$sort":  {"retweet_count": -1}},
        {"$limit": 10},
        {"$project": {
            "_id":              0,
            "id_str":           1,
            "text":             1,
            "retweet_count":    1,
            "user.screen_name": 1,
            "created_at":       1,
        }},
    ]
    results = list(col.aggregate(pipeline))
    return jsonify({"query": "top_retweeted", "count": len(results), "data": serialize(results)})

#--Query 2 - Most active users
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
        {
            "$sort": {"tweet_count": -1}
        },
        {
            "$limit": 10
        },
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
    return jsonify({
        "query": "most_active_users",
        "count": len(results),
        "data": serialize(results)
    })

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

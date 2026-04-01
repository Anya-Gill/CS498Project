# check_db.py
import os
from dotenv import load_dotenv
import pymongo

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["eurovision"]
col = db["tweets"]

count = col.count_documents({})
print(f"Tweets loaded: {count:,}")

# Show a sample tweet to confirm data looks right
sample = col.find_one({}, {"text": 1, "user.screen_name": 1, "created_at": 1, "_id": 0})
print(f"Sample tweet: {sample}")
# CS498Project

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```
### 2. Configure Env Vars
Create a .env file in the root directory and add the mongoDB connection string:

```bash
MONGO_URI="mongodb+srv://<db_username>:<db_password>@cluster0.xyjlce2.mongodb.net/?appName=Cluster0"
```

### 3. Download data from Kaggle
1. Download Eurovision 10.json from https://www.kaggle.com/datasets/patrickjoan/twitter-data-from-2018-eurovision-final/data?select=Eurovision10.json

2. Create a /data folder in the project root and place downloaded file into that folder.

### 4. Usage 

To load a single dataset:

```bash
python load_tweets.py data/Eurovision10.json
```
To check data added:

```bash
python check_db.py
```
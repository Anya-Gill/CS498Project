# CS498Project

## Setup Instructions
### In the VM
#### 1. Clone the repo 
```bash
git clone https://github.com/Anya-Gill/CS498Project.git
cd CS498Project
```

#### 2. Install dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv git -y
```

#### 3. Set up a virtual environment 
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Create your .env file with your Mongo URI
Create a .env file in the root directory and add the mongoDB connection string:

```bash
MONGO_URI="mongodb+srv://<db_username>:<db_password>@cluster0.xyjlce2.mongodb.net/?appName=Cluster0"
```

#### 5. Run the server
```bash
python app.py
```
### Locally:
#### 1. Clone the repo
```bash
git clone https://github.com/Anya-Gill/CS498Project.git
cd CS498Project
cd local
```

#### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors requests
```

### To run interface locally:
#### Run:
```bash
python launcher.py
```

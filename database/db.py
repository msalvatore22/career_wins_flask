import os
from pymongo import MongoClient
from dotenv import load_dotenv 

load_dotenv()

user = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER")
mongo_database = os.getenv("MONGO_CLUSTER")

connection_str = f"mongodb+srv://{user}:{password}@{mongo_cluster}/{mongo_database}?retryWrites=true&w=majority"

cluster = MongoClient(connection_str)

db = cluster["career_wins_flask"]


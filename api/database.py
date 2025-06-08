import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv() 

MONGO_DETAILS = os.getenv("MONGO_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client[DB_NAME]

user_collection = database.get_collection("users")
analysis_collection = database.get_collection("analyses")
from pg8000.native import Connection
from dotenv import load_dotenv
import os

load_dotenv('.env')

def connect_to_db():
    return Connection(
        user=os.getenv("LOCAL_USER"),
        password=os.getenv("LOCAL_PASSWORD"),
        database=os.getenv("LOCAL_DATABASE"),
        host=os.getenv("LOCAL_HOST"),
        port=int(os.getenv("LOCAL_PORT"))
    )
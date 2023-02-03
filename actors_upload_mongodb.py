import pymongo
import json
from pymongo import MongoClient

client = pymongo.MongoClient("mongodb+srv://mry2745:nlplab1pw@cluster0.tmoqg.mongodb.net/imdb") #change to imdb
db = client["imdb"] # database name: imdb
collection = db["actors"] # collection name: actors
requesting = []

with open(r"actors.json") as file:
    file_data = json.load(file)

# Inserting the loaded data in the Collection
# if JSON contains data more than one entry
# insert_many is used else insert_one is used
if isinstance(file_data, list):
    collection.insert_many(file_data) 
else:
    collection.insert_one(file_data)

# result = collection.bulk_write(requesting)
client.close()
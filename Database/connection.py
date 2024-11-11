# import sys
# print(sys.executable)
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import pymongo
import os

load_dotenv()
MONGODB_CONNECTION = os.getenv("MONGODB")

def connect_to_mongo():
    try:
        CONNECTION_STRING = MONGODB_CONNECTION
        
        client = MongoClient(CONNECTION_STRING) 
        db = client['Signature_Matching']
        print("Successfully Connected to MongoDB")
        return db
    except errors.ConnectionError as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    

def data_store(db, documents):
    try:
        collection = db['tbl_signatures']
        # Check if index exists on _id and person_name
        if 'person_name_1_id_1' not in collection.index_information():
            db['tbl_signatures'].create_index([('person_name', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)])
            db['tbl_signatures'].create_index([('person_name', pymongo.ASCENDING)])

        results = collection.insert_many(documents)
        if results:
            print("The images have been successfully saved.")
            return True 
        else:
            return False 
    except errors.PyMongoError as e:
        print(f"Error while saving images in MongoDB: {e}")
        return False 


def fetch_signatures(db, person_name):
    try:
        collection = db['tbl_signatures']
        documents = list(collection.find({'person_name': person_name}, {'signature': 1, '_id': 0}))
  
        if documents:
            print(f"The signatures of {person_name} have been fetched successfully.")
            return documents 
        else:
            print(f"No images found for {person_name}")
            return None
    except errors.PyMongoError as e:
        print(f"Error when fetching images from MongoDB: {e}")
        return None

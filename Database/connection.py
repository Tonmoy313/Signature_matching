# import sys
# print(sys.executable)
from pymongo import MongoClient, errors

def connect_to_mongo():
    try:
        CONNECTION_STRING = "mongodb+srv://abdullahalmahmudcse007:5s3XzQhtxtsA5zGt@cluster0.q78iz.mongodb.net"
        
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
        documents = list(collection.find({'person_name': person_name}))  
        if documents:
            print(f"The signatures of {person_name} have been fetched successfully.")
            return documents 
        else:
            print(f"No images found for {person_name}")
            return None
    except errors.PyMongoError as e:
        print(f"Error when fetching images from MongoDB: {e}")
        return None

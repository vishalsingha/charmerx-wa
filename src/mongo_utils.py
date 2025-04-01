import os
import time
import pymongo
from datetime import datetime
from dotenv import load_dotenv
source_code_location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(f'{source_code_location}/.env')

MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
MONGO_CLUSTER = os.environ.get('MONGO_CLUSTER', "charmerchatcluster.qfrux.mongodb.net")
DB_NAME = os.environ.get('MONGO_DB_NAME', "whatsappDB")
COLLECTION_NAME = os.environ.get('MONGO_COLLECTION', "messages")

# Connection String (Ensure you replace <dbname> with your actual DB name)
MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{DB_NAME}?retryWrites=true&w=majority"



class MongoDBStorage:
    def __init__(self):
        # Initialize MongoDB connection
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        
        # Check if collection exists, if not create it
        if COLLECTION_NAME in self.db.list_collection_names():
            print(f"[INFO] : Collection '{COLLECTION_NAME}' already exists.")
        else:
            print(f"[INFO] : Collection '{COLLECTION_NAME}' does not exist. Creating {COLLECTION_NAME} collection...")
            self.db.create_collection(COLLECTION_NAME)
        
        self.collection = self.db[COLLECTION_NAME]
        
        # Create necessary indexes
        self.create_indexes()


    def create_indexes(self):
        """Create MongoDB indexes for faster querying"""
        self.collection.create_index([("SmsMessageSid", pymongo.ASCENDING)], background=True)
        self.collection.create_index([("From", pymongo.ASCENDING)], background=True)
        self.collection.create_index([("To", pymongo.ASCENDING)], background=True)
        self.collection.create_index([("timestamp", pymongo.DESCENDING)], background=True)
        # self.collection.create_index([("sender", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)], background=True)


    def store_message(self, message_data, cx_reply):
        """
        Store a WhatsApp chat message in MongoDB.
        :param message_data: Dictionary containing message details
        """
        try:
            transformed_data = message_data.copy()

            if 'ProfileName' in transformed_data:
                del transformed_data['ProfileName']
            if 'WaId' in transformed_data:
                del transformed_data['WaId']
            if 'ApiVersion' in transformed_data:
                del transformed_data['ApiVersion']
            transformed_data['cx_reply'] = cx_reply
            transformed_data['timestamp'] = time.time()
            # Insert the document
            result = self.collection.insert_one(transformed_data)
            print(f"[INFO] : Message stored with ID: {result.inserted_id}")

        except Exception as e:
            print(f"Error during saving message: {e}")

    def get_user_history(self, user_id):
        """
        Fetch the 3 most recent messages based on 'From' and 'timestamp'.
        :param user_id: The 'From' field value representing the user
        :return: List of recent messages
        """

        try:
            recent_messages = list(self.collection.find({"From": user_id})
                                   .sort("timestamp", pymongo.ASCENDING)
                                   .limit(3))
            return recent_messages

        except Exception as e:
            print(f"Error fetching user history: {e}")
            return []


    

# Example usage
if __name__ == "__main__":
    # Initialize MongoDB Storage
    mongo_storage = MongoDBStorage()
    print('hi')

    data = mongo_storage.get_user_history("whatsapp:+918175847395")
    print(data)


    
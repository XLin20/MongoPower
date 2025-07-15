import json
from pymongo import MongoClient
import os
import uuid # Import the uuid module

def import_json_to_mongodb(file_path, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    """
    Imports data from a JSON file into a MongoDB collection.

    Args:
        file_path (str): The path to the JSON file.
        db_name (str): The name of the database.
        collection_name (str): The name of the collection.
        mongo_uri (str): The MongoDB connection URI.
    """
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        document_id = os.path.splitext(file_path)[0]

        try : 
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            if isinstance(file_data, list):
                # Generate aunique document/object Id: filename + UUID for each document
                file_data["_id"] = document_id +"_"+str(uuid.uuid4())
                # If the JSON is a list of objects, use insert_many
                result = collection.insert_many(file_data)
                print(f"Successfully inserted {len(result.inserted_ids)} documents from {file_path}")
            elif isinstance(file_data, dict):
                # Generate aunique document/object Id: filename + UUID for each document
                file_data["_id"] = document_id +"_"+str(uuid.uuid4())
                # If the JSON is a single object, use insert_one
                result = collection.insert_one(file_data)
                print(f"Successfully inserted 1 document (ID: {result.inserted_id}) from {file_path}")
            else:
                print(f"Unsupported JSON format: {type(file_data)}. Expected a list or a dictionary.")
        except json.JSONDecodeError:
            print(f"Error parsing JSON in '{file_path}'. Skipping.")
        except Exception as e:
            print(f"An error occurred while processing '{file_path}': {e}")
    #
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    # example JSON file and database/collection names
    json_file = "Texas2k_series24_case4_2024lowload.rawx"
    database_name = "power_data"
    collection_name = "power_model"
    # Example usage
    import_json_to_mongodb(json_file, database_name, collection_name)
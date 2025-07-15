# main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
import json
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client: Optional[MongoClient] = None

def get_mongo_client():
    """Initializes and returns the MongoDB client, handling connection errors."""
    global client
    if client is None:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print(f"Successfully connected to MongoDB at {MONGO_URI}")
        except (ConnectionFailure, InvalidURI) as e:
            client = None
            raise HTTPException(status_code=500, detail=f"Could not connect to MongoDB: {e}")
    return client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown of the MongoDB connection."""
    print("FastAPI app startup...")
    get_mongo_client()
    yield
    print("FastAPI app shutdown...")
    if client:
        client.close()
        print("MongoDB connection closed.")

app = FastAPI(
    title="MongoDB Interaction API",
    description="API for interacting with MongoDB, including data editing and change logging.",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_doc_by_id(db: Any, collection_name: str, doc_id: str) -> Optional[Dict]:
    """Helper to find a document by its ID, trying both ObjectId and string."""
    collection = db[collection_name]
    query_id = doc_id
    try:
        query_id = ObjectId(doc_id)
    except Exception:
        pass
    return collection.find_one({"_id": query_id})

def log_change(db: Any, collection_name: str, doc_id: str, action: str, old_content: Optional[Dict], new_content: Optional[Dict]):
    """Creates a log entry for a document change."""
    logs_collection = db["change_logs"]
    log_entry = {
        "timestamp": datetime.datetime.utcnow(),
        "action": action,
        "db_name": db.name,
        "collection_name": collection_name,
        "document_id": str(doc_id),
        "old_content": old_content,
        "new_content": new_content,
    }
    logs_collection.insert_one(log_entry)

@app.get("/api/connect", summary="Check MongoDB Connection")
async def check_connection():
    try:
        get_mongo_client().admin.command('ping')
        return {"status": "success", "message": "Connected to MongoDB"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update_document", summary="Update an Existing Document")
async def update_document(data: Dict[str, Any]):
    db_name = data.get('db_name')
    collection_name = data.get('collection_name')
    doc_id = data.get('_id')
    new_content = data.get('document_content')

    if not all([db_name, collection_name, doc_id, new_content]):
        raise HTTPException(status_code=400, detail="Missing required fields for update.")

    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    
    old_document = get_doc_by_id(db, collection_name, doc_id)
    if not old_document:
        raise HTTPException(status_code=404, detail="Document to update not found.")

    new_content['_id'] = old_document['_id']
    
    result = db[collection_name].replace_one({"_id": old_document['_id']}, new_content)

    if result.modified_count == 1:
        log_change(db, collection_name, doc_id, "UPDATE", old_document, new_content)
        return {"status": "success", "message": "Document updated successfully."}
    else:
        raise HTTPException(status_code=500, detail="Failed to update document.")

@app.post("/api/save_document_as_new", summary="Save Document as a New Entry")
async def save_document_as_new(data: Dict[str, Any]):
    db_name = data.get('db_name')
    collection_name = data.get('collection_name')
    document_content = data.get('document_content')
    original_document = data.get('original_document') # Get the full original document from the request

    if not all([db_name, collection_name, document_content, original_document]):
        raise HTTPException(status_code=400, detail="Missing required fields for saving.")

    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    collection = db[collection_name]

    if '_id' in document_content:
        del document_content['_id']

    result = collection.insert_one(document_content)
    new_id = result.inserted_id

    # Use the full original document for logging the diff
    log_change(db, collection_name, str(new_id), "CREATE_FROM_EDIT", original_document, document_content)
    
    return json.loads(dumps({"status": "success", "message": "Document saved as new.", "new_id": new_id}))

@app.post("/api/get_logs", summary="Get Change Logs")
async def get_logs(data: Dict[str, Any]):
    db_name = data.get('db_name')
    collection_name = data.get('collection_name')
    doc_id = data.get('document_id')

    if not db_name:
        raise HTTPException(status_code=400, detail="Database name is required.")

    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    
    if "change_logs" not in db.list_collection_names():
        return {"status": "success", "logs": []}

    query = {"db_name": db_name}
    if collection_name:
        query["collection_name"] = collection_name
    if doc_id:
        query["document_id"] = doc_id

    logs = list(db["change_logs"].find(query).sort("timestamp", -1).limit(50))
    return json.loads(dumps({"status": "success", "logs": logs}))

@app.get("/api/get_databases", summary="Get All Database Names")
async def get_databases():
    mongo_client = get_mongo_client()
    database_names = mongo_client.list_database_names()
    filtered_databases = [db for db in database_names if db not in ['admin', 'config', 'local']]
    return {"status": "success", "databases": filtered_databases}

@app.post("/api/get_collections", summary="Get Collections in a Database")
async def get_collections(data: Dict[str, str]):
    db_name = data.get('db_name')
    if not db_name:
        raise HTTPException(status_code=400, detail="Database name is required.")
    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    collection_names = [name for name in db.list_collection_names() if name != 'change_logs']
    return {"status": "success", "collections": collection_names}

@app.post("/api/get_document_ids", summary="Get Document IDs in a Collection")
async def get_document_ids(data: Dict[str, str]):
    db_name = data.get('db_name')
    collection_name = data.get('collection_name')
    if not db_name or not collection_name:
        raise HTTPException(status_code=400, detail="DB and Collection name are required.")
    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    collection = db[collection_name]
    document_ids = [str(doc['_id']) for doc in collection.find({}, {'_id': 1}).limit(1000)]
    return {"status": "success", "document_ids": document_ids}

@app.post("/api/query_by_id", summary="Query Document by _id")
async def query_by_id(data: Dict[str, str]):
    db_name = data.get('db_name')
    collection_name = data.get('collection_name')
    doc_id = data.get('_id')
    if not db_name or not collection_name or not doc_id:
        raise HTTPException(status_code=400, detail="All fields are required.")
    mongo_client = get_mongo_client()
    db = mongo_client[db_name]
    document = get_doc_by_id(db, collection_name, doc_id)
    if document:
        return json.loads(dumps({"status": "success", "document": document}))
    else:
        raise HTTPException(status_code=404, detail="Document not found.")

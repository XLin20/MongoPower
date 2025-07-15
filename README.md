#  PowerGrid Data Hub
### Project Description

This project provides a web-based interface for viewing, querying, editing, and saving MongoDB documents, with a built-in change log history. It's designed to manage power system data, allowing users to interact with database collections, inspect document contents (including nested arrays in a tabular format), and track modifications.

## Features
- MongoDB Connection Status: Real-time display of the connection status to the MongoDB instance.

- Database & Collection Browsing: Easily list and select available databases and collections.

- Document ID Listing: Retrieve and select document IDs within a chosen collection.

- Document Viewing & Editing:

    - Load and display full document content.

    - Toggle between a structured table view (for specific nested array data like ```network.buses``` or ```network.caseid.data```) or network.caseid.data) and a raw JSON editor for comprehensive modifications.

- Document Operations:
    - Query by ID: Fetch a specific document using its ```_id```.

    - Query by Field: Search for documents based on a specific field name and value.

    - Save as New Document: Create a new document based on the current content, with an option to append a custom suffix to the _id.

    - Update Existing Document: Modify and save changes to an existing document.

- Change Log History (GitHub-like):

    - A dedicated sidebar displays a history of ```SAVE_AS_NEW``` and ```EDIT``` operations.

    - Each log entry includes a timestamp, action type, document ID, and a custom message.

    - "View Details" button to inspect the ```old_content``` and ```new_content``` of a modification in a modal.

- Log Download: Download the displayed change log history as a JSON file.

## Technologies Used
### Backend (FastAPI)

- Python 3.x: The primary programming language.

- FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

- PyMongo: The official MongoDB driver for Python.

- BSON: Python utilities for BSON (Binary JSON) data.

- python-dotenv: For loading environment variables from a ```.env``` file.

- Uvicorn: An ASGI web server, used to run the FastAPI application.

### Frontend (React in HTML)

- React 17: JavaScript library for building user interfaces.

- HTML5, CSS3, JavaScript (ES6+): Standard web technologies.

- Babel Standalone: Used for in-browser JSX transformation (development only).

### Database

- MongoDB: A NoSQL, document-oriented database.

## Setup Instructions
### Prerequisites
- Git: For cloning the repository.

- Python 3.7+: For the FastAPI backend.

- pip: Python package installer (usually comes with Python).

- MongoDB: A running MongoDB instance (local or remote). You can download and install it from MongoDB Community Server.

1. Clone the Repository
```
    git clone https://github.com/your-username/PowerGrid-Data-Hub.git
    cd PowerGrid-Data-Hub
```

(Replace ```your-username/PowerGrid-Data-Hub``` with your actual GitHub repository path)

2. Backend Setup (FastAPI)

- Create a Python Virtual Environment (Recommended):
```
python -m venv venv
```
- Activate the Virtual Environment:

    - On Windows:
```
    .\venv\Scripts\activate
```
    - On macOS/Linux:
```
    source venv/bin/activate
```
3. Install Dependencies:
```
pip install fastapi uvicorn pymongo python-dotenv
```
4. Create a ```.env``` file:
In the root of your project directory (where ```main.py``` is), create a file named ```.env``` and add your MongoDB connection URI.
```
MONGO_URI="mongodb://localhost:27017/"
```
- Important: If your MongoDB is running on a different host or port, or requires authentication, update this URI accordingly. Do NOT commit this file to public repositories.

5. Run the FastAPI Backend:
```
uvicorn main:app --reload --port 5000
```
The backend will typically run on ```http://127.0.0.1:5000```. Keep this terminal window open.

6. Frontend Setup (React in HTML)
The frontend is a single ```index.html``` file that uses React and Babel directly in the browser for simplicity.

- Open ```index.html```:
Simply open the ```index.html``` file in your web browser (e.g., by double-clicking it in your file explorer).

    - Ensure the ```API_BASE_URL``` in ```index.html``` (around line 117) matches the port your FastAPI backend is running on (e.g.,http://127.0.0.1:5000).

## Usage
1. Connect to MongoDB: The frontend will automatically attempt to connect to the backend and display the MongoDB connection status.

2. Select Database & Collection: Use the left panel to select a database and then a collection. The document IDs in that collection will populate.

3. Load Document: Select a document ID to load its content into the main viewer/editor.

4. Edit Content:

- If the document contains a flat array (like ```network.buses``` or ```network.caseid.data```), it will display in an editable table.

- Use the "Switch to Raw JSON" button to edit the entire document as raw JSON.

5. Save Changes:

- "Update Existing Document": Saves your changes back to the currently loaded document.

- "Save as New Document": Saves the current content as a brand new document. You can optionally provide a suffix for the new ```_id```.

6. View Change History: The right panel will automatically update to show a log of document saves and edits. Click "View Details" to see the old and new content of a change.

7. Download Logs: Click "Download Logs" to save the current log history as a JSON file.

## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue. If you'd like to contribute code, please fork the repository and submit a pull request.

## License
This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE). (You might need to create a LICENSE file in your repository if you don't have one).
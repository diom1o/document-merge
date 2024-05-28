from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import pymongo
from bson.objectid import ObjectId
import dotenv
from flask_caching import Cache

dotenv.load_dotenv()

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

try:
    mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client.documentsDB
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
if not UPLOAD_FOLDER:
    print("UPLOAD_FOLDER environment variable is not set.")
    exit()
    
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def make_cache_key(path: str, args: dict):
    args_str = str(hash(frozenset(args.items())))
    return (path + args_str).encode('utf-8')

def get_document_by_id(doc_id):
    try:
        return db.documents.find_one({"_id": ObjectId(doc_id)})
    except Exception as e:
        print(f"Database error: {e}")
        return None

@app.rpc.method('getVersion')
@cache.memoize(timeout=60)
def get_version(doc_id, version_id):
    document = get_document_by_id(doc_id)
    
    if document:
        for version in document["versions"]:
            if version["version_id"] == version_id:
                version_path = version["path"]
                return send_from_directory(directory=UPLOAD_FOLDER, path=version_path, as_attachment=True)
    return jsonify({"error": "Document or version not found"}), 404

@app.route("/documents/<doc_id>", methods=["POST"])
def upload_document_version(doc_id):
    if "document" not in request.files:
        return jsonify({"error": "No document part"}), 400
    file = request.files["document"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        version_id = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(doc_id, version_id + "_" + filename)
        full_path = os.path.join(UPLOAD_FOLDER, file_path)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)
        
        db.documents.update_one({"_id": ObjectId(doc_id)}, {"$push": {"versions": {"version_id": version_id, "path": file_path}}}, upsert=True)
        
        cache.delete_memoized(get_version, doc_id, version_id)
        return jsonify({"message": "Document version uploaded successfully", "version_id": version_id}), 201

@app.route("/documents/<doc_id>/collaborate", methods=["POST"])
def collaborate_on_document(doc_id):
    content = request.json.get("content", "")
    db.documents.update_one({"_id": ObjectId(doc_id)}, {"$set": {"content": content}}, upsert=True)
    
    return jsonify({"message": "Document updated in real-time"}), 200

@app.route("/documents", methods=["POST"])
def create_document():
    new_doc = {
        "created_at": datetime.now(),
        "versions": [],
        "collaborators": [],
        "content": ""
    }
    
    result = db.documents.insert_one(new_doc)
    
    return jsonify({"message": "Document created", "doc_id": str(result.inserted_id)}), 201

if __name__ == "__main__":
    app.run(debug=True)
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

try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception as e:
    print(f"Error creating upload folder: {e}")
    exit()

def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


@app.route("/documents/<doc_id>/versions/<version_id>", methods=["GET"])
@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_version(doc_id, version_id):
    try:
        document = db.documents.find_one({"_id": ObjectId(doc_id), "versions.version_id": version_id})
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    
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
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            file.save(full_path)
        except Exception as e:
            return jsonify({"error": f"Error saving file: {e}"}), 500
        
        try:
            db.documents.update_one({"_id": ObjectId(doc_id)}, {"$push": {"versions": {"version_id": version_id, "path": file_path}}})
        except Exception as e:
            return jsonify({"error": f"Database error: {e}"}), 500
        
        cache.delete_memoized(get_version, doc_id, version_id)
        return jsonify({"message": "Document version uploaded successfully", "version_id": version_id}), 201

@app.route("/documents/<doc_id>/collaborate", methods=["POST"])
def collaborate_on_document(doc_id):
    content = request.json.get("content", "")
    try:
        db.documents.update_one({"_id": ObjectId(doc_id)}, {"$set": {"content": content}})
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    
    return jsonify({"message": "Document updated in real-time"}), 200

@app.route("/documents", methods=["POST"])
def create_document():
    new_doc = {
        "created_at": datetime.now(),
        "versions": [],
        "collaborators": [],
        "content": ""
    }
    
    try:
        result = db.documents.insert_one(new_doc)
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    
    return jsonify({"message": "Document created", "doc_id": str(result.inserted_id)}), 201

if __name__ == "__main__":
    app.run(debug=True)
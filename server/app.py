from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI", "sqlite:///database.db")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(80))
    created_documents = db.relationship('Document', backref='author', lazy=True)
    documents_shared_with_user = db.relationship('SharedDocument', backref='recipient', lazy=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)  
    version_number = db.Column(db.Integer, default=1)  
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  

class SharedDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_doc_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)  
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  

@app.before_first_request
def initialize_database():  
    db.create_all()

@app.route('/user', methods=['POST'])
def register_user():  
    user_data = request.get_json()
    if 'username' not in user_data or 'password' not in user_data:
        return jsonify({'error': 'Missing username or password'}), 400
    password_hash = generate_password_hash(user_data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), username=user_data['username'], password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/document', methods=['POST'])
def add_document():  
    document_data = request.get_json()
    if 'title' not in document_data or 'content' not in document_data or 'user_id' not in document_data:
        return jsonify({'error': 'Missing title, content, or user_id'}), 400
    new_document = Document(title=document_data['title'], body=document_data['content'], author_id=document_data['user_id'])
    db.session.add(new_document)
    db.session.commit()
    return jsonify({'message': 'Document added successfully'}), 201

@app.route('/document/<int:document_id>', methods=['GET'])
def fetch_document(document_id):  
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404
    document_details = {"title": document.title, "body": document.body, "version": document.version_number}
    return jsonify({'document': document_details}), 200

@app.route('/document/<int:document_id>', methods=['PUT'])
def modify_document(document_id):  
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404
    document_updates = request.get_json()
    if 'title' not in document_updates or 'content' not in document_updates:
        return jsonify({'error': 'Missing title or content'}), 400
    document.title = document_updates['title']
    document.body = document_updates['content']
    document.version_number += 1
    db.session.commit()
    return jsonify({'message': 'Document updated successfully'}), 200

@app.route('/document/share', methods=['POST'])
def share_document_with_user():  
    share_details = request.get_json()
    if 'document_id' not in share_details or 'user_id' not in share_details:
        return jsonify({'error': 'Missing document_id or user_id'}), 400
    new_shared_document = SharedDocument(target_doc_id=share_details['document_id'], recipient_user_id=share_details['user_id'])
    db.session.add(new_shared_document)
    db.session.commit()
    return jsonify({'message': 'Document shared successfully'}), 201

if __name__ == "__main__":
    app.run(debug=True)
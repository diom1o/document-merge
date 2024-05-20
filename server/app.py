from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid  # for public id

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "my_precious_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI", "sqlite:///site.db")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    documents = db.relationship('Document', backref='author', lazy='dynamic')

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, default=1)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created'}), 201

@app.route('/document', methods=['POST'])
def create_document():
    data = request.get_json()
    new_document = Document(title=data['title'], content=data['content'], user_id=data['user_id'])
    db.session.add(new_document)
    db.session.commit()
    return jsonify({'message': 'Document created successfully'}), 201

@app.route('/document/<int:document_id>', methods=['GET'])
def get_document(document_id):
    document = Document.query.filter_by(id=document_id).first()
    if not document:
        return jsonify({'message': 'No document found'}), 404
    document_data = {"title": document.title, "content": document.content, "version": document.version}
    return jsonify({'document': document_data}), 200

@app.route('/document/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    document = Document.query.filter_by(id=document_id).first()
    if not document:
        return jsonify({'message': 'No document found'}), 404
    data = request.get_json()
    document.title = data['title']
    document.content = data['content']
    document.version += 1
    db.session.commit()
    return jsonify({'message': 'Document updated successfully'}), 200

if __name__ == "__main__":
    app.run(debug=True)
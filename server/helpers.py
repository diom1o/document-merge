import os
import uuid
import shutil
from dotenv import load_dotenv
from packaging import version

load_dotenv()

def generate_unique_identifier():
    return str(uuid.uuid4())

def save_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(content)

def get_file_path(doc_id):
    base_path = os.getenv('BASE_STORAGE_PATH', './storage')
    return os.path.join(base_path, f'{doc_id}.txt')

def file_exists(file_path):
    return os.path.exists(file_path)

def delete_file(file_path):
    if file_exists(file_path):
        os.remove(file_path)

def compare_versions(version1, version2):
    v1 = version.parse(version1)
    v2 = version.parse(version2)
    if v1 > v2:
        return 1
    elif v1 < v2:
        return -1
    else:
        return 0

def move_file(source_path, destination_path):
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.move(source_path, destination_path)
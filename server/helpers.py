import os
import uuid
import shutil
from dotenv import load_dotenv
from packaging import version

load_dotenv()

def generate_uuid():
    return str(uuid.uuid4())

def write_content_to_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(content)

def construct_file_path(document_id):
    base_storage_directory = os.getenv('BASE_STORAGE_PATH', './storage')
    return os.path.join(base_storage_directory, f'{document_id}.txt')

def check_file_existence(file_path):
    return os.path.exists(file_path)

def remove_file(file_path):
    if check_file_existence(file_path):
        os.remove(file_path)

def compare_two_versions(version_a, version_b):
    parsed_version_a = version.parse(version_a)
    parsed_version_b = version.parse(version_b)
    if parsed_version_a > parsed_version_b:
        return 1
    elif parsed_version_a < parsed_version_b:
        return -1
    else:
        return 0

def relocate_file(origin_path, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.move(origin_path, target_path)
import os
import uuid
import shutil
from dotenv import load_dotenv
from packaging import version

load_dotenv()

def generate_unique_id():
    """Generates a unique identifier."""
    return str(uuid.uuid4())

def write_text_to_file(file_path, text):
    """Writes given text to a file located at file_path, creating directories as needed."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(text)

def build_document_file_path(document_id):
    """Constructs a file path for a document using its identifier."""
    base_storage_directory = os.getenv('BASE_STORAGE_PATH', './storage')
    return os.path.join(base_storage_directory, f'{document_id}.txt')

def does_file_exist(file_path):
    """Checks if a file exists at the given path."""
    return os.path.exists(file_path)

def delete_file_if_exists(file_path):
    """Deletes a file at the given path if it exists."""
    if does_file_exist(file_path):
        os.remove(file_path)

def compare_version_strings(version_str_a, version_str_b):
    """Compares two version strings and returns 1 if first is greater, -1 if less, and 0 if equal."""
    parsed_version_a = version.parse(version_str_a)
    parsed_version_b = version.parse(version_str_b)
    if parsed_version_a > parsed_version_b:
        return 1
    elif parsed_version_a < parsed_version_b:
        return -1
    else:
        return 0

def move_file_to_new_location(source_path, destination_path):
    """Moves a file from the source path to the destination path, creating directories as needed."""
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.move(source_path, destination_path)
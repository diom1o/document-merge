import os
import uuid
import shutil
from dotenv import load_dotenv
from packaging import version

# Load environment variables
load_dotenv()

def generate_unique_id() -> str:
    """
    Generates a unique UUID string.

    Returns:
        A string representation of a unique UUID.
    """
    return str(uuid.uuid4())

def write_text_to_file(file_path: str, text: str) -> None:
    """
    Writes text to a file specified by the given path.

    Args:
        file_path: The path of the file where the text will be written.
        text: The text to be written to the file.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(text)

def build_document_file_path(document_id: str) -> str:
    """
    Constructs a file path for a document using its ID.

    Args:
        document_id: The unique identifier of the document.

    Returns:
        The file path for the document.
    """
    base_storage_directory = os.getenv('BASE_STORAGE_PATH', './storage')
    return os.path.join(base_storage_directory, f'{document_id}.txt')

def does_file_exist(file_path: str) -> bool:
    """
    Checks if a file exists at the given path.

    Args:
        file_path: The path of the file to check.

    Returns:
        True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)

def delete_file_if_exists(file_path: str) -> None:
    """
    Deletes a file at the specified path if it exists.

    Args:
        file_path: The path of the file to delete.
    """
    if does_file_exist(file_path):
        os.remove(file_path)

def compare_version_strings(version_str_a: str, version_str_b: str) -> int:
    """
    Compares two version strings.

    Args:
        version_str_a: The first version string to compare.
        version_str_b: The second version string to compare.

    Returns:
        1 if version_str_a > version_str_b,
        -1 if version_str_a < version_str_b,
        0 if both are equal.
    """
    parsed_version_a = version.parse(version_str_a)
    parsed_version_b = version.parse(version_str_b)
    if parsed_version_a > parsed_version_b:
        return 1
    elif parsed_version_a < parsed_version_b:
        return -1
    else:
        return 0

def move_file_to_new_location(source_path: str, destination_path: str) -> None:
    """
    Moves a file from a source path to a destination path.

    Args:
        source_path: The current path of the file.
        destination_path: The new path where the file should be moved.
    """
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.move(source_path, destination_path)
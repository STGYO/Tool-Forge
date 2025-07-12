import os
import shutil
import sys
from datetime import datetime

def sort_files_by_type(source_directory):
    """Sorts files into subdirectories based on their file extension."""
    print(f"Sorting files by type in: {source_directory}")
    if not os.path.isdir(source_directory):
        print(f"Error: Source directory not found at '{source_directory}'")
        return

    for filename in os.listdir(source_directory):
        source_path = os.path.join(source_directory, filename)

        # Skip directories
        if os.path.isdir(source_path):
            continue

        # Get file extension
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lstrip('.').lower()

        # Determine destination folder name based on extension (simple mapping)
        if not file_extension:
            destination_folder_name = "No_Extension"
        elif file_extension in ['txt', 'doc', 'docx', 'pdf', 'odt']:
            destination_folder_name = "Documents"
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']:
            destination_folder_name = "Images"
        elif file_extension in ['mp4', 'mkv', 'avi', 'mov', 'wmv']:
            destination_folder_name = "Videos"
        elif file_extension in ['mp3', 'wav', 'flac', 'aac']:
            destination_folder_name = "Audio"
        elif file_extension in ['zip', 'rar', '7z', 'tar', 'gz']:
            destination_folder_name = "Archives"
        elif file_extension in ['exe', 'msi', 'dmg', 'deb', 'rpm']:
            destination_folder_name = "Executables"
        elif file_extension in ['py', 'js', 'html', 'css', 'java', 'c', 'cpp']:
            destination_folder_name = "Code"
        else:
            destination_folder_name = "Others" # Default category

        destination_directory = os.path.join(source_directory, destination_folder_name)

        # Create destination directory if it doesn't exist
        os.makedirs(destination_directory, exist_ok=True)

        destination_path = os.path.join(destination_directory, filename)

        try:
            # Move the file
            shutil.move(source_path, destination_path)
            print(f"Moved '{filename}' to '{destination_folder_name}/'")
        except shutil.Error as e:
            print(f"Error moving '{filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while moving '{filename}': {e}")


def sort_files_by_date(source_directory):
    """Sorts files into subdirectories based on their modified date (Year/Month)."""
    print(f"Sorting files by date in: {source_directory}")
    if not os.path.isdir(source_directory):
        print(f"Error: Source directory not found at '{source_directory}'")
        return

    for filename in os.listdir(source_directory):
        source_path = os.path.join(source_directory, filename)

        # Skip directories
        if os.path.isdir(source_path):
            continue

        try:
            # Get last modified timestamp
            timestamp = os.path.getmtime(source_path)
            modified_date = datetime.fromtimestamp(timestamp)

            # Create destination folder name (Year/Month)
            destination_folder_name = modified_date.strftime('%Y/%m')

            destination_directory = os.path.join(source_directory, destination_folder_name)

            # Create destination directory if it doesn't exist
            os.makedirs(destination_directory, exist_ok=True)

            destination_path = os.path.join(destination_directory, filename)

            try:
                # Move the file
                shutil.move(source_path, destination_path)
                print(f"Moved '{filename}' to '{destination_folder_name}/'")
            except shutil.Error as e:
                print(f"Error moving '{filename}': {e}")
            except Exception as e:
                print(f"An unexpected error occurred while moving '{filename}': {e}")

        except FileNotFoundError:
             print(f"Warning: File not found (possibly moved by another process): {filename}")
        except Exception as e:
            print(f"An error occurred processing file '{filename}': {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_directory> [--method <type|date>]")
        sys.exit(1)

    source_dir = sys.argv[1]
    method = "type" # Default method

    if len(sys.argv) > 2:
        if sys.argv[2] == "--method" and len(sys.argv) > 3:
            method = sys.argv[3].lower()
        else:
            print("Usage: python main.py <source_directory> [--method <type|date>]")
            sys.exit(1)

    if method == "type":
        sort_files_by_type(source_dir)
    elif method == "date":
        sort_files_by_date(source_dir)
    else:
        print(f"Error: Unknown method '{method}'. Use 'type' or 'date'.")
        print("Usage: python main.py <source_directory> [--method <type|date>]")
        sys.exit(1)

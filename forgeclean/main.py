import os
import sys

def get_folder_size(folder_path):
    """Calculates the total size of a folder in bytes."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # Skip if it is symbolic link to avoid infinite loops
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except FileNotFoundError:
        print(f"Warning: Could not access directory {folder_path}")
        return 0
    except Exception as e:
        print(f"An error occurred while calculating size for {folder_path}: {e}")
        return 0
    return total_size

def analyze_disk_usage(directory_path):
    """Analyzes disk usage in the specified directory and lists top 10 largest folders."""
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at '{directory_path}'")
        return

    print(f"Analyzing disk usage in: {directory_path}")

    folder_sizes = {}
    try:
        # Analyze top-level subdirectories
        for entry_name in os.listdir(directory_path):
            entry_path = os.path.join(directory_path, entry_name)
            if os.path.isdir(entry_path):
                size_bytes = get_folder_size(entry_path)
                folder_sizes[entry_path] = size_bytes

        # Sort folders by size in descending order
        sorted_folders = sorted(folder_sizes.items(), key=lambda item: item[1], reverse=True)

        print("\n--- Folder Sizes ---")
        for folder, size_bytes in sorted_folders:
            size_mb = size_bytes / (1024 * 1024) # Convert bytes to MB
            print(f"{folder}: {size_mb:.2f} MB")

        print("\n--- Top 10 Largest Folders ---")
        if sorted_folders:
            for i, (folder, size_bytes) in enumerate(sorted_folders[:10]):
                size_mb = size_bytes / (1024 * 1024) # Convert bytes to MB
                print(f"{i+1}. {folder}: {size_mb:.2f} MB")
        else:
            print("No subdirectories found or analyzed.")

    except Exception as e:
        print(f"An unexpected error occurred during analysis: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory_path>")
        sys.exit(1)

    directory_to_analyze = sys.argv[1]
    analyze_disk_usage(directory_to_analyze)

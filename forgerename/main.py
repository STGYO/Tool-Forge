import os
import re
import argparse
import sys

def rename_files(directory, prefix=None, suffix=None, regex_pattern=None, regex_replacement=None, preview=False):
    """
    Renames files in the specified directory based on the provided options.

    Args:
        directory (str): The path to the directory containing the files.
        prefix (str, optional): Text to add to the beginning of the filename.
        suffix (str, optional): Text to add to the end of the filename.
        regex_pattern (str, optional): Regular expression pattern to search for.
        regex_replacement (str, optional): Replacement string for the regex pattern.
        preview (bool, optional): If True, only show the proposed changes without renaming.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory not found at '{directory}'")
        return

    print(f"Processing directory: {directory}")
    if preview:
        print("Running in PREVIEW mode. No files will be renamed.")

    try:
        for filename in os.listdir(directory):
            old_path = os.path.join(directory, filename)

            # Skip directories
            if os.path.isdir(old_path):
                continue

            new_filename = filename

            # Apply regex first if provided
            if regex_pattern and regex_replacement is not None:
                try:
                    new_filename = re.sub(regex_pattern, regex_replacement, new_filename)
                except re.error as e:
                    print(f"Error applying regex to '{filename}': {e}")
                    continue

            # Apply prefix
            if prefix:
                new_filename = prefix + new_filename

            # Apply suffix
            if suffix:
                # Insert suffix before the last dot (file extension) if it exists
                name, ext = os.path.splitext(new_filename)
                new_filename = name + suffix + ext

            new_path = os.path.join(directory, new_filename)

            if old_path != new_path:
                if preview:
                    print(f"'{filename}' -> '{new_filename}'")
                else:
                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed '{filename}' to '{new_filename}'")
                    except OSError as e:
                        print(f"Error renaming '{filename}' to '{new_filename}': {e}")
            else:
                # No change needed
                pass

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk file renamer tool.")
    parser.add_argument("directory", help="The path to the directory containing the files.")
    parser.add_argument("--prefix", help="Add a prefix to each filename.", default=None)
    parser.add_argument("--suffix", help="Add a suffix to each filename.", default=None)
    parser.add_argument("--regex", nargs=2, metavar=('PATTERN', 'REPLACEMENT'),
                        help="Use a regular expression pattern to find and replace parts of the filename.")
    parser.add_argument("--preview", action="store_true", help="Show the proposed changes without actually renaming files.")

    args = parser.parse_args()

    regex_pattern = args.regex[0] if args.regex else None
    regex_replacement = args.regex[1] if args.regex else None

    # Basic validation for regex
    if args.regex and (not regex_pattern or regex_replacement is None):
         print("Error: --regex requires both a pattern and a replacement string.")
         sys.exit(1)

    # Ensure at least one renaming option is provided
    if not args.prefix and not args.suffix and not args.regex:
        print("Error: At least one renaming option (--prefix, --suffix, or --regex) must be provided.")
        parser.print_help()
        sys.exit(1)


    rename_files(
        args.directory,
        prefix=args.prefix,
        suffix=args.suffix,
        regex_pattern=regex_pattern,
        regex_replacement=regex_replacement,
        preview=args.preview
    )

import os

IGNORE = {
    "ObjectDetection\\abno"
          }

def ignore(root):
    for item in IGNORE:
        if item in root:
            return True
    return False


def collect_files(directory):
    """Recursively collect files in a directory, grouping by extensions."""
    data_files = []
    extensions_to_group = {'.png', '.jpg', '.txt'}  # Add more extensions if needed

    for root, dirs, files in os.walk(directory):
        if ignore(root):
            continue

        extension_counts = {}
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in extensions_to_group:
                extension_counts[ext] = extension_counts.get(ext, 0) + 1

        # Add grouped paths for extensions with multiple files
        for ext, count in extension_counts.items():
            if count > 0:
                rel_path = os.path.relpath(root, directory)
                data_files.append((os.path.join(root, f'*{ext}'), os.path.join(directory , rel_path)))

    return data_files

# Example usage
if __name__ == "__main__":
    directory = "ObjectDetection"
    files = collect_files(directory)
    for src, dest in files:
        print(f"('{src}', '{dest}'),")
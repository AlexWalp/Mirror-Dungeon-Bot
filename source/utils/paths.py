import os, sys

try:
    BASE_PATH = sys._MEIPASS
except:
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


ASSETS_DIR = os.path.join(BASE_PATH,"ImageAssets/UI")

def collect_png_paths(base_dir):
    path_dict = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".png"):
                name = os.path.splitext(file)[0]
                if name in path_dict:
                    raise ValueError(f"Duplicate image name detected: {name}")
                full_path = os.path.join(root, file).replace("\\", "/")
                path_dict[name] = full_path
    return path_dict

PTH = collect_png_paths(ASSETS_DIR)
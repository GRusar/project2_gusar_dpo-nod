
import json
import os

DATA_PATH = "data"
META_FP = os.path.join(DATA_PATH, "db_meta.json")
os.makedirs(DATA_PATH, exist_ok=True)

def load_metadata(filepath) -> dict:
    try:
        with open(filepath, 'r') as f:
            try: 
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    except FileNotFoundError as e:
        print(f"Error loading metadata from {filepath}: {e}")
        return {}

def save_metadata(filepath, data) -> None:
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f)
    except IOError as e:
        print(f"Error saving metadata to {filepath}: {e}")

def load_table_data(table_name):
    path = os.path.join(DATA_PATH, f"{table_name}.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    
def save_table_data(table_name, data) -> None:
    path = os.path.join(DATA_PATH, f"{table_name}.json")
    try:
        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error saving table data to {table_name}.json: {e}")

def delete_table_file(table_name) -> None:
    path = os.path.join(DATA_PATH, f"{table_name}.json")
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as e:
        print(f"Error deleting table file {table_name}.json: {e}")
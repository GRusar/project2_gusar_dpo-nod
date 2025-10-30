
import json
from .engine import DATA_PATH

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

def load_table_data(table_name) -> dict:
    try:
        with open(f"{DATA_PATH}{table_name}.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Table data file {table_name}.json not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {table_name}.json.")
        return {}
    
def save_table_data(table_name, data) -> None:
    try:
        with open(f"{DATA_PATH}{table_name}.json", 'w') as f:
            json.dump(data, f)
    except IOError as e:
        print(f"Error saving table data to {table_name}.json: {e}")
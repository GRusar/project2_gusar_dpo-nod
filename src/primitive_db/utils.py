
import json


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
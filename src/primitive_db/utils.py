
import json
import os

from ..decorators import handle_db_errors

DATA_PATH = "data"
META_FP = os.path.join(DATA_PATH, "db_meta.json")
os.makedirs(DATA_PATH, exist_ok=True)

@handle_db_errors(dict)
def load_metadata(filepath) -> dict:
    with open(filepath, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_metadata(filepath, data) -> None:
    try:
        with open(filepath, "w") as file:
            json.dump(data, file)
    except IOError as error:
        print(f"Ошибка сохранения метаданных в {filepath}: {error}")

@handle_db_errors(list)
def load_table_data(table_name) -> list[dict]:
    path = os.path.join(DATA_PATH, f"{table_name}.json")
    with open(path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_table_data(table_name, data) -> None:
    path = os.path.join(DATA_PATH, f"{table_name}.json")
    try:
        with open(path, "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except IOError as error:
        print(f"Ошибка сохранения данных таблицы в {table_name}.json: {error}")

def delete_table_file(table_name) -> None:
    path = os.path.join(DATA_PATH, f"{table_name}.json")
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as error:
        print(f"Ошибка удаления файла таблицы {table_name}.json: {error}")
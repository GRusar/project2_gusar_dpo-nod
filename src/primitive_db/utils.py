import json
import os

from ..decorators import handle_db_errors
from ..constants import (
    DATA_PATH,
    MSG_META_SAVE_ERROR,
    MSG_TABLE_DELETE_ERROR,
    MSG_TABLE_SAVE_ERROR,
    TABLE_FILE_TEMPLATE,
)

os.makedirs(DATA_PATH, exist_ok=True)

@handle_db_errors(dict)
def load_metadata(filepath) -> dict:
    with open(filepath, "r") as file:
        return json.load(file)

def save_metadata(filepath, data) -> None:
    try:
        with open(filepath, "w") as file:
            json.dump(data, file)
    except IOError as error:
        print(MSG_META_SAVE_ERROR.format(filepath=filepath, error=error))

@handle_db_errors(list)
def load_table_data(table_name) -> list[dict]:
    path = os.path.join(DATA_PATH, TABLE_FILE_TEMPLATE.format(table=table_name))
    with open(path, "r") as file:
        return json.load(file)

def save_table_data(table_name, data) -> None:
    path = os.path.join(DATA_PATH, TABLE_FILE_TEMPLATE.format(table=table_name))
    try:
        with open(path, "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except IOError as error:
        print(
            MSG_TABLE_SAVE_ERROR.format(
                table_file=TABLE_FILE_TEMPLATE.format(table=table_name),
                error=error,
            )
        )

def delete_table_file(table_name) -> None:
    path = os.path.join(DATA_PATH, TABLE_FILE_TEMPLATE.format(table=table_name))
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as error:
        print(
            MSG_TABLE_DELETE_ERROR.format(
                table_file=TABLE_FILE_TEMPLATE.format(table=table_name),
                error=error,
            )
        )

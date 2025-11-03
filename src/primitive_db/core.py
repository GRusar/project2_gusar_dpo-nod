from typing import Any, Callable, Hashable

from ..decorators import confirm_action, handle_db_errors, log_time
from .utils import load_table_data


def create_cacher() -> Callable[[Hashable, Callable[[], Any]], Any]:
    cache: dict[Hashable, Any] = {}

    def cache_result(key: Hashable, value_func: Callable[[], Any]) -> Any:
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    def clear(table_name: str | None = None) -> None:
        if table_name is None:
            cache.clear()
            return
        matching_keys = [
            key
            for key in cache
            if isinstance(key, tuple) and key and key[0] == table_name
        ]
        for cache_key in matching_keys:
            cache.pop(cache_key, None)

    cache_result.clear = clear  # type: ignore[attr-defined]
    return cache_result


_select_cache = create_cacher()


@handle_db_errors()
def create_table(metadata, table_name, columns) -> dict:
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError(
            "Некорректное значение: отсутствуют столбцы. Попробуйте снова."
        )

    valid_types = {"int", "str", "bool"}
    parsed_columns = []
    has_id = False

    for column in columns:
        column_str = column.strip()
        if ":" not in column_str:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        column_name, column_type = [
            part.strip() for part in column_str.split(":", 1)
        ]
        if not column_name or not column_type:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")

        if column_name.lower() == "id":
            has_id = True
            column_name = "ID"
            column_type = "int"

        if column_type not in valid_types:
            raise ValueError(f"Некорректное значение: {column_type}. Попробуйте снова.")
        parsed_columns.append(f"{column_name}:{column_type}")

    if not has_id:
        parsed_columns.insert(0, "ID:int")

    metadata[table_name] = {"table_info": parsed_columns}
    columns_repr = ", ".join(parsed_columns)
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: {columns_repr}'
    )
    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors()
def drop_table(metadata, table_name) -> dict:
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    del metadata[table_name]
    _select_cache.clear(table_name)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata) -> None:
    if not metadata:
        print("Нет доступных таблиц.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def convert_value(value, column_type: str):
    if isinstance(value, str):
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

    if column_type == "int":
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Некорректное значение: {value}. Попробуйте снова."
            )
    if column_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in {"true", "1"}:
                return True
            if lowered in {"false", "0"}:
                return False
        if isinstance(value, int) and value in {0, 1}:
            return bool(value)
        raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")
    return str(value)

@handle_db_errors()
@log_time
def insert(metadata, table_name, values, table_data=None):
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    table_info = metadata[table_name]["table_info"]
    data_without_id = table_info[1:]
    if len(values) != len(data_without_id):
        raise ValueError(
            "Ошибка: Количество значений не соответствует количеству столбцов."
        )

    if table_data is None:
        table_data = []

    existing_ids = [
        row.get("ID")
        for row in table_data
        if isinstance(row, dict) and isinstance(row.get("ID"), int)
    ]
    new_id = max(existing_ids, default=0) + 1

    record = {"ID": new_id}
    for col_def, raw_value in zip(data_without_id, values):
        name_part, type_part = col_def.split(":")
        col_name = name_part.strip()
        col_type = type_part.strip()
        record[col_name] = convert_value(raw_value, col_type)

    table_data.append(record)
    print(
        f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".'
    )
    _select_cache.clear(table_name)
    return table_data


@handle_db_errors(list)
@log_time
def select(table_name: str, where_clause: dict | None = None) -> list[dict]:
    cache_key: Hashable
    if not where_clause:
        cache_key = (table_name, None)
    else:
        cache_key = (table_name, tuple(sorted(where_clause.items())))

    def compute() -> list[dict]:
        table_data = load_table_data(table_name) or []
        if not where_clause:
            return [dict(record) for record in table_data]
        filtered = []
        for record in table_data:
            if all(record.get(key) == value for key, value in where_clause.items()):
                filtered.append(dict(record))
        return filtered

    return _select_cache(cache_key, compute)


@handle_db_errors()
def update(metadata, table_name, table_data, set_values, where_clause=None):
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    schema = metadata[table_name]["table_info"]
    type_map = {}
    for column_def in schema:
        name_part, type_part = column_def.split(":")
        type_map[name_part.strip()] = type_part.strip()

    for column in set_values:
        if column not in type_map:
            raise ValueError(
                f'Некорректное значение: столбца "{column}" не существует.'
            )

    if table_data is None:
        table_data = []

    matched = False
    for record in table_data:
        if where_clause and not all(
            record.get(key) == value for key, value in where_clause.items()
        ):
            continue
        for column, value in set_values.items():
            record[column] = convert_value(value, type_map[column])
        print(
            "Запись с ID={id} в таблице \"{table}\" успешно обновлена.".format(
                id=record.get("ID"),
                table=table_name,
            )
        )
        matched = True

    if not matched:
        print("Нет записей, соответствующих условию.")

    if matched:
        _select_cache.clear(table_name)

    return table_data


@confirm_action("удаление записи")
def delete(table_name, table_data, where_clause=None):
    if table_data is None:
        table_data = []

    remaining = []
    removed = []

    for record in table_data:
        if where_clause and all(
            record.get(key) == value for key, value in where_clause.items()
        ):
            removed.append(record)
            continue
        remaining.append(record)

    if not removed:
        print("Нет записей, соответствующих условию.")
        return table_data

    for record in removed:
        print(
            "Запись с ID={id} успешно удалена из таблицы \"{table}\".".format(
                id=record.get("ID"),
                table=table_name,
            )
        )

    _select_cache.clear(table_name)
    return remaining


@handle_db_errors()
def info(metadata, table_name, table_data):
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    schema = metadata[table_name]["table_info"]
    count = len(table_data) if table_data else 0

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(schema)}")
    print(f"Количество записей: {count}")

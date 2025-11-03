from typing import Any, Callable, Hashable

from ..constants import (
    AVAILABLE_TYPES,
    BOOL_FALSE_LITERALS,
    BOOL_INT_VALUES,
    BOOL_TRUE_LITERALS,
    ID_FIELD,
    ID_NAME,
    ID_TYPE,
    MSG_BAD_COLUMN,
    MSG_BAD_TYPE,
    MSG_NO_COLUMNS,
    MSG_NO_TABLES,
    MSG_RECORD_DELETED,
    MSG_RECORD_INSERTED,
    MSG_RECORD_UPDATED,
    MSG_RECORDS_NO_MATCH,
    MSG_TABLE_COLUMNS,
    MSG_TABLE_COUNT,
    MSG_TABLE_CREATED,
    MSG_TABLE_DROPPED,
    MSG_TABLE_EXISTS,
    MSG_TABLE_INFO,
    MSG_TABLE_NOT_EXISTS,
    MSG_TABLES_PREFIX,
    MSG_TYPE_REPLACED,
    MSG_VALUES_MISMATCH,
    PROMPT_CONFIRM_DELETE,
    PROMPT_CONFIRM_DROP,
    TABLE_INFO_KEY,
    TYPE_BOOL,
    TYPE_INT,
)
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
def create_table(metadata, table_name, columns: list[str]) -> dict:
    if table_name in metadata:
        raise ValueError(MSG_TABLE_EXISTS.format(name=table_name))

    if not columns:
        raise ValueError(MSG_NO_COLUMNS)

    parsed_columns = []
    has_id = False

    for column in columns:
        column_str = column.strip()
        if ":" not in column_str:
            raise ValueError(MSG_BAD_COLUMN.format(column=column))
        column_name, column_type = [
            part.strip() for part in column_str.split(":", 1)
        ]
        if not column_name or not column_type:
            raise ValueError(MSG_BAD_COLUMN.format(column=column))

        if column_name.lower() == ID_NAME.lower():
            has_id = True
            column_name = ID_NAME
            if column_type.lower() != ID_TYPE:
                print(
                    MSG_TYPE_REPLACED.format(
                        id_name=ID_NAME,
                        id_type=ID_TYPE,
                        column_type=column_type,
                    )
                )
            column_type = ID_TYPE

        if column_type not in AVAILABLE_TYPES:
            raise ValueError(MSG_BAD_TYPE.format(value=column_type))
        parsed_columns.append(f"{column_name}:{column_type}")

    if not has_id:
        parsed_columns.insert(0, ID_FIELD)

    metadata[table_name] = {TABLE_INFO_KEY: parsed_columns}
    columns_repr = ", ".join(parsed_columns)
    print(MSG_TABLE_CREATED.format(name=table_name, columns=columns_repr))
    return metadata


@confirm_action(PROMPT_CONFIRM_DROP)
@handle_db_errors()
def drop_table(metadata, table_name) -> dict:
    if table_name not in metadata:
        raise ValueError(MSG_TABLE_NOT_EXISTS.format(name=table_name))

    del metadata[table_name]
    _select_cache.clear(table_name)
    print(MSG_TABLE_DROPPED.format(name=table_name))
    return metadata


def list_tables(metadata) -> None:
    if not metadata:
        print(MSG_NO_TABLES)
        return

    for table_name in metadata:
        print(MSG_TABLES_PREFIX.format(name=table_name))


def convert_value(value, column_type: str):
    if isinstance(value, str):
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

    if column_type == TYPE_INT:
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(MSG_BAD_TYPE.format(value=value))
    if column_type == TYPE_BOOL:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in BOOL_TRUE_LITERALS:
                return True
            if lowered in BOOL_FALSE_LITERALS:
                return False
        if isinstance(value, int) and value in BOOL_INT_VALUES:
            return bool(value)
        raise ValueError(MSG_BAD_TYPE.format(value=value))
    return str(value)

@handle_db_errors()
@log_time
def insert(metadata, table_name, values, table_data=None):
    if table_name not in metadata:
        raise ValueError(MSG_TABLE_NOT_EXISTS.format(name=table_name))

    table_info = metadata[table_name][TABLE_INFO_KEY]
    data_without_id = table_info[1:]
    if len(values) != len(data_without_id):
        raise ValueError(MSG_VALUES_MISMATCH)

    if table_data is None:
        table_data = []

    existing_ids = [
        row.get(ID_NAME)
        for row in table_data
        if isinstance(row, dict) and isinstance(row.get(ID_NAME), int)
    ]
    new_id = max(existing_ids, default=0) + 1

    record = {ID_NAME: new_id}
    for col_def, raw_value in zip(data_without_id, values):
        name_part, type_part = col_def.split(":")
        col_name = name_part.strip()
        col_type = type_part.strip()
        record[col_name] = convert_value(raw_value, col_type)

    table_data.append(record)
    print(
        MSG_RECORD_INSERTED.format(
            id_name=ID_NAME,
            record_id=new_id,
            table=table_name,
        )
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
        raise ValueError(MSG_TABLE_NOT_EXISTS.format(name=table_name))

    schema = metadata[table_name][TABLE_INFO_KEY]
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
            MSG_RECORD_UPDATED.format(
                id_name=ID_NAME,
                record_id=record.get(ID_NAME),
                table=table_name,
            )
        )
        matched = True

    if not matched:
        print(MSG_RECORDS_NO_MATCH)

    if matched:
        _select_cache.clear(table_name)

    return table_data


@confirm_action(PROMPT_CONFIRM_DELETE)
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
        print(MSG_RECORDS_NO_MATCH)
        return table_data

    for record in removed:
        print(
            MSG_RECORD_DELETED.format(
                id_name=ID_NAME,
                record_id=record.get(ID_NAME),
                table=table_name,
            )
        )

    _select_cache.clear(table_name)
    return remaining


@handle_db_errors()
def info(metadata, table_name, table_data):
    if table_name not in metadata:
        raise ValueError(MSG_TABLE_NOT_EXISTS.format(name=table_name))

    schema = metadata[table_name][TABLE_INFO_KEY]
    count = len(table_data) if table_data else 0

    print(MSG_TABLE_INFO.format(name=table_name))
    print(MSG_TABLE_COLUMNS.format(columns=", ".join(schema)))
    print(MSG_TABLE_COUNT.format(count=count))

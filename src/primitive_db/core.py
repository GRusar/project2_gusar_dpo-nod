def create_table(metadata, table_name, columns) -> dict:
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError(
            "Некорректное значение: отсутствуют столбцы. Попробуйте снова."
        )

    valid_types = {"int", "str", "bool"}
    has_id = any(col.split(":")[0].strip().lower() == "id" for col in columns)
    if not has_id:
        columns = ["ID:int"] + columns
    parsed_columns = []

    for column in columns:
        if ":" not in column:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        column_name, column_type = column.split(":")

        if column_type not in valid_types:
            raise ValueError(f"Некорректное значение: {column_type}. Попробуйте снова.")
        parsed_columns.append(f"{column_name}:{column_type}")

    metadata[table_name] = {"table_info": parsed_columns}
    columns_repr = ", ".join(parsed_columns)
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: {columns_repr}'
    )
    return metadata


def drop_table(metadata, table_name) -> dict:
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    del metadata[table_name]
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
    return table_data


def select(table_data, where_clause: dict | None = None):
    if table_data is None:
        table_data = []

    if not where_clause:
        return list(table_data)

    filtered = []
    for record in table_data:
        if all(record.get(key) == value for key, value in where_clause.items()):
            filtered.append(record)
    return filtered

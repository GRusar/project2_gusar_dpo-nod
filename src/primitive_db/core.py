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

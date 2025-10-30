import shlex

import prompt
from prettytable import PrettyTable

from .core import (
    convert_value,
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import (
    parse_delete_tokens,
    parse_insert_tokens,
    parse_select_tokens,
    parse_update_tokens,
    parse_where_condition_tokens,
)
from .utils import (
    delete_table_file,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

FP = "db_meta.json"

def run():
    while True:
        metadata = load_metadata(FP)
        user_input = prompt.string(">>> Введите команду: ")

        args = shlex.split(user_input)
        if not args:
            continue
        command = args[0]
        match command:
            case "create_table":
                if len(args) < 3:
                    invalid_value = " ".join(args[1:]) or command
                    print(f"Некорректное значение: {invalid_value}. Попробуйте снова.")
                    continue
                table_name = args[1]
                columns = args[2:]
                try:
                    metadata = create_table(metadata, table_name, columns)
                    save_metadata(FP, metadata)
                except ValueError as e:
                    print(e)
            case "drop_table":
                if len(args) < 2:
                    invalid_value = " ".join(args[1:]) or command
                    print(f"Некорректное значение: {invalid_value}. Попробуйте снова.")
                    continue
                table_name = args[1]
                try:
                    metadata = drop_table(metadata, table_name)
                    save_metadata(FP, metadata)
                    delete_table_file(table_name)
                except ValueError as e:
                    print(e)
            case "list_tables":
                list_tables(metadata)
            case "insert":
                try:
                    table_name, values = parse_insert_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                try:
                    table_data = load_table_data(table_name)
                    updated = insert(metadata, table_name, values, table_data)
                    save_table_data(table_name, updated)
                except ValueError as e:
                    print(e)
            case "select":
                try:
                    table_name, condition_tokens = parse_select_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                table_info = metadata.get(table_name, {}).get("table_info")
                if not table_info:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                type_map = {}
                headers = []
                for column_def in table_info:
                    name_part, type_part = column_def.split(":")
                    column_name = name_part.strip()
                    headers.append(column_name)
                    type_map[column_name] = type_part.strip()

                where_clause = None
                if condition_tokens:
                    try:
                        where_clause = parse_where_condition_tokens(
                            condition_tokens,
                            type_map,
                        )
                    except ValueError as e:
                        print(e)
                        continue
                table_data = load_table_data(table_name)
                rows = select(table_data, where_clause)

                if not rows:
                    print("Нет записей, соответствующих условию.")
                    continue

                table = PrettyTable()
                table.field_names = headers

                for row in rows:
                    table.add_row([row.get(header) for header in headers])
                print(table)
            case "update":
                try:
                    table_name, set_values, condition_tokens = parse_update_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                table_info = metadata.get(table_name, {}).get("table_info")
                if not table_info:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                type_map = {}
                for column_def in table_info:
                    name_part, type_part = column_def.split(":")
                    type_map[name_part.strip()] = type_part.strip()

                converted_set = {}
                for column, raw_value in set_values.items():
                    if column not in type_map:
                        print(
                            f'Некорректное значение: столбца "{column}" не существует.'
                        )
                        break
                    try:
                        converted_set[column] = convert_value(
                            raw_value,
                            type_map[column],
                        )
                    except ValueError as e:
                        print(e)
                        break
                else:
                    where_clause = None
                    if condition_tokens:
                        try:
                            where_clause = parse_where_condition_tokens(
                                condition_tokens,
                                type_map,
                            )
                        except ValueError as e:
                            print(e)
                            continue

                    table_data = load_table_data(table_name)
                    updated_data = update(
                        metadata,
                        table_name,
                        table_data,
                        converted_set,
                        where_clause,
                    )
                    save_table_data(table_name, updated_data)
            case "delete":
                try:
                    table_name, condition_tokens = parse_delete_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                table_info = metadata.get(table_name, {}).get("table_info")
                if not table_info:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                type_map = {
                    column.split(":")[0].strip(): column.split(":")[1].strip()
                    for column in table_info
                }

                table_data = load_table_data(table_name)
                try:
                    where_clause = parse_where_condition_tokens(
                        condition_tokens,
                        type_map,
                    )
                except ValueError as e:
                    print(e)
                    continue
                updated_data = delete(table_name, table_data, where_clause)
                save_table_data(table_name, updated_data)
            case "info":
                if len(args) < 2:
                    print("Некорректное значение: info. Попробуйте снова.")
                    continue

                table_name = args[1]
                table_data = load_table_data(table_name)
                try:
                    info(metadata, table_name, table_data)
                except ValueError as e:
                    print(e)
            case "exit":
                print("Выход из программы.")
                break

            case "help":
                print_help()
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")

def welcome():
    print_help()

def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
        " - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение>"
        " - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help- справочная информация\n")

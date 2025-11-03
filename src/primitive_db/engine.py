import shlex

import prompt
from prettytable import PrettyTable

from ..constants import (
    COMMANDS,
    HELP_ALIGNMENT,
    META_FP,
    MSG_EXIT,
    MSG_INVALID_INFO,
    MSG_INVALID_VALUE,
    MSG_PARSE_ERROR,
    MSG_PARSE_HINT,
    MSG_RECORDS_NO_MATCH,
    MSG_TABLE_NOT_EXISTS,
    MSG_UNKNOWN_COLUMN,
    MSG_UNKNOWN_COMMAND,
    PROMPT_INPUT,
    TABLE_INFO_KEY,
)
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


def run():
    """Запускает основной цикл взаимодействия с пользователем."""
    while True:
        metadata = load_metadata(META_FP)
        user_input = prompt.string(PROMPT_INPUT)

        try:
            args = shlex.split(user_input)
        except ValueError as error:
            print(MSG_PARSE_ERROR.format(error=error))
            print(MSG_PARSE_HINT)
            continue
        if not args:
            continue
        command = args[0]

        match command:
            case "create_table":
                if len(args) < 3:
                    invalid_value = " ".join(args[1:]) or command
                    print(MSG_INVALID_VALUE.format(value=invalid_value))
                    continue
                table_name = args[1]
                columns = args[2:]
                updated_metadata = create_table(metadata, table_name, columns)
                if updated_metadata is None:
                    continue
                metadata = updated_metadata
                save_metadata(META_FP, metadata)
            case "drop_table":
                if len(args) < 2:
                    invalid_value = " ".join(args[1:]) or command
                    print(MSG_INVALID_VALUE.format(value=invalid_value))
                    continue
                table_name = args[1]
                updated_metadata = drop_table(metadata, table_name)
                if updated_metadata is None:
                    continue
                metadata = updated_metadata
                save_metadata(META_FP, metadata)
                delete_table_file(table_name)
            case "list_tables":
                list_tables(metadata)
            case "insert":
                try:
                    table_name, values = parse_insert_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                table_data = load_table_data(table_name)
                updated_data = insert(metadata, table_name, values, table_data)
                if updated_data is None:
                    continue
                save_table_data(table_name, updated_data)
            case "select":
                try:
                    table_name, condition_tokens = parse_select_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                table_info = metadata.get(table_name, {}).get(TABLE_INFO_KEY)
                if not table_info:
                    print(MSG_TABLE_NOT_EXISTS.format(name=table_name))
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
                rows = select(table_name, where_clause)

                if rows is None:
                    continue
                if not rows:
                    print(MSG_RECORDS_NO_MATCH)
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

                table_info = metadata.get(table_name, {}).get(TABLE_INFO_KEY)
                if not table_info:
                    print(MSG_TABLE_NOT_EXISTS.format(name=table_name))
                    continue

                type_map = {}
                for column_def in table_info:
                    name_part, type_part = column_def.split(":")
                    type_map[name_part.strip()] = type_part.strip()

                converted_set = {}
                for column, raw_value in set_values.items():
                    if column not in type_map:
                        print(MSG_UNKNOWN_COLUMN.format(column=column))
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
                    if updated_data is None:
                        continue
                    save_table_data(table_name, updated_data)
            case "delete":
                try:
                    table_name, condition_tokens = parse_delete_tokens(args)
                except ValueError as e:
                    print(e)
                    continue

                table_info = metadata.get(table_name, {}).get(TABLE_INFO_KEY)
                if not table_info:
                    print(MSG_TABLE_NOT_EXISTS.format(name=table_name))
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
                if updated_data is None:
                    continue
                save_table_data(table_name, updated_data)
            case "info":
                if len(args) < 2:
                    print(MSG_INVALID_INFO)
                    continue

                table_name = args[1]
                table_data = load_table_data(table_name)
                info(metadata, table_name, table_data)
            case "exit":
                print(MSG_EXIT)
                break

            case "help":
                print_help()
            case _:
                print(MSG_UNKNOWN_COMMAND.format(command=command))

def welcome():
    """Выводит приветственное сообщение и справку по командам."""
    print_help()


def print_help(commands: dict[str, str] = COMMANDS) -> None:
    """
    Выводит справку по доступным командам.
    """
    print("\nДоступные команды:")
    for command, description in commands.items():
        print(command.ljust(HELP_ALIGNMENT + 2, " ") + description)

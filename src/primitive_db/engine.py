import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

FP = "db_meta.json"
DATA_PATH = "data/"

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
                except ValueError as e:
                    print(e)
            case "list_tables":
                list_tables(metadata)
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
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

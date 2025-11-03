import os

DATA_PATH = "data"
META_FILENAME = "db_meta.json"
META_FP = os.path.join(DATA_PATH, META_FILENAME)

ID_NAME = "ID"
TYPE_INT = "int"
TYPE_STR = "str"
TYPE_BOOL = "bool"
ID_TYPE = TYPE_INT
ID_FIELD = f"{ID_NAME}:{ID_TYPE}"

AVAILABLE_TYPES = {TYPE_INT, TYPE_STR, TYPE_BOOL}
BOOL_TRUE_LITERALS = {"true", "1"}
BOOL_FALSE_LITERALS = {"false", "0"}
BOOL_INT_VALUES = {0, 1}

COMMANDS = {
    "create_table <имя> <столбец:тип> ...": (
        "создать таблицу (столбец ID:int добавляется автоматически)"
    ),
    "list_tables": "показать список всех таблиц",
    "drop_table <имя>": "удалить таблицу",
    "insert into <имя> values (...)": "добавить запись",
    "select from <имя>": "вывести все записи",
    "select from <имя> where поле = значение": "вывести записи по условию",
    "update <имя> set поле = значение where ...": "обновить записи по условию",
    "delete from <имя> where поле = значение": "удалить записи по условию",
    "info <имя>": "показать схему и количество записей",
    "help": "показать эту справку",
    "exit": "выйти из программы",
}
HELP_ALIGNMENT = max(len(command) for command in COMMANDS)

CONFIRM_YES = {"y"}

MSG_TABLE_EXISTS = 'Ошибка: Таблица "{name}" уже существует.'
MSG_NO_COLUMNS = "Некорректное значение: отсутствуют столбцы. Попробуйте снова."
MSG_BAD_COLUMN = "Некорректное значение: {column}. Попробуйте снова."
MSG_BAD_TYPE = "Некорректное значение: {value}. Попробуйте снова."
MSG_UNKNOWN_COLUMN = 'Некорректное значение: столбца "{column}" не существует.'
MSG_INVALID_VALUE = "Некорректное значение: {value}. Попробуйте снова."
MSG_TYPE_REPLACED = (
    'Столбец "{id_name}" поддерживает только тип {id_type}. '
    'Значение "{column_type}" заменено на "{id_type}".'
)
MSG_TABLE_NOT_EXISTS = 'Ошибка: Таблица "{name}" не существует.'
MSG_NO_TABLES = "Нет доступных таблиц."
MSG_TABLE_CREATED = (
    'Таблица "{name}" успешно создана со столбцами: {columns}'
)
MSG_TABLE_DROPPED = 'Таблица "{name}" успешно удалена.'
MSG_RECORD_INSERTED = (
    'Запись с {id_name}={record_id} успешно добавлена в таблицу "{table}".'
)
MSG_RECORD_UPDATED = (
    'Запись с {id_name}={record_id} в таблице "{table}" успешно обновлена.'
)
MSG_RECORDS_NO_MATCH = "Нет записей, соответствующих условию."
MSG_RECORD_DELETED = (
    'Запись с {id_name}={record_id} успешно удалена из таблицы "{table}".'
)
MSG_TABLE_INFO = "Таблица: {name}"
MSG_TABLE_COLUMNS = "Столбцы: {columns}"
MSG_TABLE_COUNT = "Количество записей: {count}"
MSG_EXIT = "Выход из программы."
MSG_UNKNOWN_COMMAND = "Функции {command} нет. Попробуйте снова."
MSG_INVALID_INFO = "Некорректное значение: info. Попробуйте снова."
MSG_VALUES_MISMATCH = (
    "Ошибка: Количество значений не соответствует количеству столбцов."
)
MSG_TABLES_PREFIX = "- {name}"
TABLE_INFO_KEY = "table_info"

PROMPT_CONFIRM_DROP = "удаление таблицы"
PROMPT_CONFIRM_DELETE = "удаление записи"
PROMPT_CONFIRM_TEMPLATE = 'Вы уверены, что хотите выполнить "{action}"? [y/n]: '
PROMPT_INPUT = ">>> Введите команду: "

MSG_DB_ERROR = "Ошибка: Таблица или столбец {error} не найден."
MSG_UNEXPECTED_ERROR = "Произошла непредвиденная ошибка: {error}"
MSG_ACTION_CANCELLED = "Действие '{action}' отменено пользователем."
MSG_FUNCTION_TIME = "Функция {func_name} выполнилась за {elapsed:.3f} секунд."
MSG_PARSE_ERROR = "Не удалось разобрать команду ({error})."
MSG_PARSE_HINT = "Проверьте синтаксис и кавычки."

TABLE_FILE_TEMPLATE = "{table}.json"
MSG_META_SAVE_ERROR = "Ошибка сохранения метаданных в {filepath}: {error}"
MSG_TABLE_SAVE_ERROR = (
    "Ошибка сохранения данных таблицы в {table_file}: {error}"
)
MSG_TABLE_DELETE_ERROR = (
    "Ошибка удаления файла таблицы {table_file}: {error}"
)

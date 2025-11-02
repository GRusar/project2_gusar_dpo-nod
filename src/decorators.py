from functools import wraps
from json import JSONDecodeError

import prompt


def handle_db_errors(missing_default=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError:
                if callable(missing_default):
                    return missing_default()
                return missing_default
            except JSONDecodeError:
                if callable(missing_default):
                    return missing_default()
                return missing_default
            except KeyError as error:
                print(f"Ошибка: Таблица или столбец {error} не найден.")
            except ValueError as error:
                print(f"Ошибка валидации: {error}")
            except Exception as error:
                print(f"Произошла непредвиденная ошибка: {error}")

        return wrapper

    return decorator


def confirm_action(action_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if confirmation.lower() != "y":
                print(f"Действие '{action_name}' отменено пользователем.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator

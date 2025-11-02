from functools import wraps


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
            except KeyError as e:
                print(f"Ошибка: Таблица или столбец {e} не найден.")
            except ValueError as e:
                print(f"Ошибка валидации: {e}")
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}")

        return wrapper

    return decorator
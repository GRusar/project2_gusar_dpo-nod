import time
from functools import wraps
from json import JSONDecodeError

import prompt

from .constants import (
    CONFIRM_YES,
    MSG_ACTION_CANCELLED,
    MSG_FUNCTION_TIME,
    MSG_DB_ERROR,
    MSG_UNEXPECTED_ERROR,
    PROMPT_CONFIRM_TEMPLATE,
)


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
                print(MSG_DB_ERROR.format(error=error))
            except ValueError as error:
                print(error)
            except Exception as error:
                print(MSG_UNEXPECTED_ERROR.format(error=error))

        return wrapper

    return decorator


def confirm_action(action_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = prompt.string(
                PROMPT_CONFIRM_TEMPLATE.format(action=action_name)
            )
            if confirmation.lower() not in CONFIRM_YES:
                print(MSG_ACTION_CANCELLED.format(action=action_name))
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        print(
            MSG_FUNCTION_TIME.format(
                func_name=func.__name__,
                elapsed=elapsed_time,
            )
        )
        return result

    return wrapper

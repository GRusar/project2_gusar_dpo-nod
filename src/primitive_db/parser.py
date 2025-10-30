from __future__ import annotations

from .core import convert_value


def _join_tokens(tokens: list[str]) -> str:
    return " ".join(tokens).strip()


def _split_values(segment: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_quotes = False
    quote_char = ""

    for char in segment:
        if char in {'"', "'"}:
            if in_quotes and char == quote_char:
                in_quotes = False
            elif not in_quotes:
                in_quotes = True
                quote_char = char
            current.append(char)
        elif char == "," and not in_quotes:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts

def _split_assignments(segment: str) -> list[str]:
    assignments: list[str] = []
    current: list[str] = []
    saw_equal = False

    index = 0
    length = len(segment)
    while index < length:
        char = segment[index]

        if char == "=":
            saw_equal = True
            current.append(char)
            index += 1
            continue

        if char == "," and saw_equal:
            remainder = segment[index + 1 :]
            remainder_stripped = remainder.lstrip()
            if remainder_stripped:
                token_end = 0
                while (
                    token_end < len(remainder_stripped)
                    and (
                        remainder_stripped[token_end].isalnum()
                        or remainder_stripped[token_end] == "_"
                    )
                ):
                    token_end += 1
                if token_end:
                    rest = remainder_stripped[token_end:].lstrip()
                    if rest.startswith("="):
                        assignment = "".join(current).strip()
                        if assignment:
                            assignments.append(assignment)
                        current = []
                        saw_equal = False
                        index += 1
                        continue

        current.append(char)
        index += 1

    tail = "".join(current).strip()
    if tail:
        assignments.append(tail)
    return assignments

def parse_insert_tokens(tokens: list[str]) -> tuple[str, list[str]]:
    if len(tokens) < 5:
        raise ValueError("Некорректное значение: insert. Попробуйте снова.")

    if tokens[1].lower() != "into":
        raise ValueError("Некорректное значение: insert. Попробуйте снова.")
    if tokens[3].lower() != "values":
        raise ValueError("Некорректное значение: insert. Попробуйте снова.")

    table_name = tokens[2]
    values_str = _join_tokens(tokens[4:])
    if not values_str.startswith("(") or not values_str.endswith(")"):
        raise ValueError("Некорректное значение: insert. Попробуйте снова.")

    values_segment = values_str[1:-1]
    values = _split_values(values_segment)
    if not values:
        raise ValueError("Некорректное значение: insert. Попробуйте снова.")
    return table_name, values


def parse_select_tokens(tokens: list[str]) -> tuple[str, list[str] | None]:
    if len(tokens) < 3:
        raise ValueError("Некорректное значение: select. Попробуйте снова.")
    if tokens[1].lower() != "from":
        raise ValueError("Некорректное значение: select. Попробуйте снова.")

    table_name = tokens[2]
    if len(tokens) == 3:
        return table_name, None

    if tokens[3].lower() != "where":
        raise ValueError("Некорректное значение: select. Попробуйте снова.")

    condition_tokens = tokens[4:]
    if not condition_tokens:
        raise ValueError("Некорректное значение: WHERE. Попробуйте снова.")
    return table_name, condition_tokens


def parse_where_condition_tokens(
    tokens: list[str],
    type_map: dict[str, str],
) -> dict[str, object]:
    if len(tokens) < 3:
        raise ValueError("Некорректное значение: WHERE. Попробуйте снова.")

    column_name = tokens[0]
    if column_name not in type_map:
        raise ValueError(
            f'Некорректное значение: столбца "{column_name}" не существует.',
        )

    if tokens[1] != "=":
        raise ValueError("Некорректное значение: WHERE. Попробуйте снова.")

    value_tokens = tokens[2:]
    if not value_tokens:
        raise ValueError("Некорректное значение: WHERE. Попробуйте снова.")

    value_raw = _join_tokens(value_tokens)
    converted = convert_value(value_raw, type_map[column_name])
    return {column_name: converted}


def parse_update_tokens(
    tokens: list[str],
) -> tuple[str, dict[str, str], list[str] | None]:
    if len(tokens) < 4:
        raise ValueError("Некорректное значение: update. Попробуйте снова.")

    table_name = tokens[1]
    if tokens[2].lower() != "set":
        raise ValueError("Некорректное значение: update. Попробуйте снова.")

    where_index = None
    for index, token in enumerate(tokens):
        if token.lower() == "where":
            where_index = index
            break

    if where_index is None:
        set_tokens = tokens[3:]
        condition_tokens = None
    else:
        set_tokens = tokens[3:where_index]
        condition_tokens = tokens[where_index + 1 :]

    assignments_raw = _split_assignments(_join_tokens(set_tokens))
    if not assignments_raw:
        raise ValueError("Некорректное значение: SET. Попробуйте снова.")

    set_values: dict[str, str] = {}
    for assignment in assignments_raw:
        if "=" not in assignment:
            raise ValueError("Некорректное значение: SET. Попробуйте снова.")
        column_part, value_part = assignment.split("=", 1)
        column_name = column_part.strip()
        value_raw = value_part.strip()
        if not column_name or not value_raw:
            raise ValueError("Некорректное значение: SET. Попробуйте снова.")
        set_values[column_name] = value_raw

    return table_name, set_values, condition_tokens


def parse_delete_tokens(tokens: list[str]) -> tuple[str, list[str]]:
    if len(tokens) < 5:
        raise ValueError("Некорректное значение: delete. Попробуйте снова.")

    if tokens[1].lower() != "from":
        raise ValueError("Некорректное значение: delete. Попробуйте снова.")

    table_name = tokens[2]
    if tokens[3].lower() != "where":
        raise ValueError("Некорректное значение: delete. Попробуйте снова.")

    condition_tokens = tokens[4:]
    if not condition_tokens:
        raise ValueError("Некорректное значение: WHERE. Попробуйте снова.")

    return table_name, condition_tokens

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML

# ❌ Forbidden SQL keywords (structural, not cosmetic)
FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "replace",
    "merge",
    "attach",
    "detach",
    "pragma",
    "vacuum",
}

# ❌ Forbidden clauses even inside SELECT
FORBIDDEN_SELECT_KEYWORDS = {
    "into",        # SELECT INTO
    "outfile",     # MySQL-style export
    "dumpfile",
}


def _is_single_select_statement(statement: Statement) -> bool:
    """
    Ensure the statement is exactly one SELECT.
    """
    has_select = False

    for token in statement.tokens:
        if token.ttype is DML and token.value.upper() == "SELECT":
            has_select = True
        elif token.ttype is DML:
            return False  # INSERT / UPDATE / DELETE etc.

    return has_select


def _contains_forbidden_keywords(statement: Statement) -> str | None:
    """
    Check for forbidden keywords anywhere in the statement.
    """
    for token in statement.flatten():
        if token.ttype is Keyword:
            value = token.value.lower()
            if value in FORBIDDEN_KEYWORDS:
                return value
            if value in FORBIDDEN_SELECT_KEYWORDS:
                return value
    return None


def _has_limit(statement: Statement) -> bool:
    """
    Check whether a LIMIT clause exists.
    """
    for token in statement.tokens:
        if token.ttype is Keyword and token.value.upper() == "LIMIT":
            return True
    return False


def _inject_limit(sql: str, limit: int = 100) -> str:
    """
    Append LIMIT if missing.
    """
    return f"{sql.rstrip(';')} LIMIT {limit};"


def validate_sql(sql: str, limit: int = 100):
    """
    Validate and harden SQL.
    Returns (is_valid, result_sql_or_reason).
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query"

    parsed = sqlparse.parse(sql)

    # 1️⃣ Exactly one statement
    if len(parsed) != 1:
        return False, "Only single SQL statements are allowed"

    statement = parsed[0]

    # 2️⃣ Must be SELECT-only
    if not _is_single_select_statement(statement):
        return False, "Only SELECT queries are allowed"

    # 3️⃣ Block forbidden keywords
    forbidden = _contains_forbidden_keywords(statement)
    if forbidden:
        return False, f"Forbidden SQL keyword detected: {forbidden.upper()}"

    # 4️⃣ Enforce LIMIT
    final_sql = sql.strip()
    if not _has_limit(statement):
        final_sql = _inject_limit(final_sql, limit)

    return True, final_sql

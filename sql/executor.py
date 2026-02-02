import sqlite3

def execute_sql(db_path: str, sql: str):
    """
    Execute a validated SELECT query on a SQLite database.

    Returns:
        columns: list[str]
        rows: list[tuple]
    """
    if not db_path:
        raise ValueError("Database path not provided")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
    finally:
        conn.close()

    return columns, rows

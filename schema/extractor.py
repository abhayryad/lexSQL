import sqlite3

def extract_schema(db_path: str) -> dict:
    """
    Extract tables, columns, primary keys, and foreign keys
    from a SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get user-defined tables only
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}

    for table in tables:
        # Column info
        cursor.execute(f"PRAGMA table_info({table});")
        columns_raw = cursor.fetchall()

        columns = []
        for col in columns_raw:
            columns.append({
                "name": col[1],
                "type": col[2],
                "nullable": not bool(col[3]),
                "primary_key": bool(col[5])
            })

        # Foreign key info
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        foreign_keys_raw = cursor.fetchall()

        foreign_keys = []
        for fk in foreign_keys_raw:
            foreign_keys.append({
                "from_column": fk[3],
                "to_table": fk[2],
                "to_column": fk[4]
            })

        schema[table] = {
            "columns": columns,
            "foreign_keys": foreign_keys
        }

    conn.close()
    return schema

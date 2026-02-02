def format_schema(schema: dict) -> list[str]:
    """
    Convert schema dict into a list of per-table documents.
    """
    docs = []

    for table, meta in schema.items():
        lines = [f"Table: {table}"]

        for col in meta["columns"]:
            line = f"- {col['name']} ({col['type']})"
            if col["primary_key"]:
                line += " [PRIMARY KEY]"
            lines.append(line)

        if meta["foreign_keys"]:
            lines.append("Foreign Keys:")
            for fk in meta["foreign_keys"]:
                lines.append(
                    f"- {fk['from_column']} → "
                    f"{fk['to_table']}.{fk['to_column']}"
                )

        docs.append("\n".join(lines))

    return docs

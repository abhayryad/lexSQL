EXPLAIN_RESULTS_PROMPT = """
You are a data analyst explaining SQL query results to a non-technical user.

SQL Query:
{sql}

Query Results (sample rows):
{results}

Explain clearly:
- What the results show
- Any important trend or insight
- Keep it simple and concise
"""

import gradio as gr

# -------- Schema --------
from schema.extractor import extract_schema
from schema.formatter import format_schema

# -------- RAG --------
from rag.embeddings import get_embedding_model
from rag.index import build_schema_index, retrieve_relevant_schema

# -------- LLM --------
from llm.hf_client import get_llm
from llm.sql_prompt import SQL_GENERATION_PROMPT
from llm.explain_prompt import EXPLAIN_RESULTS_PROMPT

# -------- SQL --------
from sql.validator import validate_sql
from sql.executor import execute_sql


# In-memory session state (single-user for now)
state = {}


# =========================
# Database Upload
# =========================
def upload_db(file):
    if file is None:
        return "❌ No file uploaded.", ""

    try:
        schema = extract_schema(file.name)
        schema_docs = format_schema(schema)

        embeddings = get_embedding_model()
        vectorstore = build_schema_index(schema_docs, embeddings)

        state["db_path"] = file.name
        state["vectorstore"] = vectorstore

        return "✅ Database uploaded and indexed.", "\n\n".join(schema_docs)

    except Exception as e:
        return f"❌ Error reading database: {str(e)}", ""


# =========================
# Question → SQL → Execute → Explain
# =========================
def run_query(question: str):
    if "vectorstore" not in state:
        return "❌ Please upload a database first.", None, ""

    # 1️⃣ Retrieve relevant schema (RAG)
    schema_context = retrieve_relevant_schema(
        state["vectorstore"],
        question
    )

    # 2️⃣ Initialize LLM safely
    try:
        llm = get_llm()
    except Exception as e:
        return (
            "⚠️ LLM not active.\n"
            "Set HF_TOKEN and restart the app.\n\n"
            f"Details: {str(e)}",
            None,
            ""
        )

    # 3️⃣ Generate SQL (CORRECT: invoke)
    sql_prompt = SQL_GENERATION_PROMPT.format(
        schema_context=schema_context,
        question=question
    )

    sql = llm.invoke(sql_prompt).strip()

    # 4️⃣ Validate SQL
    is_valid, reason = validate_sql(sql)
    if not is_valid:
        return f"❌ SQL BLOCKED: {reason}\n\nGenerated SQL:\n{sql}", None, ""

    # 5️⃣ Execute SQL
    try:
        columns, rows = execute_sql(state["db_path"], sql)
        results = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return f"❌ SQL execution error:\n{str(e)}", None, ""

    # 6️⃣ Explain results (CORRECT: invoke)
    try:
        explain_prompt = EXPLAIN_RESULTS_PROMPT.format(
            sql=sql,
            results=results[:5]  # sample only
        )
        explanation = llm.invoke(explain_prompt).strip()
    except Exception:
        explanation = "⚠️ Explanation unavailable."

    return sql, results, explanation


# =========================
# Gradio UI
# =========================
with gr.Blocks(title="lexSQL") as demo:
    gr.Markdown("# 🧠 lexSQL")
    gr.Markdown(
        "Upload a SQLite database and ask business questions.\n\n"
        "🔒 SQL is generated safely, validated, executed, and explained."
    )

    # Upload section
    db_file = gr.File(
        label="Upload SQLite .db file",
        file_types=[".db"]
    )

    status = gr.Textbox(label="Status")
    schema_box = gr.Textbox(label="Indexed Schema", lines=15)

    db_file.upload(
        fn=upload_db,
        inputs=db_file,
        outputs=[status, schema_box]
    )

    # Query section
    question = gr.Textbox(
        label="Ask a business question",
        placeholder="e.g. Show total revenue by customer"
    )

    generated_sql = gr.Textbox(label="Generated SQL", lines=6)

    results_table = gr.Dataframe(
        label="Query Results",
        interactive=False
    )

    explanation_box = gr.Textbox(
        label="Explanation (Plain English)",
        lines=6
    )

    question.submit(
        fn=run_query,
        inputs=question,
        outputs=[generated_sql, results_table, explanation_box]
    )

demo.launch()

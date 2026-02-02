import gradio as gr

def upload_db(file):
    if file is None:
        return "No file uploaded"
    return f"Uploaded file: {file.name}"

with gr.Blocks(title="lexSQL") as demo:
    gr.Markdown("#lexSQL")
    gr.Markdown("Upload a SQLite database to begin.")

    db_file = gr.File(
        label="Upload SQLite .db file",
        file_types=[".db"]
    )

    status = gr.Textbox(label="Status")

    db_file.upload(
        fn=upload_db,
        inputs=db_file,
        outputs=status
    )

demo.launch()

import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


def get_llm():
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN environment variable not set")

    # Base HF endpoint (chat-only model)
    endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        task="conversational",
        huggingfacehub_api_token=hf_token,
        max_new_tokens=512,
        temperature=0.1,
    )

    # Wrap as a CHAT model (this is the missing piece)
    llm = ChatHuggingFace(llm=endpoint)

    return llm

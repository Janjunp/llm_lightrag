import ollama
import subprocess
from mytool.query_paper import extract_references_from_pdf
import subprocess
import os
import subprocess

import asyncio
import inspect
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc

from mytool.get_papper import fetch_paper_from_reference

def init():
    # 在同一 shell 中执行多条命令
    commands = "export OLLAMA_MODELS=/mnt/workspace/.cache/ollama/model;ollama serve"
    process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_references(references_text):

    with open("prompt/prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    content = prompt + references_text
    references = ollama.generate(
        model="qwen2.5:7b-8k",  # 使用的模型名称
        prompt=content
        )

    return references   #参考文献


def insert(working_dir, path):

    rag = LightRAG(
    working_dir=working_dir,
    llm_model_func=ollama_model_complete,
    llm_model_name="qwen2.5:7b-8k",
    llm_model_max_async=4,
    llm_model_max_token_size=32784,
    llm_model_kwargs={"host": "http://localhost:11434", "options": {"num_ctx": 32784}},
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(texts, embed_model="nomic-embed-text", host="http://localhost:11434"),
        )
    )

    with open(path, "r", encoding="utf-8") as f:
         rag.insert(f.read())

    return rag

if __name__ == "__main__":

    working_dir = "./dickens"   #知识图谱的储存路径

    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    init()

    pdf_path = "twostream.pdf"  # 替换为实际文件路径
    references_text, txt_path= extract_references_from_pdf(pdf_path) #references_text是提取的参考文献文本，

    references = get_references(references_text)

    print(references.response)
    rag = insert(working_dir, txt_path)

    #mode="hybrid" #搜索模式一共有"naive"、"local"、"global"、"hybrid"四种
    
    print(rag.query("介绍一下论文的主要内容", param=QueryParam(mode="hybrid")))


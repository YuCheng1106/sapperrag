import json
from sapperrag import DocumentReader
from sapperrag.config.kg_infer import openai_api_parameter
from sapperrag.llm.oai.chat_openai import ChatOpenAI
from sapperrag.embedding.openai_embed import OpenAIEmbedding
from sapperrag.index.graph.cli import GraphIndexer
from sapperrag.index.text.cli import TextIndexer
from dotenv import load_dotenv
import os

load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
openai_key_list = json.loads(os.getenv("OPENAI_KEY_LIST"))
openai_api_parameter.openai_api_key_list = openai_key_list


def run_indexer(dir_path, save_path, index_type):
    local_file_reader = DocumentReader()
    chatgpt = ChatOpenAI(openai_key, base_url)
    embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")

    if index_type == "graph":
        indexer = GraphIndexer(chatgpt, embeder, local_file_reader)
    else:
        indexer = TextIndexer(chatgpt, embeder, local_file_reader)
    return indexer.build_index(dir_path, save_path)



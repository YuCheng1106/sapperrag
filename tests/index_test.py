from sapperrag import DocumentReader, TextFileChunker, run_indexer
from dotenv import load_dotenv
import os

load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 确保环境变量正确加载
if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")

# local_file_reader = DocumentReader()
# read_result = local_file_reader.read(dir_path="../input")
# text_file_chunker = TextFileChunker()
# chunk_result = text_file_chunker.chunk(read_result.documents)

run_indexer("../input", "graph")



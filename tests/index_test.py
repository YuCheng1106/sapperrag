from sapperrag import DocumentReader, TextFileChunker, run_indexer, ChunkEmbedder
from sapperrag.model import save_model_to_csv
from dotenv import load_dotenv
import os
from sapperrag.embedding import OpenAIEmbedding, LocalModelEmbedding


load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 确保环境变量正确加载
if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")

local_file_reader = DocumentReader()
read_result = local_file_reader.read(dir_path="../input")
save_model_to_csv(read_result, "../output/document.csv")

text_file_chunker = TextFileChunker()
chunk_result = text_file_chunker.chunk(read_result)
save_model_to_csv(chunk_result, "../output/text_chunks.csv")

# embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")
embeder = LocalModelEmbedding("D:\workplace\\agentdy\\app\common\RAGModuleBase\embedding\model")
chunk_embedder = ChunkEmbedder(embeder)
embed_result = chunk_embedder.embed(chunk_result)
chunk_embedder.save("../output/")

print("index success!!!")




from sapperrag import DocumentReader, TextFileChunker, run_indexer, ChunkEmbedder

from dotenv import load_dotenv
import os
from sapperrag.embedding import OpenAIEmbedding, LocalModelEmbedding


load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 确保环境变量正确加载
if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")
# from sapperrag import ConvertToolFactory
# factory = ConvertToolFactory()
# markdown_content = factory.convert_file("D:\workplace\sapperrag\input\上饶市科技局需国家层面协调事项的报告.docx")
# print(markdown_content)


local_file_reader = DocumentReader()
read_result = local_file_reader.read(dir_path="../input")
local_file_reader.save("../output")

text_file_chunker = TextFileChunker()
chunk_result = text_file_chunker.chunk(read_result)
text_file_chunker.save("../output")

# embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")
embeder = LocalModelEmbedding("D:\workplace\\agentdy\\app\common\RAGModuleBase\embedding\model")
chunk_embedder = ChunkEmbedder(embeder)
embed_result = chunk_embedder.embed(chunk_result)
chunk_embedder.save("../output")

print("index success!!!")

# run_indexer("D:\workplace\sapperrag\input", "D:\workplace\sapperrag\output1", "text")

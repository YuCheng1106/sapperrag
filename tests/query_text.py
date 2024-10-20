from dotenv import load_dotenv
import os
from sapperrag.embedding import OpenAIEmbedding, LocalModelEmbedding
from sapperrag.llm.oai import ChatOpenAI
from sapperrag.retriver import TextSearch, TextSearchContext

load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")


if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")


# embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")
embeder = LocalModelEmbedding("D:\workplace\\agentdy\\app\common\RAGModuleBase\embedding\model")

chatgpt = ChatOpenAI(openai_key, base_url)
context_builder = TextSearchContext(dir_path="../output", text_embedder=embeder)
search_engine = TextSearch(context_builder, chatgpt)

query = "高新技术企业和科技型中小企业快速增长"
context = context_builder.build_context(query)
results = search_engine.search(query)

print(results)

from dotenv import load_dotenv
import os
from sapperrag.embedding import OpenAIEmbedding, LocalModelEmbedding
from sapperrag.llm.oai import ChatOpenAI
from sapperrag.model import load_document, load_text_chunks, load_embeddings
from sapperrag.retriver import TextSearch, TextSearchContext

load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")


if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")


# embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")
embeder = LocalModelEmbedding("D:\workplace\\agentdy\\app\common\RAGModuleBase\embedding\model")

read_data = load_document("../output/document.csv")
chunk_data = load_text_chunks("../output/text_chunks.csv")
vector_db = load_embeddings("../output/text_vector_db.npy.npz")

chatgpt = ChatOpenAI(openai_key, base_url)

context_builder = TextSearchContext(chunk_data, vector_db, embeder)

search_engine = TextSearch(context_builder, chatgpt)

query = "高新技术企业和科技型中小企业快速增长"

results = search_engine.search(query)

print(results)




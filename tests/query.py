import json
import os
from dotenv import load_dotenv
from sapperrag.llm.oai.chat_openai import ChatOpenAI
from sapperrag.retriver.structured_search.local_search.mixed_context import LocalSearchMixedContext
from sapperrag.retriver.structured_search.local_search.search import LocalSearch
from sapperrag.embedding.openai_embed import OpenAIEmbedding
from sapperrag.model.model_load import load_relationships, load_entities, load_text_chunks, load_community
# 加载环境变量
load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 定义文件路径
root_path = '../input/kg/'
graph_path = os.path.join(root_path, 'graph.json')
entities_path = os.path.join(root_path, 'entities.json')
relations_path = os.path.join(root_path, 'relations.json')

# 初始化文本嵌入器
embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")

# 定义查询
query = "c"

# 初始化 ChatOpenAI 对象
chatgpt = ChatOpenAI(openai_key, base_url)

entities = load_entities("../output/entities.csv")
relationships = load_relationships("../output/relationships.csv")
text_chunks = load_text_chunks("../output/text_chunks.csv")
community_reports = load_community("../output/communities.csv")
# 初始化 LocalSearchMixedContext 对象
context_builder = LocalSearchMixedContext(entities, relationships, text_chunks, community_reports, embeder.embed)

# 初始化 LocalSearch 对象
search_engine = LocalSearch(context_builder, chatgpt)

# 执行搜索
results = search_engine.search(query)
print("Search Results:", results)

import json
import os
from dotenv import load_dotenv
from sapperrag.llm.oai.chat_openai import ChatOpenAI
from sapperrag.retriver.structured_search.local_search.mixed_context import LocalSearchMixedContext
from sapperrag.retriver.structured_search.local_search.search import LocalSearch
from sapperrag.embedding.openai_embed import OpenAIEmbedding

# 加载环境变量
load_dotenv("D:\workplace\AIKG\.env")
openai_key = os.getenv("OPENAI_KEY")

# 确保环境变量正确加载
if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")

# 定义文件路径
root_path = '../input/kg/'
graph_path = os.path.join(root_path, 'graph.json')
entities_path = os.path.join(root_path, 'entities.json')
relations_path = os.path.join(root_path, 'relations.json')


# 读取实体
with open(entities_path, 'r', encoding='utf-8') as file:
    entities = json.load(file)

# 读取关系
with open(relations_path, 'r', encoding='utf-8') as file:
    relations = json.load(file)

# 初始化文本嵌入器
text_embedder = OpenAIEmbedding()

# 定义查询
query = "什么是进程"

# 初始化 ChatOpenAI 对象
chatgpt = ChatOpenAI(openai_key)

# 初始化 LocalSearchMixedContext 对象
context_builder = LocalSearchMixedContext(entities, relations, text_embedder.embed)

# 初始化 LocalSearch 对象
search_engine = LocalSearch(context_builder, chatgpt)

# 执行搜索
results = search_engine.search(query)
print("Search Results:", results)

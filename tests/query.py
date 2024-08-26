import json
import os
import csv
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
query = "国家课程、地方课程和校本课程在小学课程体系中的地位和作用是什么？如何实现三者的有机结合？"

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


# def generate_answer(query: str):
#     # 定义查询
#
#     # 初始化 ChatOpenAI 对象
#     chatgpt = ChatOpenAI(openai_key, base_url)
#
#     entities = load_entities("../output/entities.csv")
#     relationships = load_relationships("../output/relationships.csv")
#     text_chunks = load_text_chunks("../output/text_chunks.csv")
#     community_reports = load_community("../output/communities.csv")
#     # 初始化 LocalSearchMixedContext 对象
#     context_builder = LocalSearchMixedContext(entities, relationships, text_chunks, community_reports, embeder.embed)
#
#     # 初始化 LocalSearch 对象
#     search_engine = LocalSearch(context_builder, chatgpt)
#
#     # 执行搜索
#     results = search_engine.search(query)
#     return results
#

# # 打开现有的CSV文件并逐行读取
# with open('questions_and_answers.csv', 'r', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
#
#     # 准备写入更新后的CSV文件
#     with open('questions_and_answers_updated.csv', 'w', newline='', encoding='utf-8') as csvfile_out:
#         fieldnames = reader.fieldnames + ['answer']  # 确保包含 'answer' 列
#         writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
#
#         writer.writeheader()
#
#         # 逐行处理每个query并生成answer
#         for row in reader:
#             query = row['query']
#             answer = generate_answer(query)
#             row['answer'] = answer
#             writer.writerow(row)
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import List, AnyStr, Dict, Tuple
from sapperrag.model.entity import Entity
from sapperrag.model.relationship import Relationship
from uuid import uuid4
from ....index.graph.infering.data_handling import DataProcessor

DataProcessor = DataProcessor()


def graph_parse(kg):
    # 初始化实体和关系的列表
    relations = []
    entities = []
    # 用于存储实体的字典，用于去重
    entity_dict = {}

    # 处理数据
    for item in kg:
        directional_entity = item.get("DirectionalEntity")
        directed_entity = item.get("DirectedEntity")
        relation = item.get("Relation")

        # 处理方向性实体
        def process_entity(entity):
            entity_key = json.dumps(entity, sort_keys=True, ensure_ascii=False)
            if entity_key not in entity_dict:
                entity_id = str(uuid4())
                entity["id"] = entity_id
                entity_dict[entity_key] = entity

                attributes = entity.get("Attributes", {})
                text_chunk_id = [attributes.pop("source_id", None)]

                entities.append(Entity(
                    id=entity_id,
                    type=entity["Type"],
                    title=attributes.get("name", ""),
                    text_chunk_ids=text_chunk_id,
                    attributes=attributes,
                    short_id=entity_id
                ))
            return entity_dict[entity_key]["id"]

        # 处理 directional_entity 和 directed_entity
        source_id = process_entity(directional_entity) if directional_entity else None
        target_id = process_entity(directed_entity) if directed_entity else None

        # 处理关系
        if relation and source_id and target_id:
            rela_id = str(uuid4())
            relations.append(Relationship(
                id=rela_id,
                source=source_id,
                target=target_id,
                short_id=rela_id,
                type=relation["Type"],
                name=relation["Name"],
                attributes=relation.get("Attributes", {}),
            ))

    return entities, relations


class TriplesExtractor:
    """
    该类依赖于三个基本组件：文件加载器、AI执行器和知识图谱模式提取器：FileLoader, AIExecutor, EntityExtractor
    提供了三种不同的方法来从文本中提取三元组：单线程提取、多线程提取和线程池提取：
    extract: 单线程提取
    extract_with_multithread: 多线程提取
    extract_with_thread_pool: 线程池提取
    """

    def __init__(
            self,
            ai_executor,
    ):
        """
        :param file_loader: 用于加载各类文本文件
        :param ai_executor: AI执行单元，作为提取三元组的引擎
        """
        self.ai_executor = ai_executor

    def process_chunk_with_thread_pool(self, text_chunk, kg_schema, schema_definition: Dict = None):
        """
        分别每个线程提取三元组，传入对应的文本块和知识架构。
        :param text_chunk: 文本块
        :param kg_schema: 知识架构 -> 列表
        :param schema_definition: 知识架构定义
        :return: 返回三元组列表
        """
        # 使用线程池处理文本块，可自定义线程数
        try:
            # 请求元素传入
            response = self.ai_executor.execute(step="knowledge_extraction", text_chunk=text_chunk, kg_schema=kg_schema,
                                                schema_definition=schema_definition)
            if response:
                return response
            else:
                return []
        except Exception as e:
            # 如果出现线程异常，打印异常信息，并返回空列表
            if str(e) == "Unsupported llm API Call":
                # 如果出现不支持的调用方法异常，抛出异常，终止程序。如果不是这个异常，放弃该线程并继续执行。
                raise ValueError("Unsupported llm API Call")
            print(f"Error processing the threading for the text chunk: {str(e)}")
            return []

    def extract(self, text_chunks: list, kg_schema: List, schema_definition: Dict):
        """
        一般不含结构化信息的内容知识图谱提取的通用方法
        """
        # 加载文本块

        triples = list()
        # 设置线程池的最大线程数
        with ThreadPoolExecutor(max_workers=4) as executor:
            # 将任务分派给线程池
            future_to_chunk = {
                executor.submit(self.process_chunk_with_thread_pool, chunk.text, kg_schema, schema_definition): chunk.id
                for chunk in text_chunks}
            # as_completed 生成器会在未来的任务完成时产生future
            for future in tqdm(as_completed(future_to_chunk),
                               total=len(text_chunks), desc=f"Processing text chunks from"):
                # 获取未来线程的结果
                result = future.result()
                # 获取对应文本块的索引
                index = future_to_chunk[future]
                if result:
                    # 如果结果不为空，将结果添加到三元组列表中
                    result = DataProcessor.add_source_id_to_entities(result, source_id=index)
                    triples.extend(result)
        # # 将提取的三元组存储到指定的目录当中： 注意先后顺序
        # triples = DataProcessor.add_source_for_entity(triples, "text_chunks")
        # 返回前去重
        kg = DataProcessor.deduplicate_triples(triples)
        entities, relationships = graph_parse(kg)
        return entities, relationships

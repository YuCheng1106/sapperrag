import json
from dataclasses import asdict, is_dataclass, fields, MISSING
from typing import List, Any, Type, get_origin, get_args, Union

import pandas as pd

from sapperrag import DocumentReader, TextFileChunker, SchemaConstructor
from sapperrag.config.kg_infer import openai_api_parameter
from sapperrag.index.graph.attribute_embedding import AttributeEmbedder
from sapperrag.index.graph.infering.AIExecutorTool import AIResponseGetter
from sapperrag.index.graph.infering.ai_executor import AIExecutor
from sapperrag.index.graph.infering.triples_extractor import TriplesExtractor
from sapperrag.index.graph.reporting.community_detection import CommunityDetection
from sapperrag.index.graph.reporting.report_generate import CommunityReportGenerator
from sapperrag.llm.base import BaseLLM
from sapperrag.embedding.base import BaseTextEmbedding
from sapperrag.index.base import Indexer
from sapperrag.model.model_load import load_entities, load_relationships, load_text_chunks


def save_dataclasses_to_csv(dataclasses_list: List[Any], csv_file_path: str):
    """
    保存 dataclass 对象的列表到 CSV 文件中。

    Args:
        dataclasses_list (List[Any]): 包含 dataclass 对象的列表。
        csv_file_path (str): 要保存的 CSV 文件路径。
    """
    if not dataclasses_list:
        raise ValueError("The dataclasses_list is empty.")

    # 检查第一个元素是否为 dataclass
    if not is_dataclass(dataclasses_list[0]):
        raise ValueError("Items in the list must be dataclass instances.")

    # 将每个 dataclass 对象转换为字典
    dict_list = [asdict(item) for item in dataclasses_list]

    # 使用 pandas 创建 DataFrame
    df = pd.DataFrame(dict_list)

    # 保存到 CSV
    df.to_csv(csv_file_path, index=False, encoding='utf-8')


def resolve_type(type_hint):
    """将类型提示转换为实际的 Python 类型"""
    if isinstance(type_hint, str):
        # 处理字符串类型提示
        if type_hint == 'str':
            return str
        elif type_hint == 'int':
            return int
        elif type_hint == 'float':
            return float
        elif type_hint == 'bool':
            return bool
        else:
            # raise ValueError(f"Unsupported type hint: {type_hint}")
            return str
    # 处理 Union 和 Optional 类型提示
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        if len(args) == 2 and type(None) in args:
            # 处理 Optional[X]，即 Union[X, None] 形式
            non_none_type = [arg for arg in args if arg is not type(None)][0]
            return non_none_type
        return Union[args]
    return type_hint


def load_dataclasses_from_csv(dataclass_type: Type[Any], csv_file_path: str) -> List[Any]:
    """
    从 CSV 文件加载数据并将其转换为 dataclass 对象的列表。

    Args:
        dataclass_type (Type[Any]): 要创建的 dataclass 类型。
        csv_file_path (str): 包含数据的 CSV 文件路径。

    Returns:
        List[Any]: 包含 dataclass 对象的列表。
    """
    # 读取 CSV 文件为 DataFrame
    df = pd.read_csv(csv_file_path)

    # 获取 dataclass 的字段
    dataclass_fields = {f.name: f for f in fields(dataclass_type)}

    dataclass_list = []
    for _, row in df.iterrows():
        row_data = {}
        for column, value in row.items():
            if column in dataclass_fields:
                field_info = dataclass_fields[column]
                field_type = resolve_type(field_info.type)

                # 检查类型的原始类型（例如 Optional[str] 的原始类型是 Union）
                origin = get_origin(field_type)
                args = get_args(field_type)

                if origin is Union:
                    # 如果是 Optional 或其他 Union 类型
                    if type(None) in args:
                        # 如果是 Optional[T]，则获取第一个非 None 的类型
                        field_type = args[0]
                    else:
                        # 处理其他 Union 类型的情况
                        # 如果 Union 只包含基本类型，尝试逐个类型进行转换
                        for arg in args:
                            try:
                                if arg is not type(value):
                                    value = arg(value)
                                break
                            except (TypeError, ValueError):
                                continue
                elif origin is list and isinstance(value, str):
                    # 如果是列表类型，将字符串值解析成列表
                    value = value.strip("[]").split(", ")
                elif origin is dict and isinstance(value, str):
                    # 如果是字典类型，可以解析 JSON 字符串或自定义格式
                    import json
                    value = json.loads(value)
                elif field_type is not type(value):
                    # 对非复杂类型进行转换，如果类型不匹配
                    value = field_type(value)

            row_data[column] = value

        dataclass_list.append(dataclass_type(**row_data))

    return dataclass_list


class GraphIndexer(Indexer):
    def __init__(self, llm: BaseLLM, embeder: BaseTextEmbedding, local_file_reader):
        super().__init__()
        self.llm = llm
        self.embeder = embeder
        self.local_file_reader = local_file_reader

    def build_index(self, dir_path, save_path, **kwargs):
        read_result = self.local_file_reader.read(dir_path=dir_path)
        text_file_chunker = TextFileChunker()
        chunk_result = text_file_chunker.chunk(read_result.documents)
        # save_dataclasses_to_csv(chunk_result, '../output/source.csv')
        # schema_constructor = SchemaConstructor(text_chunks=chunk_result, llm=self.llm)
        # schema_result = schema_constructor.construct()
        # schema = schema_result.schema
        # definition = schema_result.definition

        # with open("D:\workplace\sapperrag\output\kg_schema.json", 'r', encoding='utf-8') as file:
        #     schema = json.load(file)
        #
        # with open("D:\workplace\sapperrag\output\definition.json", 'r', encoding='utf-8') as file:
        #     definition = json.load(file)

        ai_response_getter = AIResponseGetter(llm_api_parameter=openai_api_parameter)
        ai_executor = AIExecutor(ai_response_getter=ai_response_getter)
        triples_extractor = TriplesExtractor(ai_executor=ai_executor)

        # entities, relationships = triples_extractor.extract(
        #     text_chunks=chunk_result,
        #     kg_schema=schema,
        #     schema_definition=definition)

        # save_dataclasses_to_csv(entities, '../output/entities.csv')
        # save_dataclasses_to_csv(relationships, '../output/relationships.csv')

        entities = load_entities("../output/entities.csv")
        relationships = load_relationships("../output/relationships.csv")
        community_detector = CommunityDetection(max_comm_size=10, max_level=1, seed=5)
        vertices, edges = community_detector.load_data(entities, relationships)
        graph = community_detector.create_graph(vertices, edges)
        communities = community_detector.detect_communities(graph)
        save_dataclasses_to_csv(communities, '../output/communities.csv')
        entities = load_entities("../output/entities.csv", entities=entities, communities=communities)
        save_dataclasses_to_csv(entities, "../output/entities.csv")

        generator = CommunityReportGenerator(llm=self.llm, input_data=communities)
        reports_df = generator.generate_reports()
        save_dataclasses_to_csv(reports_df, '../output/communities.csv')

        embedder = AttributeEmbedder(self.embeder)
        df = embedder.add_attribute_vectors(entities)
        save_dataclasses_to_csv(df, '../output/entities.csv')

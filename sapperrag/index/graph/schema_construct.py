import re
from typing import Optional, Dict, Any
from sapperrag.index.graph.base import BaseConstructor
from jinja2 import Template
from sapperrag.index.graph.promt.schema_construct_prompt import SCHEMA_CONSTRUCTOR, TYPE_DEFINITION, ATTRIBUTES_INFER
from collections import defaultdict
from sapperrag.llm.base import BaseLLM
from sapperrag.model.text_chunk import TextChunk
from sapperrag.index.graph.base import ConstructResult
import asyncio

class SchemaConstructor(BaseConstructor):
    def __init__(self, llm: BaseLLM, text_chunks: list[TextChunk], kg_schema: Optional[Dict[str, Any]] = None,
                 definition: Optional[Dict[str, Any]] = None):
        super().__init__(text_chunks, llm)
        self.definition = definition if definition is not None else {}
        self.kg_schema = kg_schema if kg_schema is not None else []
        self.count = 0
        self.source = ""
        self.suggestion = ""
        self.info = {
            "add_entity": [],
            "add_relationship": [],
            "del_entity": [],
            "del_relationship": []
        }

    def llm_response(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = self.llm.generate(messages)

        return response

    def sum_suggestion(self, info: dict):
        for key, value in info.items():
            if key == "add_entity" and value:
                self.add_suggestion(f"Do not ignore entities belonging to the following categories:{','.join(value)}")
            if key == "del_entity" and value:
                self.add_suggestion(f"Do not extract entities belonging to the following categories:{','.join(value)}")
            if key == "add_relationship" and value:
                self.add_suggestion(
                    f"If the entity relationship is similar in meaning to the following vocabulary, the following vocabulary can be used as the entity relationship:{','.join(value)}")
            if key == "del_relationship" and value:
                triples = []
                relation_counter = {}
                for item in value:
                    triple = f"({item['DirectionalEntityType']},{item['DirectedEntityType']},{item['RelationType']})"
                    triples.append(triple)
                    relation = item["RelationType"]
                    if relation in relation_counter:
                        relation_counter[relation] += 1
                    else:
                        relation_counter[relation] = 1
                # 找出出现次数超过一次的RelationType
                frequent_relations = [relation for relation, count in relation_counter.items() if count > 3]
                if frequent_relations:
                    self.add_suggestion(
                        "Do not use the following vocabulary as entity relationship categories：" + "，".join(
                            frequent_relations))
                result_string = "Ensure that the extracted triplet does not conform to the following pattern:" + ",".join(
                    triples)
                self.add_suggestion(result_string)

    def add_suggestion(self, suggestion):
        if self.suggestion == "":
            self.suggestion = "@Rules {}".format(suggestion)
        else:
            self.suggestion = "{}\n@Rules {}".format(self.suggestion, suggestion)

    def construct(self, aim="extract knowledge", info=None) -> ConstructResult:
        if info is None:
            info = {}
        self.sum_suggestion(info)

        # 根据句子结构分割文本。

        for chunk in self.text_chunks:
            self.extract_kg_schema(chunk.text, aim)
        self.suggestion = ""

        return ConstructResult(self.kg_schema, self.definition)

    def extract_kg_schema(self, text, aim):

        # 以下是对已存在的知识架构进行操作：
        original_type_string = ""

        # 判断文本是什么语言
        def calculate_english_ratio(text):
            # 初始化英文字符计数器和总字符计数器
            english_count = 0
            total_count = 0

            # 遍历字符串中的每个字符
            for char in text:
                # 判断字符是否是英文字符
                if char.isalpha() and char.isascii():
                    english_count += 1
                total_count += 1

            # 计算英文字符占总字符的比例
            if total_count == 0:
                return 0  # 避免除以零的情况
            english_ratio = english_count / total_count
            if english_ratio >= 0.5:
                return True
            else:
                return False

        language = "English" if calculate_english_ratio(text=text) else "Chinese"
        # 读取已存在的知识架构，先给注释掉
        if self.kg_schema:
            # 提取实体类别和关系类别
            entity_categories = set()
            relation_categories = set()

            for item in self.kg_schema:
                try:
                    entity_categories.add(item['schema']['DirectionalEntityType']['Name'])
                    entity_categories.add(item['schema']['DirectedEntityType']['Name'])
                    relation_categories.add(item['schema']['RelationType'])
                except KeyError:
                    continue

            # 转换为字符串
            entity_categories_str = "，".join(entity_categories)
            relation_categories_str = "，".join(relation_categories)

            # 格式化为指定的字符串
            original_type_string = f'''
                    original entity categories:{entity_categories_str}
                    original entity relationship categories:{relation_categories_str}
                    '''

        prompt1 = Template(SCHEMA_CONSTRUCTOR)

        # 第一次带哦用大模型
        prompt1 = prompt1.render(text=text, aim=aim, language=language, suggestion=self.suggestion)
        print(prompt1)

        response1 = self.llm_response(prompt1)

        print(response1)
        # 从模型输出中得到实体类别和实体关系类别

        # 使用正则表达式提取定义部分
        pattern = re.compile(r'///(.*?)///', re.DOTALL)
        match = pattern.search(response1)
        definitions = match.group(1) if match else ''

        pattern1 = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
        match1 = pattern1.search(response1)
        definitions1 = match1.group(1) if match1 else ''

        for line in definitions.strip().split('#'):
            if ':' in line:
                key, value = line.split(':', 1)
                if key not in self.definition:
                    self.definition[key.strip()] = value.strip()

        for line in definitions1.strip().split('#'):
            if ':' in line:
                key, value = line.split(':', 1)
                if key not in self.definition:
                    self.definition[key.strip()] = value.strip()

        try:
            entity_categories = response1.split('%%')[1].split('%%')[0].strip()
            entity_relationships = response1.split('&&')[1].split('&&')[0].strip()
        except IndexError as e:
            print("IndexError: ", e)
            return self.extract_kg_schema(text, aim)

        # Create the final string
        type_string = f'''new entity categories：{entity_categories}\nnew entity relationship categories：{entity_relationships}'''

        # 从模型输出中提取三元组字符串
        try:
            # 使用正则表达式匹配所需的模式
            pattern = re.compile(r'\(\S+?, \S+?, \S+?\): [^(\n]+')

            # 找到所有匹配的字符串
            matches = pattern.findall(response1)

            # 将匹配的字符串转换为字典
            Triple_source_dict = {}
            Triple_string = ""
            for match in matches:
                match = match.replace('^', '')
                key, value = match.split(': ')
                Triple_source_dict[key] = value
                Triple_string += str(key)
                Triple_string += ','
        except IndexError as e:
            print("IndexError: ", e)
            return self.extract_kg_schema(text, aim)

        # 分割字符串，提取实体类别和关系类别
        entity_part, relationship_part = type_string.split('\n')

        # 提取实体类别
        entities = entity_part.split('：')[1].split(', ')

        # 提取关系类别
        relationships = relationship_part.split('：')[1].split(', ')

        # 合并实体类别和关系类别
        entities_and_relationships = entities + relationships

        # 构建结果字符串
        type_definition = ""
        for item in entities_and_relationships:
            if item in self.definition:
                type_definition += f"{item}:{self.definition[item]}\n"

        response2 = ""
        if self.kg_schema:
            # 第二次调用大模型
            prompt2 = Template(TYPE_DEFINITION)
            prompt2 = prompt2.render(oringinal_type_string=original_type_string, type_string=type_string,
                                     definition=type_definition)
            print(prompt2)
            response2 = self.llm_response(prompt2)
        print(response2)
        prompt3 = Template(ATTRIBUTES_INFER)
        if self.kg_schema:
            prompt3 = prompt3.render(type=response2, Triplet=Triple_string, language=language)
            print(prompt3)
        else:
            prompt3 = prompt3.render(type=type_string, Triplet=Triple_string, language=language)
            print(prompt3)
        response3 = self.llm_response(prompt3)
        print(response3)
        # 使用正则表达式找到有冒号的行，并提取冒号前后的部分
        pattern = re.compile(r'(\(\s*[^,]+,\s*[^,]+,\s*[^)]+\s*\))\s*[:：]\s*([^:\n]+)')
        matches = pattern.findall(response3)
        print(matches)
        # 构建字典
        instance_type_dict = {key.strip(): value.strip() for key, value in matches}

        relation_pattern = r'&\(([^#]+)\[([^\]]+)\] # ([^#]+)\[([^\]]+)\] # ([^\)]+)\)&'
        for Triple, string in instance_type_dict.items():
            cleaned_str = re.sub(r'\s*&\s*\(', '&(', string)
            cleaned_str = re.sub(r'\)\s*&', ')&', cleaned_str)
            str1 = re.findall(relation_pattern, cleaned_str)
            str1 = str1[0]
            directional_entity = {'Name': str1[0].strip(),
                                  'Attributes': [attr.strip() for attr in str1[1].split(',')]}
            directed_entity = {'Name': str1[2].strip(),
                               'Attributes': [attr.strip() for attr in str1[3].split(',')]}
            relation_type = str1[4].strip()
            instance_type_dict[Triple] = {
                'DirectionalEntityType': directional_entity,
                'RelationType': relation_type,
                'DirectedEntityType': directed_entity
            }

        # 初始化字典以收集每个模式的源代码
        schema_sources = {}

        # 根据类型三元组来收集source
        for key, value in Triple_source_dict.items():
            if key in instance_type_dict:
                schema = instance_type_dict[key]
                schema_key = str(schema)
                if schema_key not in schema_sources:
                    schema_sources[schema_key] = {'schema': schema, 'source': {}}
                schema_sources[schema_key]['source'][key] = value

        # 将字典转换成一个列表
        schema_list = list(schema_sources.values())

        # 调整三元组的顺序以保证关系词在中间
        def reorder_triples(schema_list):
            adjusted_schema_list = []
            for item in schema_list:
                schema = item["schema"]
                source = item["source"]
                new_source = {}
                for key, value in source.items():
                    elements = key.strip("()").split(", ")
                    new_key = f"({elements[0]}, {elements[2]}, {elements[1]})"
                    new_source[new_key] = value
                adjusted_schema_list.append({
                    "schema": schema,
                    "source": new_source
                })
            return adjusted_schema_list

        schema_list = reorder_triples(schema_list)

        # 将本次得到的schema和之前得到的schema按照特定模式合并，把相同模式的source进行合并
        merged_dict = defaultdict(lambda: {"schema": None, "source": {}})

        def add_to_merged_dict(item):
            schema = item["schema"]
            schema_key = (schema["DirectionalEntityType"]["Name"],
                          tuple(schema["DirectionalEntityType"]["Attributes"]),
                          schema["RelationType"],
                          schema["DirectedEntityType"]["Name"],
                          tuple(schema["DirectedEntityType"]["Attributes"]))

            if merged_dict[schema_key]["schema"] is None:
                merged_dict[schema_key]["schema"] = schema

            merged_dict[schema_key]["source"].update(item["source"])

        for item in self.kg_schema + schema_list:
            add_to_merged_dict(item)

        # 构建输出列表
        # output_list = [{"schema": value["schema"], "source": value["source"]} for value in merged_dict.values()]
        output_list = []
        for value in merged_dict.values():
            value["schema"]["source"] = value["source"]
            output_list.append(value["schema"])

        self.kg_schema = output_list

    async def aconstruct(self, aim="extract knowledge", info=None) -> ConstructResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.construct, aim, info)

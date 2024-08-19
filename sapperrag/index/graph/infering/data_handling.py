from collections import defaultdict
from typing import List, Dict, Tuple
import os


class DataProcessor:
    """
    本类用于对初提取的三元组以及KG推理得到的新三元组进行去重操作。重点在于每个实体的属性不应该丢弃。
    """
    @staticmethod
    def merge_attributes(attr1, attr2):
        """
        合并两个属性字典，保留一个source和source_id，其他属性去重
        :param attr1: 属性字典
        :param attr2: 属性字典
        :return: 合并后的属性字典
        """
        # 初始化两个三元组去重后的三元组字典。
        merged = {}
        # 对特殊属性进行特殊保留处理：保留第一个字典的source和source_id
        if "source" in attr1:
            merged["source"] = attr1["source"]
        elif "source" in attr2:
            merged["source"] = attr2["source"]

        if "source_id" in attr1:
            merged["source_id"] = attr1["source_id"]
        elif "source_id" in attr2:
            merged["source_id"] = attr2["source_id"]

        # 合并其他属性 -> 两个集合的并集
        all_keys = set(attr1.keys()).union(set(attr2.keys()))
        for key in all_keys:
            # 特殊属性不参与合并
            if key not in ["source", "source_id"]:
                value1 = attr1.get(key, "")
                value2 = attr2.get(key, "")
                if value1 and value2:
                    # 如果两个属性都有值且不同，合并为列表
                    if value1 != value2:
                        merged[key] = [value1, value2]
                    else:
                        merged[key] = value1
                else:
                    merged[key] = value1 if value1 else value2

        return merged

    def deduplicate_triples(self, triples) -> List:
        """
        对原始三元组列表进行去重操作，保留属性字典。
        :param triples: 原始三元组列表
        :return: 去重后的三元组列表
        """
        # 设定抽象字典模板。
        triple_dict = defaultdict(list)

        for triple in triples:
            try:
                # 元组不可变，因此可以作为key
                key = (
                    triple["DirectionalEntity"]["Type"],
                    triple["DirectionalEntity"]["Attributes"]["name"],
                    triple["Relation"]["Type"],
                    triple["Relation"]["Attributes"]["name"],
                    triple["DirectedEntity"]["Type"],
                    triple["DirectedEntity"]["Attributes"]["name"]
                )
                triple_dict[key].append(triple)
            except KeyError:
                pass
            except TypeError:
                pass
            except Exception:
                pass

        # 三元组去重列表容器
        deduplicated_triples = []

        for key, grouped_triples in triple_dict.items():
            try:
                # 如果相同元组key只有一个，则直接加入去重列表
                if len(grouped_triples) == 1:
                    deduplicated_triples.append(grouped_triples[0])
                else:
                    # 合并多个三元组
                    merged_triple = grouped_triples[0]
                    for i in range(1, len(grouped_triples)):
                        merged_triple["DirectionalEntity"]["Attributes"] = self.merge_attributes(
                            merged_triple["DirectionalEntity"]["Attributes"],
                            grouped_triples[i]["DirectionalEntity"]["Attributes"]
                        )
                        merged_triple["DirectedEntity"]["Attributes"] = self.merge_attributes(
                            merged_triple["DirectedEntity"]["Attributes"],
                            grouped_triples[i]["DirectedEntity"]["Attributes"]
                        )
                    deduplicated_triples.append(merged_triple)
            except KeyError:
                pass
            except TypeError:
                pass
            except Exception:
                pass

        return deduplicated_triples

    @staticmethod
    def transform_to_cytoscape_elements(triples) -> List[Dict]:
        """
        将三元组列表转换为Cytoscape.js所需的元素列表
        """
        elements = []
        id_counter = 1  # 用于生成唯一的节点和边ID
        node_id_map = {}  # 用于映射实体名称到节点ID

        for triple in triples:
            # 处理DirectionalEntity
            dir_entity = triple['DirectionalEntity']
            dir_name = dir_entity['Attributes']['name']
            if dir_name not in node_id_map:
                node_id = f'n{id_counter}'
                id_counter += 1
                node_id_map[dir_name] = node_id
                elements.append({
                    'data': {
                        'id': node_id,
                        'label': dir_name,
                        'type': dir_entity['Type']
                    }
                })
            else:
                node_id = node_id_map[dir_name]

            # 处理DirectedEntity
            directed_entity = triple['DirectedEntity']
            directed_name = directed_entity['Attributes']['name']
            if directed_name not in node_id_map:
                target_id = f'n{id_counter}'
                id_counter += 1
                node_id_map[directed_name] = target_id
                elements.append({
                    'data': {
                        'id': target_id,
                        'label': directed_name,
                        'type': directed_entity['Type']
                    }
                })
            else:
                target_id = node_id_map[directed_name]

            # 处理Relation
            relation = triple['Relation']
            rel_name = relation['Attributes']['name']
            edge_id = f'e{id_counter}'
            id_counter += 1
            elements.append({
                'data': {
                    'id': edge_id,
                    'source': node_id,
                    'target': target_id,
                    'name': rel_name
                }
            })
        return elements

    @staticmethod
    def entities_combine_type_and_definition(schema_definition: Dict, kg_schema: List) -> str:
        """
        将知识图谱的类型和定义合并到一起
        :param schema_definition: 知识架构的定义
        :param kg_schema: 知识图谱的类型架构
        :return: 合并后的知识图谱
        """
        # 读取知识图谱的定义文件
        relation_type_set = set()
        for schema in kg_schema:
            try:
                relation_type = schema["RelationType"]
                relation_type_set.add(relation_type)
            except KeyError:
                continue
        # 删去对关系类型的定义：
        for relation_type in relation_type_set:
            schema_definition.pop(relation_type, None)
        # 为每个实体类型添加定义，构建列表再拼接：
        entities_types_whit_definition = [f"{key}({value})" for key, value in schema_definition.items()]
        return "; ".join(entities_types_whit_definition)

    @staticmethod
    def relations_combine_type_and_definition(schema_definition: Dict, kg_schema: List):
        """
        将知识图谱的类型和定义合并到一起
        """
        entity_type_set = set()
        for schema in kg_schema:
            try:
                directional_entity_type = schema["DirectionalEntityType"]["Name"]
                directed_entity_type = schema["DirectedEntityType"]["Name"]
                entity_type_set.add(directed_entity_type)
                entity_type_set.add(directional_entity_type)
            except KeyError:
                continue
        # 删去对实体类型的定义：
        for entity_type in entity_type_set:
            schema_definition.pop(entity_type, None)
        # 为每个关系类型添加定义，构建列表再拼接：
        relations_types_whit_definition = [f"{key}({value})" for key, value in schema_definition.items()]
        return "; ".join(relations_types_whit_definition)

    @staticmethod
    def combine_entity_type(entity_type_dic: Dict):
        """
        将实体类型字典转换为字符串
        :param entity_type_dic: 实体类型字典
        :return: 实体类型字符串
        """
        # 为每个实体类型添加定义，构建列表再拼接：key是实体，value是类型
        entities_types_whit_definition = [f"{key}({value})" for key, value in entity_type_dic.items()]
        return "; ".join(entities_types_whit_definition)

    @staticmethod
    def combine_entities_and_type(entity_type_dic: Dict):
        """
        收集实体类型字典中的实体
        :param entity_type_dic: 实体类型字典
        :return: 实体列表
        """
        return ";".join([f"{key}({value})" for key, value in entity_type_dic.items()])

    @staticmethod
    def combine_extracted_entities_with_types(entity_type_dic: Dict):
        """
        将实体类型字典转换为字符串
        :param entity_type_dic: 实体类型字典
        :return: 实体类型字符串
        """
        # 为每个实体类型添加定义，构建列表再拼接：key是实体，value是类型
        entities_with_types = [f"{key}:{value}" for key, value in entity_type_dic.items()]
        return "; ".join(entities_with_types)

    @staticmethod
    def combine_types_and_attributes(kg_schema: List) -> Tuple[str, Dict]:
        """
        将知识图谱的类型和属性合并到一起
        """
        # 为每个实体类型添加定义，构建列表再拼接：
        entities_types_with_attributes = [f"{schema['DirectionalEntityType']['Name']}:({', '.join(schema['DirectionalEntityType']['Attributes'])})" for schema in kg_schema]
        entities_types_with_attributes.extend([f"{schema['DirectedEntityType']['Name']}:({', '.join(schema['DirectedEntityType']['Attributes'])})" for schema in kg_schema])

        type_attributes_dic = {}
        for schema in kg_schema:
            try:
                directional_entity_type = schema["DirectionalEntityType"]["Name"]
                directed_entity_type = schema["DirectedEntityType"]["Name"]
                directional_entity_attributes = schema["DirectionalEntityType"]["Attributes"]
                directed_entity_attributes = schema["DirectedEntityType"]["Attributes"]
                directional_entity_attributes_dic = {attr: "Unknown" for attr in directional_entity_attributes}
                directed_entity_attributes_dic = {attr: "Unknown" for attr in directed_entity_attributes}
                type_attributes_dic[directional_entity_type] = directional_entity_attributes_dic
                type_attributes_dic[directed_entity_type] = directed_entity_attributes_dic
            except KeyError:
                continue
            except Exception:
                continue
        # 对相同元素去重：
        entities_types_with_attributes = list(set(entities_types_with_attributes))
        return "; ".join(entities_types_with_attributes), type_attributes_dic

    @staticmethod
    def convert_to_kg_json_format(triples_and_type_dic: Dict[Tuple, Tuple], entity_attributes_dic: Dict[str, Dict], type_attributes_dic: Dict[str, Dict] = None):
        """
        将 三元组 -> 类型三元组 和 实体属性字典 合并转换为标准KG JSON格式
        :param triples_and_type_dic: 三元组 -> 类型三元组 字典
        :param entity_attributes_dic: 实体属性字典
        """
        # 生成指定的知识图谱JSON格式
        kg_json_format = []

        # 分离三元组和类型三元组 -> 一对一的形式：
        for triples, type_triples in triples_and_type_dic.items():
            try:
                directional_entity, relation, directed_entity = triples
                directional_entity_type, relation_type, directed_entity_type = type_triples
                # 从实体属性字典中获取实体属性，如果没有则从类型属性字典中获取，并将属性值置为Unknown
                directional_entity_attributes = entity_attributes_dic.get(directional_entity, {})
                # 注意原地操作的特性
                directional_entity_attributes.update({"name": directional_entity})
                directed_entity_attributes = entity_attributes_dic.get(directed_entity, {})
                directed_entity_attributes.update({"name": directed_entity})
                kg_json_format.append({
                    "DirectionalEntity": {
                        "Type": directional_entity_type,
                        "Attributes": directional_entity_attributes
                    },
                    "Relation": {
                        "Type": relation_type,
                        "Attributes": {
                            "name": relation
                        }
                    },
                    "DirectedEntity": {
                        "Type": directed_entity_type,
                        "Attributes": directed_entity_attributes
                    }
                })
            except Exception:
                pass

        return kg_json_format

    @staticmethod
    def add_key_attribute(triples: List, key_word: str, value: str):
        """
        添加指定名称的属性键值对
        """
        for triple in triples:
            for entity in ["DirectionalEntity", "Relation", "DirectedEntity"]:
                if entity in triple:
                    if "Attributes" in triple[entity]:
                        triple[entity]["Attributes"][key_word] = value
                    else:
                        triple[entity]["Attributes"] = {key_word: value}
        return triples

    @staticmethod
    def add_source_id_to_entities(triples, source_id=0):
        """
        为列表中所有的实体添加source_id为0的属性键值对
        :param triples: 包含三元组的列表
        :param source_id: 要添加的source_id值，默认为0
        :return: 添加了source_id后的三元组列表
        """
        for triple in triples:
            for entity in ["DirectionalEntity", "Relation", "DirectedEntity"]:
                if entity in triple:
                    if "Attributes" in triple[entity]:
                        triple[entity]["Attributes"]["source_id"] = source_id
                    else:
                        triple[entity]["Attributes"] = {"source_id": source_id}
        return triples

    @staticmethod
    def add_source_for_entity(triples_list: List[dict] = None, source: str = "PATH_TO_YOUR_FILE") -> List[dict]:
        """
        本方法旨在为三元组中的实体添加文件来源
        :param triples_list: 不带有来源的三元组列表
        :param source: 该提取的三元组的文件来源
        :return: triples_list_with_source: 带有来源的三元组列表
        """
        # 如果没有传入三元组列表，那么返回空列表
        if not triples_list:
            return []

        # 为每个三元组添加来源信息，以及对应的文件名
        triples_list_with_source = []
        for triple in triples_list:
            # 分割文件路径，获取文件名
            file_name = os.path.basename(source)
            # 为每个实体添加来源信息，以及对应的文件名
            triple["DirectionalEntity"]["Attributes"].update({"source": file_name})
            triple["DirectedEntity"]["Attributes"].update({"source": file_name})
            triples_list_with_source.append(triple)

        # 返回带有来源的三元组列表
        return triples_list_with_source

    @staticmethod
    def kg_infer_convert2attributes_dic(kg_schema: List[Dict]) -> Dict:
        """
        将知识架构转换为类型属性字典
        """
        type_attributes_dic = {}
        for type_triple in kg_schema:
            try:
                type1 = type_triple["DirectionalEntityType"]["Name"]
                type2 = type_triple["DirectedEntityType"]["Name"]
                type_attributes_dic[type1] = type_triple["DirectionalEntityType"]["Attributes"]
                type_attributes_dic[type2] = type_triple["DirectedEntityType"]["Attributes"]
            except KeyError:
                continue

        return type_attributes_dic


class KGFilter:

    def __init__(self, kg, kg_schema):
        self.kg = kg
        self.kg_schema = kg_schema

    def is_valid_triplet(self, triplet):
        for schema in self.kg_schema:
            if (triplet["DirectionalEntity"]["Type"] == schema["DirectionalEntityType"]["Name"] and
                    triplet["Relation"]["Type"] == schema["RelationType"] and
                    triplet["DirectedEntity"]["Type"] == schema["DirectedEntityType"]["Name"]):
                return True
        return False

    def strict_filter(self):
        filtered_kg = [triplet for triplet in self.kg if self.is_valid_triplet(triplet)]
        return filtered_kg, self.kg_schema

    def non_strict_filter(self, repeat_count):
        type_triplet_count = defaultdict(int)
        type_triplet_to_triplets = defaultdict(list)

        for triplet in self.kg:
            type_triplet = (triplet["DirectionalEntity"]["Type"], triplet["Relation"]["Type"], triplet["DirectedEntity"]["Type"])
            type_triplet_count[type_triplet] += 1
            type_triplet_to_triplets[type_triplet].append(triplet)

        filtered_kg = []

        for type_triplet, count in type_triplet_count.items():
            if self.is_valid_type_triplet(type_triplet):
                filtered_kg.extend(type_triplet_to_triplets[type_triplet])
            elif count > repeat_count:
                self.add_to_schema(type_triplet)
                filtered_kg.extend(type_triplet_to_triplets[type_triplet])

        return filtered_kg, self.kg_schema

    def is_valid_type_triplet(self, type_triplet):
        for schema in self.kg_schema:
            if (type_triplet[0] == schema["DirectionalEntityType"]["Name"] and
                    type_triplet[1] == schema["RelationType"] and
                    type_triplet[2] == schema["DirectedEntityType"]["Name"]):
                return True
        return False

    def add_to_schema(self, type_triplet):
        new_schema_entry = {
            "DirectionalEntityType": {
                "Name": type_triplet[0],
                "Attributes": []
            },
            "RelationType": type_triplet[1],
            "DirectedEntityType": {
                "Name": type_triplet[2],
                "Attributes": []
            }
        }
        self.kg_schema.append(new_schema_entry)

    def filter_kg(self, strict=True, repeat_count=None):
        """
        过滤KG并更新schema,如果选择非严格模式，需要传入重复次数参数，如果是严格模式，则默认传入的schema完全正确且全面
        :param strict: 是否严格模式
        :param repeat_count: 重复次数
        :return: 过滤后的KG和更新后的schema
        """
        if strict:
            return self.strict_filter()
        else:
            if repeat_count is None:
                raise ValueError("Non-strict filter mode requires a repeat_count parameter")
            return self.non_strict_filter(repeat_count)

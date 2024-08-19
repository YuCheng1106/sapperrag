from ....index.graph.infering.LLM_API import OpenAIResponseGetter
from ....index.graph.infering.LLM_API_Parameter import OPENAI_API_PARAMETER
from typing import Tuple, Dict, List


class AIResponseGetter:
    """
    提供三种调用方法，分别是SapperChainAPI, SapperAgentPost, OpenAIAPI
    调用SapperChainAPI时，需要提供sapper_agent_param_json_path参数，用于指定SapperChain的参数文件路径
    调用SapperAgentPost时，需要提供sapper_agent_url参数，用于指定SapperAgent的URL
    调用OpenAIAPI时，需要提供openai_api_key参数，用于指定OpenAI的API key
    以及其他参数：base_url, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop
    """
    def __init__(self, llm_api_parameter: OPENAI_API_PARAMETER = None):
        """
        初始化AIResponseGetter
        :param llm_api_parameter: llm API的参数，包括openai_api_key, base_url, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop
        """
        self.llm_api_parameter = llm_api_parameter

    def get_response(self, request, step) -> str:
        """
        获取AI的响应
        :param request: 完整请求
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :return: 返回AI的响应，是一个字符串
        """
        llm_api_parameter = self.llm_api_parameter
        # 如果调用方法是OpenAIAPI，那么调用OpenAIResponseGetter
        if type(llm_api_parameter) is OPENAI_API_PARAMETER:
            # 调用OpenAI，注意api_key的依赖
            response = OpenAIResponseGetter(openai_api_parameter=llm_api_parameter).get_response(request, step=step)
            return response
        else:
            # 如果调用方法不在上述三种方法中，那么抛出异常,终止程序
            raise ValueError(f"Unsupported llm API Call")


class FormatConvertTool:
    """
    用于格式转换的工具类，提供静态方法string_to_list()，将字符串转换为列表
    """
    def __init__(self):
        pass

    @staticmethod
    def parse_entities_string(entity_string) -> Dict:
        """
        解析实体属性提取的字符串
        :param entity_string: 实体属性提取的字符串 -> e1(attr1: value1 && attr2:value2); e2(attr1: value1 && attr2:value2); ...
        :return: 解析后的实体字典 -> {e1: {attr1: value1, attr2: value2}, e2: {attr1: value1, attr2: value2}, ...}
        """
        # 去除不规则的空白字符和换行符
        cleaned_string = " ".join(entity_string.split())
        # 拆分整个字符串为以";"分隔的条目
        entries = cleaned_string.split(";")
        # 创建一个空字典来存储解析结果
        entity_dict = {}
        # 迭代每一个条目并拆分为实体及其属性
        for entry in entries:
            try:
                entry = entry.strip()  # 去除前后空白字符
                if "(" in entry and ")" in entry:
                    entity_name, attributes = entry.split("(", 1)
                    entity_name = entity_name.strip()
                    attributes = attributes.strip(")").strip()
                    # 拆分属性对
                    attr_dict = {}
                    for attr in attributes.split("&&"):
                        if ":" in attr:
                            key, value = attr.split(":", 1)
                            attr_dict[key.strip()] = value.strip()
                        else:
                            pass
                    entity_dict[entity_name] = attr_dict
                else:
                    pass
            except ValueError:
                pass
            except Exception:
                pass
        return entity_dict

    @staticmethod
    def parse_triples_string(triples_string) -> Tuple[Dict[Tuple, Tuple], List]:
        """
        解析关系三元组提取的字符串
        :param triples_string: 关系三元组提取的字符串 -> (e1, r1, e2)-(t1, t2, t3); (e3, r2, e4)-(t4, t5, t6); ...
        :return: 解析后的三元组字典 -> {(e1, r1, e2): (t1, t2, t3), (e3, r2, e4): (t4, t5, t6), ...}
        """
        # 去除不规则的空白字符和换行符
        cleaned_string = " ".join(triples_string.split())
        # 拆分整个字符串为以 "; " 分隔的条目
        entries = cleaned_string.split(";")
        # 创建一个空字典来存储解析结果
        triples_dict = {}
        extracted_entities = []
        # 迭代每一个条目并拆分为键值对
        for entry in entries:
            try:
                entry = entry.replace(" ", "")  # 去除所有空白字符
                if ")-(" in entry:
                    entity_part, type_part = entry.split(")-(")
                    entity_part = entity_part.strip("()")
                    type_part = type_part.strip(")")
                    entities = entity_part.split(",")
                    types = type_part.split(",")
                    if len(entities) == 3 and len(types) == 3:
                        relation_key = (entities[0], entities[1], entities[2])
                        type_value = (types[0], types[1], types[2])
                        triples_dict[relation_key] = type_value
                        # 将提取得实体添加进列表
                        extracted_entities.append(entities[0])
                        extracted_entities.append(entities[2])
                    else:
                        pass
            except Exception:
                pass
        return triples_dict, list(set(extracted_entities))

    @staticmethod
    def parse_entity_types(entity_type_string) -> Dict:
        """
        解析实体及其类型提取的字符串
        :param entity_type_string: 实体及其类型提取的字符串 -> e1: t1; e2: t2; e3: t3; ...
        :return: 解析后的实体类型字典 -> {e1: t1, e2: t2, e3: t3, ...}
        """
        # 去除转义字符和多余的空白字符，并拆分整个字符串为以 ";" 分隔的条目
        entries = [" ".join(entry.split()).strip() for entry in entity_type_string.split(";") if entry.strip()]
        # 创建一个空字典来存储解析结果
        entity_type_dict = {}
        # 迭代每一个条目并拆分为键值对
        for entry in entries:
            try:
                if ":" in entry:
                    entity, entity_type = entry.split(":", 1)
                    entity = entity.strip()
                    entity_type = entity_type.strip()
                    entity_type_dict[entity] = entity_type
                else:
                    pass
            except ValueError:
                pass
            except Exception:
                pass
        return entity_type_dict


class PreAIResponseGetter:
    def __init__(self, template_choice: str = None):
        """
        :param template_choice: 模板选择： "INSTRUCTION1" OR "INSTRUCTION2" OR "INSTRUCTION3"
        AI-Chain -> "INSTRUCTION1" -> 提取实体及其对应的类型 -> "INSTRUCTION2" -> 提取三元组及其对应的类型三元组 -> "INSTRUCTION3" -> 提取实体属性
        """
        self.template_choice = template_choice

    def insert_query_into_template(self, **kwargs) -> str:
        """
        将query插入到SPL模板中
        :param kwargs: 请求的内容 -> 可以是多个
        :return: 插入query后的SPL prompt
        """
        # 依赖于jinja2模板引擎：
        from jinja2 import Template
        # 根据传入的模板选择，选择不同的模板
        if self.template_choice == "INSTRUCTION1":
            template = Template(self.get_entities_extracting_spl_prompt())
            # 返回渲染后的结果
            return template.render(**kwargs)
        elif self.template_choice == "INSTRUCTION2":
            template = Template(self.get_relations_identifying_spl_prompt())
            # 返回渲染后的结果
            return template.render(**kwargs)
        elif self.template_choice == "INSTRUCTION3":
            template = Template(self.get_entities_attributes_identifying_spl_prompt())
            # 返回渲染后的结果
            return template.render(**kwargs)
        else:
            # 如果后续还需要再添加新的prompt，在这里设置逻辑选择即可。
            pass

    @staticmethod
    def get_entities_extracting_spl_prompt():
        """
        获取简单的三元组提取SPL模板
        :return: 三元组提取SPL模板，提取结果是简单格式的，同时带有属性标签的三元组
        """
        entities_extracting_prompt = """
@Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should executing all instructions as needed"
三元组提取器{
    @Persona {
        @Description{
            You are an expert Triples extractor.
        }
    }
    @Audience {
        @Description{
            Data scientists and knowledge engineers.
        }
    }
    @ContextControl {
        @Rules Ensure that the extracted entities accurately correspond to the content in the original text.
        @Rules Ensure consistency between the extracted entities and the original text.
    }
    
    @Instruction Extract entity{
        @InputVariable{
            documentation: ${ {{text_chunk}} }$
            entity types definitions: ${ {{entity_types_definitions}} }$
        }
        @Commands Extracting entities from the documentation based on the given entity types and definitions.
        @Commands Do not output any additional text instructions other than those specified in the format.
        @OutputVariable{
            ${Entities}$
        }
        @Rules You need to analyze each token in the documentation and determine if it is an entity.
        @Rules Ensure that the extracted entities match the entity types and definitions provided.
        @Rules Strictly ensure that the output entity can be found in the original text and don`t make any change.
        @Rules The format of output (Entities) is "entity: entity type".
        @Format{ 
            entity1: type1; entity2: type2; entity3: type3; ...
        }   @Example{
                fox: animal; dog: animal; 小李: 程序员
            }

    }
}
You are now the 三元组提取器 defined above, please complete the user interaction as required.
    """

        return entities_extracting_prompt

    @staticmethod
    def get_relations_identifying_spl_prompt():
        """
        获取简单的关系识别SPL模板
        :return: 关系识别SPL模板，提取结果是简单格式的，同时带有属性标签的三元组
        """
        relations_identifying_prompt = """
@Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should executing all instructions as needed"
三元组提取器{
    @Persona {
        @Description{
            You are an expert Triples extractor.
        }
    }
    @Audience {
        @Description{
            Data scientists and knowledge engineers.
        }
    }
    @ContextControl {
        @Rules Ensure that the determined relation accurately correspond to the content in the original text.
        @Rules Ensure consistency between the entity of the output triples and the provided entities.
        @Rules Ensure that the components of building instance triples and type triples strictly come from input variable.
    }
    @Instruction Identify relation{
        @InputVariable{
            entities: ${ {{entities_set}} }$
            documentation: ${ {{text_chunk}} }$
            relation type definitions: ${ {{relation_types_definitions}} }$
        }
        @Commands Based on the documentation and the given relation type definitions, determine whether there is a relation between provided entities.
        @Commands Identify and analyze the entity type in parentheses attached to each entity in entities.
        @Commands Attach the corresponding entity type and relationship type to each triples to form a type triples.
        @Commands Do not output any additional text instructions other than those specified in the @Format.
        @OutputVariable{
            ${Triples}$
        }
        @Rules Carefully determine whether an existing relation type is satisfied between any two entities.
        @Rules Ensure all output entities and types must be strictly selected from the provided input variable and are not allowed to exceed this range.
        @Rules Ensure that each entity corresponds strictly to the type indicated in parentheses.
        @Rules The format of output (Triples) is "(entity1 name, relation, entity2 name)-(type of entity1, type of relation, type of entity2)"
        @Format{
            (entity1, relation1, entity2)-(type of entity1, type of relation1, type of entity2); (entity3, relation2, entity4)-(type of entity3, type of relation2, type of entity4); ...
        }   @Example{
                (fox, jumps over, dog)-(animal, activity, animal); (小李, 跳槽, 字节跳动)-(人, 工作变迁, 公司); (fox, bigger than, dog)-(animal, compare, animal)
            }
    }	
}
You are now the 三元组提取器 defined above, please complete the user interaction as required.
        """
        return relations_identifying_prompt

    @staticmethod
    def get_entities_attributes_identifying_spl_prompt():
        """
        获取简单的实体属性识别SPL模板
        :return: 实体属性识别SPL模板，提取结果是简单格式的，同时带有属性标签的三元组
        """
        entities_attributes_identifying_prompt = """
@Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should executing all instructions as needed"
三元组提取器{
    @Persona {
        @Description{
            You are an expert Triples extractor.
        }
    }
    @Audience {
        @Description{
            Data scientists and knowledge engineers.
        }
    }
    @ContextControl {
        @Rules Ensure that the extracted value of attribute accurately correspond to the content in the original text.
        @Rules Ensure that the attributes corresponding to entities of the same type are fully extracted.
    }
    @Instruction Indentify attribute{
        @InputVariable{
            documentation: ${ {{text_chunk}} }$
            type attributes: ${ {{types_attributes}} }$
            entities: ${ {{extracted_entities_with_types_str}} }$
        }
        @Commands Based on the documentation and the given type attributes, extract attribute values of entities of the same type.
        @Commands Extract all attributes of entity type declarations, and set them to Unknown if attribute values cannot be found.
        @Commands Do not output any additional text instructions other than those specified in the format.
        @OutputVariable{
            ${Entities_with_attributes}$
        } 
        @Rules Ensure that the attributes corresponding to entities of the same type are accurately extracted.
        @Rules Strictly ensure that the output entity can be found in the original text and don`t make any change.
        @Rules The format of output (Entity_with_attributes) is "entity(attribute1: value1 && attribute2: value2, ...)".
        @Format{
            entity1(attribute1: value1 && attribute2: value2); entity2(attribute3: value3 && attribute4: value4); ...
        }   @Example{
                fox(color: brown && size: small); dog(color: brown && size: Unknown); 小李(工作: 编程 && 年龄: 30 && 邮箱: Unknown); 小王(工作: Unknown && 年龄: Unknown && 邮箱: Unknown)
            }
    }
}
You are now the 三元组提取器 defined above, please complete the user interaction as required.
        """
        return entities_attributes_identifying_prompt

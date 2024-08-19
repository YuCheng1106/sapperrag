from ....index.graph.infering.AIExecutorTool import AIResponseGetter
from ....index.graph.infering.AIExecutorTool import FormatConvertTool
from ....index.graph.infering.AIExecutorTool import PreAIResponseGetter
from ....index.graph.infering.LLM_API_Parameter import OPENAI_API_PARAMETER
from typing import List, Dict
from ....index.graph.infering.data_handling import DataProcessor
data_processor = DataProcessor()


class AIExecutor:
    """
    AI执行器，用于执行AI请求
    方法：
    execute：执行AI请求：
    提供两个Instruction的模板，用于请求预处理AI，应对OpenAIAPI的情况
    如果不是OpenAIAPI，则无需请求预处理AI
    """
    def __init__(self, ai_response_getter: AIResponseGetter = None):
        """
        :param ai_response_getter: 用于获取AI回复的对象
        """
        self.ai_response_getter = ai_response_getter
        self.format_convert_tool = FormatConvertTool()

    def execute(self, step: str, text_chunk: str = "", kg_schema: List = None, schema_definition: Dict = None):
        """
        执行AI请求
        :param text_chunk: 用户请求的文本块
        :param kg_schema: 知识架构
        :param schema_definition: 知识架构定义的路径
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :return: AI的回复
        """

        if type(self.ai_response_getter.llm_api_parameter) is OPENAI_API_PARAMETER:
            # 如果是OpenAIAPI，则需要请求预处理模板，获取第一个instruction的回复
            try:
                final_response = self.execute_openai_api(step, text_chunk, kg_schema, schema_definition)
                return final_response
            except Exception as e:
                # 如果出现异常，打印异常信息，并返回空列表
                print(f"Error processing the response: {str(e)}")
                return []
        else:
            # 不支持的调用方法，手动抛出异常
            raise ValueError("Unsupported llm API Call")

    def execute_instruction1(self, step: str, text_chunk: str = "", kg_schema: List = None, schema_definition: Dict = None):
        """
        执行第一个instruction，提取实体及其对应的类型。
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :param text_chunk: 用户请求的文本块
        :param kg_schema: 知识架构
        :param schema_definition: 知识架构定义的路径
        """
        entity_types_definitions = data_processor.entities_combine_type_and_definition(schema_definition, kg_schema)
        pre_ai_response_getter_instruction1 = PreAIResponseGetter(template_choice="INSTRUCTION1")
        # 将用户请求插入到第一个instruction的模板中，构建请求获取第一个instruction的回复
        instruction1_request_prompt = pre_ai_response_getter_instruction1.insert_query_into_template(
            text_chunk=text_chunk,
            entity_types_definitions=entity_types_definitions)
        # 获取第一个instruction的回复，作为第二个instruction的输入
        instruction1_response = self.ai_response_getter.get_response(instruction1_request_prompt, step)

        return self.format_convert_tool.parse_entity_types(instruction1_response)

    def execute_instruction2(self, step: str, text_chunk: str = "", kg_schema: List = None, schema_definition: Dict = None, instruction1_response: Dict = None):
        """
        执行第二个instruction，提取三元组及其对应的类型三元组。
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :param text_chunk: 用户请求的文本块
        :param kg_schema: 知识架构
        :param schema_definition: 知识架构定义的路径
        :param instruction1_response: 第一个instruction的回复
        """
        # 实体为键，类型为值的字典
        entity_type_dic = instruction1_response
        entities = data_processor.combine_entities_and_type(entity_type_dic)
        relation_types_definitions = data_processor.relations_combine_type_and_definition(schema_definition, kg_schema)
        pre_ai_response_getter_instruction2 = PreAIResponseGetter(template_choice="INSTRUCTION2")
        # 将用户请求插入到第二个instruction的模板中，构建请求获取第二个instruction的回复
        instruction2_request_prompt = pre_ai_response_getter_instruction2.insert_query_into_template(
            text_chunk=text_chunk,
            entities_set=entities,
            relation_types_definitions=relation_types_definitions)
        # 获取第二个instruction的回复，作为最终回复
        instruction2_response = self.ai_response_getter.get_response(instruction2_request_prompt, step)

        return instruction2_response, entity_type_dic

    def execute_instruction3(self, step: str, text_chunk: str = "", kg_schema: List = None, instruction2_response: str = "", entity_type_dic: Dict = None):
        """
        执行第三个instruction，提取实体属性。
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :param text_chunk: 用户请求的文本块
        :param kg_schema: 知识架构
        :param instruction2_response: 第二个instruction的回复
        :param entity_type_dic: 实体为键，类型为值的字典
        """
        # 这样更改的话这里的triples_and_type_dic携带的就不是单个的关系类型了，而是整个类型三元组。也省去了换原实体类型这种容易出错的步骤。
        triples_and_type_dic, extracted_entities = self.format_convert_tool.parse_triples_string(instruction2_response)  # 这里是三元组元组以及对应的关系类型组成的三元组
        # 这是提取的实体
        extracted_entities_with_types_str = data_processor.combine_extracted_entities_with_types(entity_type_dic)  # 这里是提取到的实体和类型的字典，实体是键，类型是值
        # 组成的带类型标签的字符串，用于构建提取属性的请求 -> 返回用于构建的带有属性的实体类型声明 + 类型属性字典
        types_with_attributes_str, type_attributes_dic = data_processor.combine_types_and_attributes(kg_schema)

        # 构建第三个instruction的请求
        pre_ai_response_getter_instruction3 = PreAIResponseGetter(template_choice="INSTRUCTION3")
        instruction3_request_prompt = pre_ai_response_getter_instruction3.insert_query_into_template(
            text_chunk=text_chunk,
            extracted_entities_with_types_str=extracted_entities_with_types_str,
            types_attributes=types_with_attributes_str
        )
        # 获取第三个instruction的回复
        instruction3_response = self.ai_response_getter.get_response(instruction3_request_prompt, step)
        # 解析第三个instruction的回复
        entity_attributes_dic = self.format_convert_tool.parse_entities_string(instruction3_response)  # 这里是实体的属性字典，实体是键，属性字典是值

        # 三元组:
        return entity_attributes_dic, triples_and_type_dic, type_attributes_dic

    def execute_openai_api(self, step: str, text_chunk: str = "", kg_schema: List = None, schema_definition: Dict = None):
        """
        执行OpenAI API请求
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :param text_chunk: 用户请求的文本块
        :param kg_schema: 知识架构
        :param schema_definition: 知识架构定义的路径
        """
        # LLM请求处理：
        instruction1_response = self.execute_instruction1(step, text_chunk, kg_schema, schema_definition)
        instruction2_response, entity_type_dic = self.execute_instruction2(step, text_chunk, kg_schema, schema_definition, instruction1_response)
        entity_attributes_dic, triples_and_type_dic, type_attributes_dic = self.execute_instruction3(
            step,
            text_chunk,
            kg_schema,
            instruction2_response,
            entity_type_dic)
        # 将三个instruction的回复转换为KG定义的json格式
        final_kg_json = data_processor.convert_to_kg_json_format(
            triples_and_type_dic=triples_and_type_dic,
            entity_attributes_dic=entity_attributes_dic,
            type_attributes_dic=type_attributes_dic)
        # 分别得到一般形式的三元组和其对应的关系类型，被提取的带类型标签的实体，以及实体属性字典 -> 将其转换为KG定义的json格式
        return final_kg_json

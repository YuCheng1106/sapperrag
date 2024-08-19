
import random
from openai import OpenAI
from ....index.graph.infering.LLM_API_Parameter import OPENAI_API_PARAMETER


# 未来如果需要的话，可以修改LLM_API与LLM_API_Parameter，使其更加通用化，不仅仅是OpenAI
class OpenAIResponseGetter:
    def __init__(self, openai_api_parameter: OPENAI_API_PARAMETER):
        """
        :param openai_api_parameter: OpenAI API的参数对象
        """
        self.openai_api_parameter = openai_api_parameter

    def select_model(self, step: str) -> str:
        if self.openai_api_parameter.model:
            model = self.openai_api_parameter.model
        elif step == "schema_construction":
            model = self.openai_api_parameter.schema_construction_model
        elif step == "knowledge_extraction":
            model = self.openai_api_parameter.knowledge_extraction_model
        elif step == "knowledge_reasoning":
            model = self.openai_api_parameter.knowledge_reasoning_model
        elif step == "reasoning_validation":
            model = self.openai_api_parameter.reasoning_validation_model
        else:
            raise ValueError("Unsupported step")
        return model

    def get_response(self, request: str, step) -> str:
        """
        获取OpenAI的回复
        :param step: 请求所处理的步骤：Schema构建、知识提取、知识推理、推理验证？
        :param request: 请求的内容
        :return: OpenAI的回复
        """

        # 随机打乱api_key_list,避免同一key的重复多次调用
        random.shuffle(self.openai_api_parameter.openai_api_key_list)

        # 根据流程步骤的不同，选择对应的用户指定的模型。
        model = self.select_model(step)
        client = OpenAI(
            api_key=self.openai_api_parameter.openai_api_key_list[0],
            base_url=self.openai_api_parameter.base_url,
            organization=self.openai_api_parameter.organization,
            timeout=self.openai_api_parameter.timeout,
            max_retries=self.openai_api_parameter.max_retries
        )
        # 调用OpenAI的API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": request}
            ],
            # 解包额外参数
            max_tokens=self.openai_api_parameter.max_tokens,
            temperature=self.openai_api_parameter.temperature,

        )
        # 返回OpenAI的回复
        return response.choices[0].message.content

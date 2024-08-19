# ----------------------------所有LLM的参数配置类皆在此处
from typing import List


class OPENAI_API_PARAMETER:
    # 请在此处填入您的OpenAI API密钥，以及相关的OPENAI API请求头参数
    def __init__(
            self,
            openai_api_key_list: List = None,
            base_url: str = "https://api.rcouyi.com/v1",
            organization: str = "",
            timeout: float = 180.0,
            max_retries: int = 3,

            # 框架分为三个总体部分：Schema构建、知识提取、知识推理、推理验证 ；每个部分都有默认使用模型，若传入model，即代表限定所有步骤都使用
            # 同一个模型，否则配置各项模型参数 OR 不传入model参数，即使用默认模型
            model: str = "",
            schema_construction_model: str = "",
            knowledge_extraction_model: str = "",
            knowledge_reasoning_model: str = "",
            reasoning_validation_model: str = "",

            max_tokens: int = 4096,
            temperature: float = 1.0,
    ):
        """
        初始化OpenAI API参数
        :param openai_api_key_list: 你的OpenAI API Key
        :param base_url: 默认使用官方API地址， https://api.openai.com/v1。可填入中转url
        :param organization: 你的Open
        :param timeout: 请求超时时间
        :param max_retries: 最大重试次数
        :param model: 指定使用的模型，默认使用gpt-4o
        :param schema_construction_model: 指定使用的模型，默认使用gpt-4o
        :param knowledge_extraction_model: 指定使用的模型，默认使用gpt-4o
        :param knowledge_reasoning_model: 指定使用的模型，默认使用gpt-4o
        :param reasoning_validation_model: 指定使用的模型，默认使用gpt-4o
        :param max_tokens: 最大token数
        :param temperature: 温度参数
        """
        # 客户端openai对象参数配置：
        self.openai_api_key_list = openai_api_key_list
        self.base_url = base_url
        self.organization = organization
        self.timeout = timeout
        self.max_retries = max_retries

        # 请求response参数配置：
        self.model = model
        self.schema_construction_model = schema_construction_model
        self.knowledge_extraction_model = knowledge_extraction_model
        self.knowledge_reasoning_model = knowledge_reasoning_model
        self.reasoning_validation_model = reasoning_validation_model

        # 请求response参数配置：
        self.max_tokens = max_tokens
        self.temperature = temperature


class WenXin_API_PARAMETER:
    # 文心一言API参数配置
    pass


class StarFire_API_PARAMETER:
    # 星火API参数配置
    pass


class XunFei_API_PARAMETER:
    # 讯飞API参数配置
    pass


class Gemini_API_PARAMETER:
    # Gemini API参数配置
    pass


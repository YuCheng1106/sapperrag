import os

from sapperrag.index.graph.infering.LLM_API_Parameter import OPENAI_API_PARAMETER

openai_api_parameter = OPENAI_API_PARAMETER(
    openai_api_key_list=os.getenv("OPENAI_KEY_LIST"),
    base_url="https://api.rcouyi.com/v1",
    schema_construction_model="gpt-4o",
    knowledge_reasoning_model="gpt-4o",
    knowledge_extraction_model="gpt-4o",
    reasoning_validation_model="gpt-3.5-turbo"
)

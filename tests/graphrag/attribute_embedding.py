import openai
import numpy as np
import json
import concurrent.futures


class AttributeEmbedder:
    def __init__(self, api_key, api_base):
        # 初始化OpenAI API的键和基础URL
        self.api_key = api_key
        self.model_name = 'text-embedding-3-small'
        openai.api_key = self.api_key
        openai.api_base = api_base

    def embed_attributes(self, attributes):
        # 将属性字典转换为单个字符串以进行嵌入
        attributes_text = " ".join([f"{k}: {v}" for k, v in attributes.items()])

        # 调用OpenAI API以获取嵌入
        response = openai.Embedding.create(
            input=attributes_text,
            model=self.model_name
        )

        # 从响应中提取嵌入向量
        attribute_vector = np.array(response['data'][0]['embedding'])
        return attribute_vector

    def add_attribute_vectors(self, df):
        # 处理DataFrame中的每一行以添加属性向量
        def process_row(row):
            node_details = json.loads(row['node_details'])
            attributes = node_details.get('attributes', {})
            attribute_vector = self.embed_attributes(attributes)
            return attribute_vector

        attribute_vectors = []

        # 使用线程池并行处理每一行
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_row, row) for _, row in df.iterrows()]
            for future in concurrent.futures.as_completed(futures):
                attribute_vectors.append(future.result())

        # 将属性向量添加到DataFrame中
        df['attribute_vector'] = attribute_vectors
        return df

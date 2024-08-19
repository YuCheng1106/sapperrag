import numpy as np
import json
import concurrent.futures


class AttributeEmbedder:
    def __init__(self, text_embeder):
        # 初始化OpenAI API的键和基础URL
        self.text_embeder = text_embeder

    def embed_attributes(self, attributes):
        # 将属性字典转换为单个字符串以进行嵌入
        attributes_text = " ".join([f"{k}: {v}" for k, v in attributes.items()])

        # 调用OpenAI API以获取嵌入
        response = self.text_embeder.embed(attributes_text)

        # 从响应中提取嵌入向量
        attribute_vector = np.array(response)
        return attribute_vector

    def add_attribute_vectors(self, entities):
        # 处理DataFrame中的每一行以添加属性向量
        def process_row(row):
            attributes = row.attributes
            attribute_vector = self.embed_attributes(attributes)
            return attribute_vector

        # 使用线程池并行处理每一行
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_row, row): idx for idx, row in enumerate(entities)}

            for future in concurrent.futures.as_completed(futures):
                idx = futures[future]
                try:
                    attribute_vector = future.result()
                    # 将嵌入向量添加到对应的DataFrame行中
                    entities[idx].description_embedding = attribute_vector.tolist()
                except Exception as e:
                    print(f"Error processing row {idx}: {e}")

        return entities

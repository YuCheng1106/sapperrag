import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def map_query_to_entities(query, text_embedder, all_entities, k=20):
    if query != "":
        # 生成查询的嵌入
        query_embed = np.array(text_embedder(query))

        # 确保query_embed是二维数组
        if query_embed.ndim == 1:
            query_embed = query_embed.reshape(1, -1)

        # 初始化一个列表存储每个实体的相似度
        similarities = []

        # 计算查询与所有实体之间的相似度
        for entity in all_entities:
            entity_embed = np.array(entity.description_embedding)

            # 确保entity_embed是二维数组
            if entity_embed.ndim == 1:
                entity_embed = entity_embed.reshape(1, -1)

            similarity = cosine_similarity(query_embed, entity_embed)[0][0]
            similarities.append((entity, similarity))

        # 根据相似度对实体进行排序，并选择前 k 个相似的实体
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k_entities = [entity for entity, similarity in similarities[:k]]

        return top_k_entities
    return []


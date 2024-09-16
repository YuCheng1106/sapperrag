import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Union

from sapperrag.model import TextChunk


def map_query_to_text_chunks(
    query: str,
    text_chunks: List[TextChunk],
    vector_db: pd.DataFrame,
    text_embedder
) -> List[TextChunk]:
    # 获取查询的嵌入向量
    query_emb = np.array(text_embedder.embed(query), dtype=np.float32).reshape(1, -1)

    # 计算每个存储的嵌入向量与查询嵌入向量的余弦相似度
    similarities = []
    for _, row in vector_db.iterrows():
        # 将存储的嵌入向量转换为 numpy 数组
        stored_emb = np.array(row.Embedding, dtype=np.float32).reshape(1, -1)
        sim = cosine_similarity(query_emb, stored_emb)[0][0]
        similarities.append(sim)

    # 将相似度添加到 DataFrame 中
    vector_db['similarity'] = similarities

    # 根据相似度排序
    sorted_vector_db = vector_db.sort_values(by='similarity', ascending=False)

    # 将 vector_db 的 ID 列转为集合以加快查找速度
    sorted_ids = set(sorted_vector_db['ID'])

    # 将 text_chunks 转换为一个以 ID 为键的字典，以便快速查找
    text_chunks_dict = {chunk.id: chunk for chunk in text_chunks}

    # 根据排序的 ID 提取相应的文本块
    sorted_chunks = [text_chunks_dict[chunk_id] for chunk_id in sorted_ids if chunk_id in text_chunks_dict]

    return sorted_chunks

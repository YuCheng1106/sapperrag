from __future__ import annotations

from typing import Any
import pandas as pd
import tiktoken
from ....retriver.context_builder.builders import TextContextBuilder
from ....retriver.structured_search.text_search.query_embedding import map_query_to_text_chunks
from ....retriver.context_builder.text_context import build_text_context
import json


class TextSearchContext(TextContextBuilder):
    def __init__(self, text_chunks, vector_db, text_embedder):
        self.text_chunks = text_chunks
        self.vector_db = vector_db
        self.text_embedder = text_embedder

    def build_context(self, query: str, **kwargs: Any) -> Any:
        """Build the context for the local search mode."""
        # 示例实现：将查询和其他参数构建成一个上下文字典
        token_encoder = tiktoken.get_encoding("cl100k_base")

        sorted_chunks = map_query_to_text_chunks(query, self.text_chunks, self.vector_db, self.text_embedder)

        final_context = list[str]()
        final_context_data = dict[str, pd.DataFrame]()

        text_context, text_context_data = build_text_context(sorted_chunks, token_encoder)

        if text_context.strip() != "":
            final_context.append(str(text_context))
            final_context_data["Text"] = text_context_data

        return "\n\n".join(final_context), final_context_data

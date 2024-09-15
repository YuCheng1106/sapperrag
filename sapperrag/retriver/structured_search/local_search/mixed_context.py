from __future__ import annotations

from typing import Any
import pandas as pd
import tiktoken
from ....retriver.context_builder.builders import LocalContextBuilder
from ....retriver.context_builder.entity_extraction import map_query_to_entities
from ....retriver.context_builder.entity_context import build_entity_context
from ....retriver.context_builder.relationship_context import build_relationship_context
from ....retriver.context_builder.community_context import build_community_context
from ....retriver.context_builder.source_context import build_source_context
import json

class LocalSearchMixedContext(LocalContextBuilder):
    def __init__(self, entities, relationships, text_chunks, community_reports, text_embedder):
        self.entities = entities
        self.relationships = relationships
        self.text_chunks = text_chunks
        self.text_embedder = text_embedder
        self.community_reports = community_reports

    def build_context(self, query: str, **kwargs: Any) -> Any:
        """Build the context for the local search mode."""
        # 示例实现：将查询和其他参数构建成一个上下文字典
        token_encoder = tiktoken.get_encoding("cl100k_base")

        selected_entities = map_query_to_entities(query, self.text_embedder, self.entities)

        final_context = list[str]()
        final_context_data = dict[str, pd.DataFrame]()

        source_context, source_context_data = build_source_context(text_chunks=self.text_chunks,
                                                                   selected_entities=selected_entities,
                                                                   token_encoder=token_encoder)
        if source_context.strip() != "":
            final_context.append(str(source_context))
            final_context_data["Sources"] = source_context_data

        community_context, community_context_data = build_community_context(self.community_reports,
                                                                            selected_entities=selected_entities,
                                                                            token_encoder=token_encoder)
        if community_context.strip() != "":
            final_context.append(str(community_context))
            final_context_data["Reports"] = community_context_data

        entity_context, entity_context_data = build_entity_context(selected_entities, token_encoder=token_encoder)

        if entity_context.strip() != "":
            final_context.append(str(entity_context))
            final_context_data["Entities"] = entity_context_data

        relationship_context, relationship_context_data = build_relationship_context(selected_entities=selected_entities,
                                                                                     token_encoder=token_encoder,
                                                                                     relationships=self.relationships,
                                                                                     entities=self.entities)

        if relationship_context.strip() != "":
            final_context.append(str(relationship_context))
            final_context_data["Relationship"] = relationship_context_data

        return "\n\n".join(final_context), final_context_data

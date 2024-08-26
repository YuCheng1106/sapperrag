from typing import cast, Any

import pandas as pd
from sapperrag.model.text_chunk import TextChunk
from sapperrag.model.entity import Entity
from sapperrag.model.relationship import Relationship
from sapperrag.llm.text_utils import num_tokens


def build_source_context(
        selected_entities: list[Entity],
        text_chunks: list[TextChunk],
        token_encoder,
        column_delimiter: str = "|",
        max_tokens: int = 8000,
        context_name: str = "Sources",
):
    if text_chunks is None or len(text_chunks) == 0:
        return ("", {})
    # add context header
    current_context_text = f"-----{context_name}-----" + "\n"
    current_token = 0

    # add header
    header = ["id", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    select_chunks = set()
    for entity in selected_entities:
        select_chunks.update(entity.text_chunk_ids)

    for unit in text_chunks:
        # if unit.id in select_chunks:.q213=
        if unit.id in select_chunks:
            new_context = [
                unit.id,
                unit.text
            ]
            new_context_text = column_delimiter.join(new_context) + "\n"

            current_context_text += new_context_text
            all_context_records.append(new_context)
            current_token += num_tokens(current_context_text, token_encoder)
            if current_token >= max_tokens:
                break

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(
            all_context_records[1:], columns=cast(Any, all_context_records[0])
        )
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df

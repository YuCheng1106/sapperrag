from typing import cast, Any

import pandas as pd
from sapperrag.model.text_chunk import TextChunk
from sapperrag.model.entity import Entity


def build_source_context(
    select_entities: list[Entity],
    text_chunks: list[TextChunk],
    column_delimiter: str = "|",
    max_tokens: int = 8000,
    context_name: str = "Sources",
):
    if text_chunks is None or len(text_chunks) == 0:
        return ("", {})
    # add context header
    current_context_text = f"-----{context_name}-----" + "\n"

    # add header
    header = ["id", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    select_chunks = set()
    for entity in select_entities:
        select_chunks.update(entity.text_chunk_ids)

    for unit in text_chunks:
        if unit.id in select_chunks:
            new_context = [
                unit.id,
                unit.text
            ]
            new_context_text = column_delimiter.join(new_context) + "\n"

            current_context_text += new_context_text
            all_context_records.append(new_context)

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(
            all_context_records[1:], columns=cast(Any, all_context_records[0])
        )
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df

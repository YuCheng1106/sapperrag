from typing import cast, Any

import pandas as pd
from sapperrag.model.text_chunk import TextChunk
from sapperrag.llm.text_utils import num_tokens


def build_text_context(
        sorted_chunks: list[TextChunk],
        token_encoder,
        k: int = 3,
        column_delimiter: str = "|",
        max_tokens: int = 8000,
        context_name: str = "Text",
):
    if sorted_chunks is None or len(sorted_chunks) == 0:
        return ("", {})
    selected_chunks = sorted_chunks[:k]
    # add context header
    current_context_text = f"-----{context_name}-----" + "\n"
    current_token = 0

    # add header
    header = ["id", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    for unit in selected_chunks:
        new_context = [
            unit.id,
            str(unit.text)
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

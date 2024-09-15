import pandas as pd
from typing import Any, cast
from sapperrag.llm.text_utils import num_tokens


def build_entity_context(
        selected_entities,
        token_encoder,
        context_name="Entities",
        column_delimiter: str = "|",
        max_tokens: int = 8000
):
    current_context_text = f"-----{context_name}-----" + "\n"
    current_token = 0
    header = ["id", "entity_type", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    for entity in selected_entities:
        description = " ".join([f"{k}: {v}" for k, v in entity.attributes.items()])
        new_context = [
            entity.id if entity.id else "",
            entity.type,
            description,
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

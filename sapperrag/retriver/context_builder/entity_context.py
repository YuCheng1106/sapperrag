import pandas as pd
from typing import Any, cast


def build_entity_context(
        selected_entities,
        context_name="Entities",
        column_delimiter: str = "|",
        max_tokens: int = 8000
):
    current_context_text = f"-----{context_name}-----" + "\n"
    header = ["id", "entity_type", "description"]
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

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(
            all_context_records[1:], columns=cast(Any, all_context_records[0])
        )
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df

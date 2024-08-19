import pandas as pd
from sapperrag.model.community import Community
from sapperrag.model.entity import Entity
from typing import List


def build_community_context(
        select_entities: List[Entity],
        community_reports: List[Community],
        column_delimiter: str = "|",
        max_tokens: int = 8000,
        context_name: str = "Community Reports",
):
    if not community_reports:
        return "", pd.DataFrame()

    # 添加上下文标题
    current_context_text = f"-----{context_name}-----\n"

    # 添加表头
    header = ["id", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    # 选择符合条件的报告
    select_reports = []
    for entity in select_entities:
        for report in community_reports:
            if entity.id in report.entity_ids and report not in select_reports:
                select_reports.append(report)

    # 构建上下文文本和记录
    for report in select_reports:
        new_context = [
            report.id,
            report.full_content
        ]
        new_context_text = column_delimiter.join(new_context) + "\n"

        current_context_text += new_context_text
        all_context_records.append(new_context)

    # 构建 DataFrame
    if len(all_context_records) > 1:
        record_df = pd.DataFrame(all_context_records[1:], columns=all_context_records[0])
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df

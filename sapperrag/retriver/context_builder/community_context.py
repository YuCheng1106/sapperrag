from __future__ import annotations
import json
import ast
import tiktoken
import pandas as pd
from sapperrag.model.community import Community
from sapperrag.llm.text_utils import num_tokens
from sapperrag.model.entity import Entity
from typing import List


def build_community_context(
        community_reports: list,
        selected_entities: List[Entity],
        token_encoder,
        column_delimiter: str = "|",
        max_tokens: int = 8000,
        min_community_rank: int = 5,
        context_name: str = "Reports",
):
    sorted_community_reports = sort_community(community_reports, selected_entities)

    def _is_included(report: community_reports) -> bool:
        return report.rating is not None and report.rating >= min_community_rank

    selected_reports = [report for report in sorted_community_reports if _is_included(report)]

    if not selected_reports:
        return "", pd.DataFrame()

    # 添加上下文标题
    current_context_text = f"-----{context_name}-----\n"
    current_token = 0

    # 添加表头
    header = ["id", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    # 构建上下文文本和记录
    for report in selected_reports:
        new_context = [
            report.id,
            json.loads(report.full_content)["summary"]
        ]
        new_context_text = column_delimiter.join(new_context) + "\n"

        current_context_text += new_context_text
        all_context_records.append(new_context)
        current_token += num_tokens(current_context_text, token_encoder)
        if current_token >= max_tokens:
            break

    # 构建 DataFrame
    if len(all_context_records) > 1:
        record_df = pd.DataFrame(all_context_records[1:], columns=all_context_records[0])
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df


def sort_community(community_reports, selected_entities: List[Entity]):
    community_matches = {}
    for entity in selected_entities:
        # 计算社区所包含选中实体的数量
        if entity.community_ids:
            for community_id in ast.literal_eval(entity.community_ids):
                community_matches[community_id] = (
                        community_matches.get(community_id, 0) + 1
                )

    community_reports_id_dict = {
        community.id: community for community in community_reports
    }

    # 按匹配实体的数量和排名对社区进行排序

    # 防止部分社区没有报告
    select_communities = [
        community_reports_id_dict.get(community_id)
        for community_id in community_matches
        if community_id in community_reports_id_dict
    ]
    for community in select_communities:
        if community.attributes is None:
            community.attributes = {}
        community.attributes["matches"] = community_matches[community.id]
    select_communities.sort(
        key=lambda x: (x.attributes["matches"], x.level),  # type: ignore
        reverse=True,  # type: ignore
    )
    for community in select_communities:
        del community.attributes["matches"]  # type: ignore
    return select_communities

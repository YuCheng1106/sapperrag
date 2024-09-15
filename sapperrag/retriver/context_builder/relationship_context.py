from collections import defaultdict
from typing import cast, Any
from sapperrag.llm.text_utils import num_tokens

import pandas as pd


def build_relationship_context(
        selected_entities,
        relationships,
        token_encoder,
        entities,
        context_name="Relationships",
        top_k_relationships: int = 10,
        column_delimiter: str = "|",
        max_tokens: int = 8000
):
    selected_relationships = _filter_relationships(
        selected_entities=selected_entities,
        relationships=relationships,
        top_k_relationships=top_k_relationships
    )

    current_context_text = f"-----{context_name}-----" + "\n"
    current_token = 0
    header = ["relation_type", "source", "target", "description"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    for relationship in selected_relationships:
        description = " ".join([f"{k}: {v}" for k, v in relationship.attributes.items()])
        new_context = [
            relationship.type,
            get_entity_title_by_id(entities=entities, given_id=relationship.source),
            get_entity_title_by_id(entities=entities, given_id=relationship.target),
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


def _filter_relationships(
        selected_entities,
        relationships,
        top_k_relationships: int = 10,
        relationship_ranking_attributes: str = "weight",
):
    """Filter and sort relationships based on a set of selected entities and a ranking attributes."""
    # First priority: in-network relationships (i.e. relationships between selected entities)
    selected_entity_ids = [entity.id for entity in selected_entities]
    in_network_relationships = [
        relationship
        for relationship in relationships
        if relationship.source in selected_entity_ids
        and relationship.target in selected_entity_ids
    ]

    # Second priority -  out-of-network relationships
    # (i.e. relationships between selected entities and other entities that are not within the selected entities)
    source_relationships = [
        relationship
        for relationship in relationships
        if relationship.source in selected_entity_ids
        and relationship.target not in selected_entity_ids
    ]
    target_relationships = [
        relationship
        for relationship in relationships
        if relationship.target in selected_entity_ids
        and relationship.source not in selected_entity_ids
    ]

    out_network_relationships = source_relationships + target_relationships

    # within out-of-network relationships, prioritize mutual relationships
    # (i.e. relationships with out-network entities that are shared with multiple selected entities)

    out_network_source_ids = [
        relationship.source
        for relationship in out_network_relationships
        if relationship.source not in selected_entity_ids
    ]
    out_network_target_ids = [
        relationship.target
        for relationship in out_network_relationships
        if relationship.target not in selected_entity_ids
    ]
    out_network_entity_ids = list(
        set(out_network_source_ids + out_network_target_ids)
    )
    out_network_entity_links = defaultdict(int)
    for entity_name in out_network_entity_ids:
        targets = [
            relationship.target
            for relationship in out_network_relationships
            if relationship.source == entity_name
        ]
        sources = [
            relationship.source
            for relationship in out_network_relationships
            if relationship.target == entity_name
        ]
        out_network_entity_links[entity_name] = len(set(targets + sources))

    # sort out-network relationships by number of links and rank_attributes
    for rel in out_network_relationships:
        if rel.attributes is None:
            rel.attributes = {}
        rel.attributes["links"] = (
            out_network_entity_links[rel.source]
            if rel.source in out_network_entity_links
            else out_network_entity_links[rel.target]
        )

    # sort by attributes[links] first, then by ranking_attributes
    if relationship_ranking_attributes == "weight":
        out_network_relationships.sort(
            # key=lambda x: (x.attributes["links"], x.attributes["weight"]),
            key=lambda x: (x.attributes["links"]),
            reverse=True,  # type: ignore
        )
    else:
        out_network_relationships.sort(
            key=lambda x: (
                x.attributes["links"],  # type: ignore
                x.attributes[relationship_ranking_attributes],  # type: ignore
            ),  # type: ignore
            reverse=True,
        )

    relationship_budget = top_k_relationships * len(selected_entities)
    return in_network_relationships + out_network_relationships[:relationship_budget]


def get_entity_title_by_id(entities, given_id):
    for entity in entities:
        if entity.id == given_id:
            return entity.title

import json

import pandas as pd

from sapperrag.model.community import Community
from sapperrag.model.entity import Entity
from sapperrag.model.relationship import Relationship
from sapperrag.model.text_chunk import TextChunk


def load_entities(csv_file_path: str):
    df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(Entity(
            id=row.id,
            short_id=row.short_id,
            title=row.title,
            type=row.type,
            text_chunk_ids=json.loads(row.text_chunk_ids.replace("'", '"')),
            description_embedding=json.loads(row.description_embedding) if not pd.isna(row.description_embedding) else None,
            attributes=json.loads(row.attributes.replace("'", '"'))
        ))
    return dataclass_list


def load_text_chunks(csv_file_path: str):
    df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(TextChunk(
            id=row.id,
            short_id=row.short_id,
            text=row.text,
            document_ids=row.document_ids
        ))
    return dataclass_list


def load_relationships(csv_file_path: str):
    df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(Relationship(
            id=row.id,
            source=row.source,
            target=row.target,
            short_id=row.short_id,
            type=row.type,
            attributes=json.loads(row.attributes.replace("'", '"'))
        ))
    return dataclass_list


def load_community(csv_file_path: str):
    df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(Community(
            id=row.id,
            short_id=row.short_id,
            entity_ids=json.loads(row.entity_ids.replace("'", '"')),
            full_content=row.full_content,
            title=row.title
        ))
    return dataclass_list



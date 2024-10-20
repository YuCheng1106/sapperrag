import json
from typing import List

import numpy as np
import pandas as pd

from sapperrag.model import Document
from sapperrag.model.community import Community
from sapperrag.model.entity import Entity
from sapperrag.model.relationship import Relationship
from sapperrag.model.text_chunk import TextChunk


def load_entities(csv_file_path: str, communities=None, entities=None):
    if communities is None:
        df = pd.read_csv(csv_file_path)

        dataclass_list = []
        for _, row in df.iterrows():
            dataclass_list.append(Entity(
                id=row.id,
                short_id=row.short_id,
                title=row.title,
                type=row.type,
                community_ids=row.community_ids,
                text_chunk_ids=json.loads(row.text_chunk_ids.replace("'", '"')),
                description_embedding=json.loads(row.description_embedding) if not pd.isna(
                    row.description_embedding) else None,
                attributes=json.loads(row.attributes.replace("'", '"'))
            ))

        return dataclass_list
    else:
        entity_to_communities = {entity.id: [] for entity in entities}

        for community in communities:
            for community_entity_id in community.entity_ids:
                if community_entity_id in entity_to_communities:
                    entity_to_communities[community_entity_id].append(community.id)

        for entity in entities:
            entity.community_ids = entity_to_communities[entity.id]

    return entities


def load_text_chunks(csv_file_path: str) -> List[TextChunk]:
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
            rating=row.rating,
            title=row.title
        ))
    return dataclass_list


def load_document(csv_file_path: str):
    df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(Document(
            id=row.id,
            short_id=row.short_id,
            title=row.title,
            raw_content=row.raw_content,
            type=row.type
        ))
    return dataclass_list


def load_embeddings(file_path: str):
    # Load the data from the .npz file
    with np.load(file_path, allow_pickle=True) as data:
        ids = data['ids']
        embeddings = data['embeddings']

        # Convert byte IDs to string if necessary
        ids = [id.decode('utf-8') if isinstance(id, bytes) else id for id in ids]

        # Create a DataFrame
        df = pd.DataFrame({
            'ID': ids,
            'Embedding': list(embeddings)
        })

        return df

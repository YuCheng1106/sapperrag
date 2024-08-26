import json
import pandas as pd
from uuid import uuid4
from sapperrag.model.text_chunk import TextChunk
from sapperrag.model.entity import Entity
from sapperrag.model.relationship import Relationship

# Define file paths
file_path = 'kg.json'
text_source_path = 'source.csv'

# Load JSON data
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Load CSV data
source = pd.read_csv(text_source_path)

# Create TextChunk objects
text_chunks = [
    TextChunk(id=row.ID, text=row.TripleSource, short_id=row.ID)
    for _, row in source.iterrows()
]

entities = []
relations = []

# Dictionary to keep track of processed entities
entity_dict = {}
# id
# title
# short_id
# text_chunk_ids
# attributes
# description

def process_entity(entity_data: dict, text_chunks_id: []) -> str:
    """Process an entity, assign a UUID if not already processed, and return the entity ID."""
    entity_key = json.dumps(entity_data, sort_keys=True, ensure_ascii=False)
    entity = {}
    if entity_key not in entity_dict:
        entity["id"] = str(uuid4())
        entity["short_id"] = entity["id"]
        entity["text_chunk_ids"] = json.dumps(text_chunks_id)
        entity["attributes"] = json.dumps(entity_data.get('Attributes'))
        entity["title"] = entity_data.get('Name')
        entity["type"] = entity_data.get('Type')
        entity["description"] = json.dumps(entity_data.get('Attributes'))
        entity_dict[entity_key] = entity

    return entity_dict[entity_key]["id"]


# Process each item in the JSON data
for item in data:
    directional_entity = item.get("DirectionalEntity")
    directed_entity = item.get("DirectedEntity")
    relation = item.get("Relation")
    text_chunks_id  = item.get("ID")
    if directional_entity:
        source_id = process_entity(directional_entity, [text_chunks_id])

    if directed_entity:
        target_id = process_entity(directed_entity, [text_chunks_id])

    if relation:
        relation["Source"] = source_id
        relation["Target"] = target_id
        relations.append(Relationship(
            target=target_id,
            source=source_id,
            type= relation.get("Type"),
            id= str(uuid4()),
            short_id=str(uuid4()),
            text_unit_ids=json.dumps([text_chunks_id]),
            attributes=json.dumps(relation.get("Attributes"))
        ))

# If necessary, convert entities and relations to Entity objects or a DataFrame
entities = [
    Entity.from_dict(entity_data)
    for entity_data in entity_dict.values()
]


# Example: Converting relations to a DataFrame (if needed)
relations_df = pd.DataFrame(relations)
entities_df = pd.DataFrame(entities)

# Example: Saving entities and relations to a file or further processing
entities_df.to_csv('entities.csv', index=False)
relations_df.to_csv('relations.csv', index=False)

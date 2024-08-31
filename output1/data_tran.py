import csv

from sapperrag.index.graph.cli import save_dataclasses_to_csv
from sapperrag.model.model_load import load_entities


def remove_unknown_attributes(entities):
    for entity in entities:
        keys_to_remove = [key for key, value in entity.attributes.items() if value == "Unknown" or value == "unknown"]
        for key in keys_to_remove:
            del entity.attributes[key]
    return entities


entities = load_entities(r"D:\sapperrag\output1\entities.csv")
data = remove_unknown_attributes(entities=entities)

save_dataclasses_to_csv(data, "../output_try/entities.csv")

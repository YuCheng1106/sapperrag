import json
import torch
from transformers import BertModel, BertTokenizer, BertConfig
import numpy as np

# 定义文件路径
file_path = '../input/kg/graph.json'

# 读取 JSON 文件
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 初始化实体和关系的列表
entities = []
relations = []

# 用于存储实体的字典，用于去重
entity_dict = {}
next_id = 0

# 处理数据
for item in data:
    directional_entity = item.get("DirectionalEntity")
    directed_entity = item.get("DirectedEntity")
    relation = item.get("Relation")

    if directional_entity:
        entity_key = json.dumps(directional_entity, sort_keys=True, ensure_ascii=False)
        if entity_key not in entity_dict:
            directional_entity["id"] = str(next_id)
            entity_dict[entity_key] = directional_entity
            next_id += 1
        source_id = entity_dict[entity_key]["id"]

    if directed_entity:
        entity_key = json.dumps(directed_entity, sort_keys=True, ensure_ascii=False)
        if entity_key not in entity_dict:
            directed_entity["id"] = str(next_id)
            entity_dict[entity_key] = directed_entity
            next_id += 1
        target_id = entity_dict[entity_key]["id"]

    if relation:
        relation["Source"] = source_id
        relation["Target"] = target_id
        relations.append(relation)

# 将去重后的实体从字典中提取到列表中
entities = list(entity_dict.values())

# 定义文件路径
model_path = "../embedding/model/pytorch_model.bin"
config_path = "../embedding/model/config.json"
vocab_path = "../embedding/model/vocab.txt"

# 加载配置文件
config = BertConfig.from_json_file(config_path)

# 初始化模型
model = BertModel(config)

# 加载模型权重
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

# 加载分词器
tokenizer = BertTokenizer(vocab_file=vocab_path)


def get_sentence_embedding(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    # 获取 [CLS] token 的向量
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return cls_embedding


# 生成描述嵌入并保存到文件
print("Entities:")
for entity in entities:
    description = " ".join([f"{k}: {v}" for k, v in entity["Attributes"].items()])
    entity["description_embedding"] = get_sentence_embedding(description, model, tokenizer).tolist()
    print(entity)

with open("../input/kg/entities.json", "w", encoding="utf-8") as f:
    json.dump(entities, f, ensure_ascii=False, indent=4)


print("\nRelations:")
for relation in relations:
    description = " ".join([f"{k}: {v}" for k, v in relation["Attributes"].items()])
    relation["description_embedding"] = get_sentence_embedding(description, model, tokenizer).tolist()
    print(relation)

with open("../input/kg/relations.json", "w", encoding="utf-8") as f:
    json.dump(relations, f, ensure_ascii=False, indent=4)

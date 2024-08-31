# coding=utf-8
import csv


# 对指定列的值进行修改的函数
def modify_value(value: str):
    # 进行修改
    modified_value = value[:8]
    return modified_value


# 读取 CSV 文件并写回修改后的数据
with open(r'D:\sapperrag\output\communities.csv', 'r', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = []

    # 遍历所有行
    for row in reader:
        # 读取指定列的值
        value = row['id']
        # 对值和列表进行修改
        modified_value = modify_value(value)
        row['id'] = modified_value

        entity_ids = row['entity_ids'].split(',')  # Assuming entity_ids are comma-separated
        modified_entity_ids = [modify_value(entity_id.strip()) for entity_id in entity_ids]
        row['entity_ids'] = ','.join(modified_entity_ids)

        rows.append(row)

# 写入修改后的数据到文件
with open(r'D:\sapperrag\output\communities_modified.csv', 'w', encoding="utf-8", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

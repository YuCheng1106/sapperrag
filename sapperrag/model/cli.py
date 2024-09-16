from dataclasses import is_dataclass, asdict
from typing import List, Any

import pandas as pd


def save_model_to_csv(dataclasses_list: List[Any], csv_file_path: str):
    if not dataclasses_list:
        raise ValueError("The dataclasses_list is empty.")

    # 检查第一个元素是否为 dataclass
    if not is_dataclass(dataclasses_list[0]):
        raise ValueError("Items in the list must be dataclass instances.")

    # 将每个 dataclass 对象转换为字典
    dict_list = [asdict(item) for item in dataclasses_list]

    # 使用 pandas 创建 DataFrame
    df = pd.DataFrame(dict_list)

    # 保存到 CSV
    df.to_csv(csv_file_path, index=False, encoding='utf-8')

import leidenalg as la
import pandas as pd
import json
import uuid
import igraph as ig


class CommunityDetection:
    def __init__(self, max_comm_size=10, max_level=3, seed=None):
        # 初始化社区检测参数
        self.max_comm_size = max_comm_size
        self.max_level = max_level
        self.seed = seed
        self.node_details_map = {}  # 存储节点详细信息的映射
        self.node_id_map = {}  # 存储节点ID的映射

    def calculate_and_update_degrees(self, kg_data):
        # 计算并更新每个节点的度数
        degree_dict = {}

        for entry in kg_data:
            directional_entity = entry["DirectionalEntity"]["Attributes"]["name"]
            directed_entity = entry["DirectedEntity"]["Attributes"]["name"]

            # 初始化度数为0
            if directional_entity not in degree_dict:
                degree_dict[directional_entity] = 0
            if directed_entity not in degree_dict:
                degree_dict[directed_entity] = 0

            # 增加度数
            degree_dict[directional_entity] += 1
            degree_dict[directed_entity] += 1

        for entry in kg_data:
            directional_entity = entry["DirectionalEntity"]["Attributes"]["name"]
            directed_entity = entry["DirectedEntity"]["Attributes"]["name"]

            # 更新度数到实体属性
            entry["DirectionalEntity"]["Attributes"]["degree"] = degree_dict[directional_entity]
            entry["DirectedEntity"]["Attributes"]["degree"] = degree_dict[directed_entity]

        return kg_data

    def generate_node_ids(self, vertices):
        # 为每个节点生成唯一的UUID
        for vertex in vertices:
            self.node_id_map[vertex] = str(uuid.uuid4())

    def recursive_leiden(self, graph, level=0, prefix='', node_map=None):
        # 递归地应用Leiden算法进行社区检测
        if level > self.max_level:
            return {}, {}

        if node_map is None:
            node_map = {v.index: v.index for v in graph.vs}

        partition = la.find_partition(graph, partition_type=la.ModularityVertexPartition, seed=self.seed)
        communities = partition.membership

        levels = {node_map[v.index]: [] for v in graph.vs}
        community_info = {node_map[v.index]: [] for v in graph.vs}

        for v in graph.vs:
            levels[node_map[v.index]].append(level)
            community_info[node_map[v.index]].append(f"{prefix}L{level}_C{communities[v.index]}")

        for community in set(communities):
            subgraph_indices = [v.index for v in graph.vs if communities[v.index] == community]
            subgraph = graph.subgraph(subgraph_indices)
            sub_node_map = {subgraph.vs[i].index: node_map[subgraph_indices[i]] for i in range(len(subgraph.vs))}

            if 1 < len(subgraph.vs) <= self.max_comm_size:
                sub_prefix = f"{prefix}L{level}_C{community}_"
                sub_levels, sub_community_info = self.recursive_leiden(subgraph, level + 1, sub_prefix, sub_node_map)

                for v in subgraph.vs:
                    if sub_node_map[v.index] not in sub_levels:
                        sub_levels[sub_node_map[v.index]] = []
                    if sub_node_map[v.index] not in sub_community_info:
                        sub_community_info[sub_node_map[v.index]] = []

                for v in subgraph.vs:
                    levels[sub_node_map[v.index]].extend(sub_levels[sub_node_map[v.index]])
                    community_info[sub_node_map[v.index]].extend(sub_community_info[sub_node_map[v.index]])

        return levels, community_info

    def load_data(self, json_file):
        # 从JSON文件中加载数据
        with open(json_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # 计算并更新节点的度数
        json_data = self.calculate_and_update_degrees(json_data)

        vertices = set()
        edges = []

        for item in json_data:
            directional_entity = item["DirectionalEntity"]["Attributes"]["name"]
            directed_entity = item["DirectedEntity"]["Attributes"]["name"]

            vertices.add(directional_entity)
            vertices.add(directed_entity)

            edges.append((directional_entity, directed_entity))

            self.node_details_map[directional_entity] = {
                "attributes": item["DirectionalEntity"]["Attributes"],
                "type": item["DirectionalEntity"]["Type"]
            }
            self.node_details_map[directed_entity] = {
                "attributes": item["DirectedEntity"]["Attributes"],
                "type": item["DirectedEntity"]["Type"]
            }

        # 为每个节点生成唯一ID
        self.generate_node_ids(vertices)

        return list(vertices), edges

    def create_graph(self, vertices, edges):
        # 创建图对象并添加节点和边
        g = ig.Graph(directed=False)
        g.add_vertices(vertices)
        g.add_edges(edges)
        return g

    def detect_communities(self, graph):
        # 检测社区并返回社区信息的DataFrame
        levels, community_info = self.recursive_leiden(graph)

        data = []
        for node in graph.vs:
            node_name = node["name"] if "name" in node.attributes() else node.index
            node_id = self.node_id_map.get(node_name, -1)
            node_details = self.node_details_map.get(node_name, {})
            for level, community in zip(levels[node.index], community_info[node.index]):
                data.append({
                    "community_name": community,
                    "node_id": node_id,
                    "node_name": node_name,
                    "level": level,
                    "node_details": json.dumps(node_details, ensure_ascii=False)
                })

        df = pd.DataFrame(data)

        # 对社区名称进行排序
        df['community_sort_key'] = df['community_name'].apply(self.community_sort_key)
        df.sort_values(by=['level', 'community_sort_key'], inplace=True)
        df.drop(columns=['community_sort_key'], inplace=True)

        df = df[['community_name', 'node_id', 'node_name', 'level', 'node_details']]

        return df

    @staticmethod
    def community_sort_key(community_name):
        # 根据社区名称的层级和社区编号进行排序
        parts = community_name.split('_')
        return tuple(int(part[1:]) for part in parts if part)

    def save_to_csv(self, df, file_name):
        # 将DataFrame保存为CSV文件
        df.to_csv(file_name, index=False)

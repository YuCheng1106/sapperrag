import heapq
import json
import uuid
from collections import defaultdict
from neo4j import GraphDatabase
from py2neo import Node, Graph, Relationship
from tqdm import tqdm
import logging
import threading
import re

logging.basicConfig(level=logging.INFO)


class GraphManager:
    def __init__(self, profile: str = "bolt://localhost:7687", user_name: str = "neo4j", password: str = "12345678",
                 database_name: str = "neo4j"):
        self.profile = profile
        self.user_name = user_name
        self.password = password
        self.database_name = database_name
        self.tenant_id = str(uuid.uuid4())
        try:
            self.graph = self.connect_to_graph(self.profile, self.user_name, self.password, self.database_name)
        except Exception as e:
            logging.error(f"连接图数据库失败: {e}")

    @staticmethod
    def connect_to_graph(profile, user_name, password, database_name):
        return Graph(profile=profile, auth=(user_name, password), name=database_name)

    @staticmethod
    def add_relation_weights(file_path: str) -> dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            logging.error(f"文件 {file_path} 不存在。")
            return {"状态": "错误", "消息": f"文件 {file_path} 不存在。"}
        except json.JSONDecodeError as e:
            logging.error(f"解码文件 {file_path} 的 JSON 失败。{str(e)}")
            return {"状态": "错误", "消息": f"解码文件 {file_path} 的 JSON 失败。{str(e)}"}

        relation_count = defaultdict(int)
        for entry in data:
            relation_type = entry["Relation"]["Attributes"]["Name"]
            relation_count[relation_type] += 1

        total_relations = sum(relation_count.values())
        relation_weights = {rel_type: round(count / total_relations, 2) for rel_type, count in relation_count.items()}

        for entry in data:
            relation_type = entry["Relation"]["Name"]
            weight = relation_weights[relation_type]
            entry["Relation"]["Attributes"]["weight"] = weight

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return {"状态": "成功", "消息": "权重添加成功"}

    def clean_string(self, value):
        # 去除无关字符，只保留字母、数字、下划线和中文字符
        return re.sub(r'[^\w\u4e00-\u9fff]+', '', value)

    def find_existing_entity(self, entity_type, name):
        query = f"MATCH (n:{entity_type} {{Name: $name}}) RETURN n"
        result = self.graph.run(query, name=name).data()
        return result[0]['n'] if result else None

    def import_data(self, json_file: str) -> dict:
        judgement = True
        try:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"导入数据失败: {e}")
            return {"状态": "错误", "消息": f"导入数据失败: {e}"}

        for item in tqdm(data):
            try:
                # 依次获取三元组散列列表中的单个三元组的元素
                directional_entity = item.get('DirectionalEntity')
                relation = item.get('Relation')
                directed_entity = item.get('DirectedEntity')

                # 获取实体的 name 以及其他属性
                source_attributes = directional_entity.get('Attributes', {})
                source_name = directional_entity.get('Name', "")
                if not source_name:
                    continue

                target_attributes = directed_entity.get('Attributes', {})
                target_name = directed_entity.get('Name', "")
                if not target_name:
                    continue

                relation_attributes = relation.get('Attributes', {})
                relation_name = relation.get('Name', "")
                if not relation_name:
                    continue

                # 清理实体类型和属性名
                source_type = self.clean_string(directional_entity.get('Type'))
                target_type = self.clean_string(directed_entity.get('Type'))
                relation_name = self.clean_string(relation_name)

                # 确保 Name 属性存在于 source_attributes 和 target_attributes
                source_attributes['Name'] = source_name
                target_attributes['Name'] = target_name

                # 检查并融合 source 实体
                existing_source_node = self.find_existing_entity(source_type, source_name)
                if existing_source_node:
                    for key, value in source_attributes.items():
                        existing_source_node[key] = value
                    self.graph.push(existing_source_node)
                    source_node = existing_source_node
                else:
                    source_node = Node(source_type, **source_attributes)
                    self.graph.create(source_node)

                # 检查并融合 target 实体
                existing_target_node = self.find_existing_entity(target_type, target_name)
                if existing_target_node:
                    for key, value in target_attributes.items():
                        existing_target_node[key] = value
                    self.graph.push(existing_target_node)
                    target_node = existing_target_node
                else:
                    target_node = Node(target_type, **target_attributes)
                    self.graph.create(target_node)

                # 创建关系，并添加所有属性
                relationship = Relationship(source_node, relation_name, target_node, **relation_attributes)
                self.graph.create(relationship)
            except Exception as e:
                logging.error(f"处理条目失败: {e}")
                judgement = False
                continue

        if judgement:
            return {"状态": "成功", "消息": "信息导入完成。"}
        else:
            return {"状态": "警告", "消息": "数据未成功导入。"}

    def find_all_paths(self, start_node_name: str, end_node_name: str) -> dict:
        if start_node_name == end_node_name:
            return {"状态": "错误", "消息": "输入的起始节点相同。"}

        def dfs(current_node, end_node, visited, path):
            visited.add(current_node)

            for rel in self.graph.match((current_node, None), r_type=None).where("rel.tenant_id = $tenant_id",
                                                                                 tenant_id=self.tenant_id):
                if rel.end_node not in visited:
                    new_path = path[:]
                    new_path.append((rel.__class__.__name__, dict(rel)))
                    new_path.append(
                        (rel.end_node, list(rel.end_node.labels)[0], rel.end_node['name'], dict(rel.end_node)))
                    dfs(rel.end_node, end_node, visited, new_path)

            if current_node == end_node:
                all_paths.append(path[:])

            visited.remove(current_node)

        all_paths = []
        start_node = self.graph.nodes.match(name=start_node_name, tenant_id=self.tenant_id).first()
        end_node = self.graph.nodes.match(name=end_node_name, tenant_id=self.tenant_id).first()

        if start_node is None or end_node is None:
            return {"状态": "错误", "消息": "未找到起始节点或结束节点。"}

        visited = set()
        dfs(start_node, end_node, visited,
            [(start_node, list(start_node.labels)[0], start_node['name'], dict(start_node))])

        paths = []
        for i, path in enumerate(all_paths, 1):
            path_str = ""
            for j, component in enumerate(path):
                if j % 2 == 0:
                    node, node_type, node_name, node_properties = component
                    path_str += f"(类型: {node_type}, 名称: {node_name}, 属性: {node_properties}) -> "
                else:
                    rel_type, rel_properties = component
                    path_str += f"(关系: {rel_type}, 属性: {rel_properties}) -> "
            path_str = path_str.rstrip(" -> ")
            paths.append(f"路径 {i}: {path_str}")

        return {"状态": "成功", "路径": paths}

    def search_node_by_name(self, name: str) -> dict:
        node = self.graph.nodes.match(name=name, tenant_id=self.tenant_id).first()
        if node:
            node_info = {
                "id": node.identity,
                "标签": list(node.labels),
                "属性": dict(node)
            }
            return {"状态": "成功", "节点": node_info}
        else:
            return {"状态": "错误", "消息": "未找到节点。"}

    def find_shortest_path_weighted(self, start_node_name: str, end_node_name: str) -> dict:
        try:
            if start_node_name == end_node_name:
                return {"状态": "错误", "消息": "输入的起始节点相同。"}

            start_node = self.graph.nodes.match(name=start_node_name, tenant_id=self.tenant_id).first()
            end_node = self.graph.nodes.match(name=end_node_name, tenant_id=self.tenant_id).first()

            if start_node is None or end_node is None:
                return {"状态": "错误", "消息": "未找到起始节点或结束节点。"}

            queue = [(0, start_node['name'],
                      [(start_node, list(start_node.labels)[0], start_node['name'], dict(start_node))])]
            visited = {}
            shortest_paths = []
            shortest_length = float('inf')

            while queue:
                current_cost, current_node_name, path = heapq.heappop(queue)

                if current_node_name in visited and visited[current_node_name] < current_cost:
                    continue

                visited[current_node_name] = current_cost

                current_node = self.graph.nodes.match(name=current_node_name, tenant_id=self.tenant_id).first()

                for rel in self.graph.match((current_node, None), r_type=None).where("rel.tenant_id = $tenant_id",
                                                                                     tenant_id=self.tenant_id):
                    next_node = rel.end_node
                    next_node_name = next_node['name']
                    rel_weight = rel.get('weight', 1)
                    new_cost = current_cost + rel_weight
                    new_path = path[:]
                    new_path.append((rel.__class__.__name__, dict(rel)))
                    new_path.append((next_node, list(next_node.labels)[0], next_node_name, dict(next_node)))

                    if next_node == end_node:
                        if new_cost < shortest_length:
                            shortest_length = new_cost
                            shortest_paths = [(new_cost, new_path)]
                        elif new_cost == shortest_length:
                            shortest_paths.append((new_cost, new_path))
                        continue

                    if next_node_name not in visited or visited[next_node_name] > new_cost:
                        heapq.heappush(queue, (new_cost, next_node_name, new_path))

            if shortest_paths:
                paths = []
                for cost, path in shortest_paths:
                    path_str = ""
                    for j, component in enumerate(path):
                        if j % 2 == 0:
                            node, node_type, node_name, node_properties = component
                            path_str += f"(类型: {node_type}, 名称: {node_name}, 属性: {node_properties}) -> "
                        else:
                            rel_type, *rel_properties = component
                            path_str += f"(关系: {rel_type}, 属性: {rel_properties}) -> "
                    path_str = path_str.rstrip(" -> ")
                    paths.append(f"最短路径 (成本: {cost}): {path_str}")
                return {"状态": "成功", "路径": paths}
            else:
                return {"状态": "错误", "消息": "未找到给定节点之间的路径。"}
        except Exception as e:
            logging.error(f"发生错误: {e}")
            return {"状态": "错误", "消息": f"发生错误: {e}"}

    def search_relationship_by_name(self, relation: str) -> dict:
        try:
            relationships = list(self.graph.relationships.match(r_type=relation).where("rel.tenant_id = $tenant_id",
                                                                                       tenant_id=self.tenant_id))

            if relationships:
                rels_info = []
                for relationship in relationships:
                    start_node = relationship.start_node
                    end_node = relationship.end_node
                    rel_type = type(relationship).__name__
                    rel_properties = dict(relationship)

                    start_node_info = {
                        "名称": start_node.get('name', 'N/A'),
                        "标签": list(start_node.labels),
                        "属性": dict(start_node)
                    }

                    end_node_info = {
                        "名称": end_node.get('name', 'N/A'),
                        "标签": list(end_node.labels),
                        "属性": dict(end_node)
                    }

                    rels_info.append({
                        "起始节点": start_node_info,
                        "结束节点": end_node_info,
                        "关系": {
                            "类型": rel_type,
                            "属性": rel_properties
                        }
                    })

                return {"状态": "成功", "关系": rels_info}
            else:
                return {"状态": "错误", "消息": "未找到关系。"}
        except Exception as e:
            logging.error(f"搜索关系时发生错误: {e}")
            return {"状态": "错误", "消息": f"搜索关系时发生错误: {e}"}

    def calculate_entity_ratio(self, filename: str) -> dict:
        try:
            neo4j_uri = self.profile
            neo4j_user = self.user_name
            neo4j_password = self.password

            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            with driver.session() as session:
                result = session.run(f"MATCH (n) WHERE n.tenant_id = $tenant_id RETURN count(n) AS total_entities",
                                     tenant_id=self.tenant_id)
                total_entities_in_kg = result.single()["total_entities"]

            entities = set()
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    for line in file:
                        try:
                            label, name = line.strip().split(' ')
                            entities.add((name, label))
                        except ValueError:
                            logging.warning(f"跳过格式错误的行: {line.strip()}")
            except FileNotFoundError:
                logging.error(f"未找到文件 {filename}。")
                return {"状态": "错误", "消息": f"未找到文件 {filename}。"}

            valid_entities = set()
            with driver.session() as session:
                for entity in entities:
                    name, label = entity
                    query = f"MATCH (n:{label} {{name: $name, tenant_id: $tenant_id}}) RETURN count(n) AS count"
                    result = session.run(query, name=name, tenant_id=self.tenant_id)
                    count = result.single()["count"]
                    if count > 0:
                        valid_entities.add(entity)

            total_entities_in_file = len(valid_entities)

            if total_entities_in_kg > 0:
                overall_ratio = total_entities_in_file / total_entities_in_kg * 100
                return {
                    "状态": "成功",
                    "知识图谱中的实体总数": total_entities_in_kg,
                    "文件中的实体总数": total_entities_in_file,
                    "总体比例": f"{overall_ratio}%"
                }
            else:
                return {"状态": "错误", "消息": "知识图谱中没有实体进行比较。"}
        except FileNotFoundError:
            logging.error(f"未找到文件 {filename}。")
            return {"状态": "错误", "消息": f"未找到文件 {filename}。"}
        except ValueError as ve:
            logging.error(f"处理文件时发生错误: {ve}")
            return {"状态": "错误", "消息": f"处理文件时发生错误: {ve}"}
        except KeyError as ke:
            logging.error(f"访问数据时发生错误: {ke}")
            return {"状态": "错误", "消息": f"访问数据时发生错误: {ke}"}
        except Exception as e:
            logging.error(f"发生意外错误: {e}")
            return {"状态": "错误", "消息": f"发生意外错误: {e}"}
        finally:
            try:
                driver.close()
            except:
                pass

    def delete_tenant_data(self):
        try:
            # 删除具有特定 tenant_id 的所有关系
            self.graph.run("MATCH ()-[r]->() WHERE r.tenant_id = $tenant_id DELETE r", tenant_id=self.tenant_id)
            # 删除具有特定 tenant_id 的所有节点
            self.graph.run("MATCH (n) WHERE n.tenant_id = $tenant_id DELETE n", tenant_id=self.tenant_id)

            return {"状态": "成功", "消息": "租户数据已删除。"}
        except Exception as e:
            logging.error(f"删除租户数据时发生错误: {e}")
            return {"状态": "错误", "消息": f"删除租户数据时发生错误: {e}"}

    def export_graph_to_file(self, filename: str) -> dict:
        try:
            nodes = self.graph.run("MATCH (n) WHERE n.tenant_id = $tenant_id RETURN n", tenant_id=self.tenant_id)
            relationships = self.graph.run("MATCH ()-[r]->() WHERE r.tenant_id = $tenant_id RETURN r",
                                           tenant_id=self.tenant_id)

            data = {
                "nodes": [],
                "relationships": []
            }

            for node in nodes:
                n = node["n"]
                data["nodes"].append({
                    "id": n.identity,
                    "labels": list(n.labels),
                    "properties": dict(n)
                })

            for relationship in relationships:
                r = relationship["r"]
                data["relationships"].append({
                    "id": r.identity,
                    "type": type(r).__name__,
                    "start_node": r.start_node.identity,
                    "end_node": r.end_node.identity,
                    "properties": dict(r)
                })

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            return {"状态": "成功", "消息": f"数据已导出到 {filename}"}
        except Exception as e:
            logging.error(f"导出数据时发生错误: {e}")
            return {"状态": "错误", "消息": f"导出数据时发生错误: {e}"}

    def schedule_deletion(self, delay: int):
        def delete_data():
            logging.info(f"删除租户 {self.tenant_id} 的数据。")
            self.delete_tenant_data()

        timer = threading.Timer(delay, delete_data)
        timer.start()

    def use_graph(self, option: int, start_node_name: str = None, end_node_name: str = None, relation_name: str = None,
                  filename: str = None, export: bool = False) -> dict:
        if option == 1:
            result = self.find_all_paths(start_node_name, end_node_name)
        elif option == 2:
            result = self.find_shortest_path_weighted(start_node_name, end_node_name)
        elif option == 3:
            result = self.search_node_by_name(start_node_name)
        elif option == 4:
            result = self.search_relationship_by_name(relation_name)
        else:
            result = self.calculate_entity_ratio(filename)

        if export:
            export_result = self.export_graph_to_file(f"{self.tenant_id}_graph.json")
            logging.info(export_result)
            # 一天后删除数据（1天 * 24小时 * 60分钟 * 60秒）
            self.schedule_deletion(1 * 24 * 60 * 60)
        else:
            # 一周后删除数据（7天 * 24小时 * 60分钟 * 60秒）
            self.schedule_deletion(7 * 24 * 60 * 60)

        return result


if __name__ == "__main__":
    graph_manner = GraphManager()
    graph_manner.import_data(json_file="kg.json")

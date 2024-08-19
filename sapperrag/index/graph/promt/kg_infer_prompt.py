inference_capacity = """
Triple - A type triple refers to an instance RDF triple, which is linked to its entity type and relationship type using the symbol "-" .

Please help determine if the following triple is suitable for inference.
If the triple contains private domain information or insufficient background information, please output 'No'. Otherwise, please output 'Yes'.
Only output the content of the output in Example format, do not output "output:" or other irrelevant characters.

Example:
input: (Li Hua, is the son, ?)-(People, Relationship, People)
output: No
input: (Li Hua, age, ?)-(People, age, Number)

input:(Python Tuple, Feature, ?)-(Basic Concept, Feature, Fixed size)
output: Yes

Query:
input:{{masked_triple}}
output:
"""

kg_inference = """
Triple - A type triple refers to an instance RDF triple, which is linked to its entity type and relationship type using the symbol "-" .

Please reason and complete the obscured triple elements.
Please provide three reasonable reasoning results and ensure that these results have practical application value. 
Only output the content of the output in Example format, do not output "output:" or other irrelevant characters.

Example:
input: (Tuple, Feature, ?)-(Basic Concept, Feature, Fixed size)
output: (Tuple, Feature, Fixed number of elements)-(Basic Concept, Feature, Fixed size); (Tuple, Feature, Elements can be of different types)-(Basic Concept, Feature, Fixed size); (Tuple, Feature, Ordered elements)-(Basic Concept, Feature, Fixed size)

Query:
input:{{masked_triple}}
output:
"""

entity_attributes_infer = """
The attributes of the given entity are contained in parentheses connected to it, such as e1(attr1, attr2, attr3,...).
        
Please infer the attribute values corresponding to the given entity's attributes.
Pay attention to ensuring the accuracy and practicality of inference attribute values.
Only output the content of the output in Example format, do not output "output:" or other irrelevant characters.

Example:
input: 内存(容量, 类型, 频率, 电压, 时序, 访问速度)
output: 容量: 大; 类型: DDR4; 频率: 高; 电压: 低; 时序: 紧凑; 访问速度: 快

input: 水(溶解性, 沸点, 熔点, 密度, 极性, 比热容)
output: 溶解性: 高; 沸点: 100度(一个大气压下); 熔点: 0度(一个大气压下); 密度: 1g/cm3(4摄氏度时); 极性: 极性分子; 比热容: 4.18J/g·K

Query:
input:{{entity_with_attribute_keys}}
output:
"""

triples_source_inference = """
Generate the corresponding text in reverse based on triplets.
Pay attention to generating source information as rich as possible while maintaining its accuracy.
If accurate text cannot be provided, respond with "No"

Example:
Q:(学习, 是, 积累过程)
A:学习是一种积累的过程，通过不断地学习和实践，我们可以逐步积累知识和经验。正如老话所说，学习是没有尽头的，每一步的积累都会为未来打下坚实的基础。

Input:
{{inferred_triple}}
"""

entity_inference = """
Answer the question about entity knowledge.
Example:
Q: What is the primary simple information of the teacher?
A: The main job of teachers is to teach and educate students, and they are active in the field of technical education in various universities.
Q: What is the primary simple information of the student?
A: Students are the main body of the school, and their main task is to learn knowledge.

Input: What is the primary simple information of the {{entity}}?
"""

yes_no_judgement = """
Answer the question based on the knowledge about the entities.
Example:
Entities Knowledge:
The main job of teachers is to teach and educate students, and they are active in the field of technical education in various universities.
Students are the main body of the school, and their main task is to learn knowledge.
Q: Based on the knowledge above, do "teacher teach student"  is reasonable?
A: Yes.

Entities Knowledge:
The primary simple information about a country typically includes its geographical location, population size, capital city, official language(s), and currency.
Firefighters are emergency responders trained to combat and extinguish fires, rescue people and animals from dangerous situations, and provide medical assistance in emergencies. They often work for fire departments or emergency services agencies and undergo rigorous training to handle various types of emergencies.
Q: Based on the knowledge above, do "country eat firefighters" is reasonable?
A: No.

Input: 
Entities Knowledge:
{{domain_knowledge}}
Based on the knowledge above, do "{{directional_entity}} {{relation}} {{directed_entity}}" is reasonable?
"""

claim_validate = """
Determine whether the claim is correct based on the Knowledge of entities.
Example:
Entities Knowledge:
The main job of teachers is to teach and educate students, and they are active in the field of technical education in various universities.
Students are the main body of the school, and their main task is to learn knowledge.
Q: Based on the knowledge above, "teacher teach student"  is reasonable.
A: Correct.

Entities Knowledge:
The primary simple information about a country typically includes its geographical location, population size, capital city, official language(s), and currency.
Firefighters are emergency responders trained to combat and extinguish fires, rescue people and animals from dangerous situations, and provide medical assistance in emergencies. They often work for fire departments or emergency services agencies and undergo rigorous training to handle various types of emergencies.
Q: Based on the knowledge above, "country eat firefighters" is reasonable.
A: Incorrect.

Input: 
Entities Knowledge:
{{domain_knowledge}}
Based on the knowledge above, "{{directional_entity}} {{relation}} {{directed_entity}}" is reasonable.
"""

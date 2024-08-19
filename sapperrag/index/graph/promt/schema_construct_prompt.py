SCHEMA_CONSTRUCTOR = """
@Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should executing all instructions as needed"
架构提取器{
@Contextcontrol{
    Output must be in {{language}} form.
}
@Persona {
    @Description{
        You are responsible for extracting entities from the text and classify the entities and entity relationships.
    }
}
@Audience {
    @Description{
        People who need to extract knowledge architecture from data.
    }
}
@Instruction提取器 {
    @Commands Please extract useful entities for {{aim}},and analyze what entity category each entity belongs to. 
    @Command Infer what kind of relationship exists between entities based on the article.
    @Rules When extracting entities, focus on individuals that can exist independently, such as planets, oceans, islands, etc.
    @Rules The identified relationships between entities must be output in the form of triples.The first two elements of a triplet are entities, and the third element is entity relationship. 
    @Rules Entity relationships should be concise and not exceed ten words.The first entity acts on the second entity through a relationship.
    @Rules Ensure that each relationship is not a noun.
    @Rules Output the source text corresponding to each triplet.
    @Rules The entity category must be consistent with the language form of the text.
    {{suggestion}} 
    @Format{
        [Entity and Entity Category]: Entity1 (entity category1),Entity2 (entity category2)
        [Entity Relationship]: 
        ^^(Entity 1, Entity 2, Entity Relationship1): source text
        (Entity 3, Entity 4, Entity Relationship2): source text^^
    }
}
@Instruction实体分类器 {
    @Commands The content in the parentheses in the [Entity and Entity Categories] section of Instruction提取器 is all categories. Classify entities with the middle level of abstraction possible.
    @Commands Provide a definition for each entity category
    @Format{
        %%Entity Category 1, Entity Category 2, Entity Category 3%%
        ///Entity Category 1:the defininition of Entity Category 1 #
        Entity Category 2:the defininition of Entity Category 2 #
        Entity Category 3:the defininition of Entity Category 3///
    }			
}
@Instruction关系分类器
{
   There are some triples in the output of @Instruction提取器, and the format of the triples is (Entity 1, Entity 2, Relationship). 
   @Commands Extract the relationships in the triples you mentioned above (the third element of the triplet), classify entity relationships with the highest level of abstraction as far as possible.
   @Commands Provide a definition for each entity relationship category.
   @Rules Only output entity relationships, no need to provide examples for each type of entity relationship
   @Rules The relationship category is usually a verb phrase and cannot be a noun and no more than five words
   @Format{
        &&Entity Relationship Category 1, Entity Relationship Category 2, Entity Relationship Category 3&&
        $$Entity Category 1:the defininition of Entity Category 1 #
        Entity Category 2:the defininition of Entity Category 2 #
        Entity Category 3:the defininition of Entity Category 3$$
   }
}
You are now the 架构提取器 defined above, please complete the user interactions as required.
Please complete @SystemOutput {} as required.
text:{{ text }}
"""

TYPE_DEFINITION = """
Following is some type definition:
{{definition}}
{{oringinal_type_string}}
{{type_string}}
@Commands    Determine whether the new entity category is semantically similar to the original entity category. If the semantically similar according to the type definition, replace the new entity category with the original entity relationship category and output all final new entity categories
@Commands   Determine whether the new entity relationship category is semantically similar to the original entity relationship category. If the semantically similar, replace the new entity relationship category with the original entity relationship category and output all final new entity relationship categories
@Rules Do not output the analysis process, only output the final result.
@Format{
   entity categories: entity category1,entity category2,entity category3
   entity relationship categories: entity relationship category1,entity relationship category2,entity relationship category3
}
"""

ATTRIBUTES_INFER = """
{{Triplet}}
{{type}}
@Instruction 属性推断器{
    @Commands Infer the possible attributes of each entity category based on the text, and these attributes must match the entity category.
    List the corresponding attributes after each entity type and infer three attributes for each entity type.  
    @Rules Do not infer attributes for relationship categories.  
    @Rules Output must be in {{language}} form.
    @Rules Note that attributes are specific characteristics of entity types, and each attribute corresponding to that type of entity will have an attribute value.
    @Format{
        Entity Category 1 [Attribute 1, Attribute 2, Attribute 3]
        Entity Category 2 [Attribute 4, Attribute 5, Attribute 6]
    }   @example{
            @Input{
                scholar
            }
            @Output{
                scholar [achievement, works, age]
            }
        }
}
@Instruction 整合器{
        @Commands There are some triples above.The format of the triples is (Entity 1, Entity 2, Entity Relationship).Determine which entity category Entity 1 and Entity 2 belong to, and determine which Entity Relationship category entity relationship belongs to.
        @Commands Replace the original triplet with the corresponding type triplet.
        @Format{  
            (Entity 1, Entity 2,Entity relationship1): &(Category to which Entity 1 belongs [attributes corresponding to this category, attributes corresponding to this category] # Category to which Entity 2 belongs [attributes corresponding to this category, attributes corresponding to this category] # Entity relationship category to which entity relationship1 belongs)&
            (Entity 3, Entity 4,Entity relationship2): &(Category to which Entity 3 belongs [attributes corresponding to this category, attributes corresponding to this category] # Category to which Entity 4 belongs [attributes corresponding to this category, attributes corresponding to this category] # Entity relationship category to which entity relationship2 belongs)&
        }
    }
"""

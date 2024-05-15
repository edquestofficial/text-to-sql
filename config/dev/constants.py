DATA_BASE_PATH = "data"
ALL_DATA = "/gleif_lei_all.csv"
REL_DATA = "/gleif_lei_rel.csv"
TABLE_SCHEMA_PATH = "table_schema/"
UI_TITLE = "GLeif Generative Search"
LLM_MODEL="gpt-3.5-turbo"

TABLE_SCHEMA_PROMPT = """\
Give me a summary of the table with the following json format.

- Table name must be unique to the table and describe it while being concise.
- Do not output a Generic table name (e.g. table, my_table)
- Table name should not contains any space in it. If it contains space, replace it with underscore.

Do not make table name one of the following: {exclude_table_name_list}

Table: {table_str}
Summary:
"""

TABLE_SUMMARY = """Table containing relationship details between nodes, including start and end node IDs, 
relationship type, status, periods, qualifiers, quantifiers, registration information, and validation sources.
Following is the Foreign key ralationship
- FOREIGN KEY Relationship_StartNode_NodeID REFERENCES EntityInformation(LEI),
- FOREIGN KEY Relationship_EndNode_NodeID REFERENCES EntityInformation(LEI).

Relationship_RelationshipType defines the relationship between Relationship_StartNode_NodeID and Relationship_EndNode_NodeID.
Following are the avilable relations type:
- 'IS_ULTIMATELY_CONSOLIDATED_BY' defines ultimate child,
- `IS_DIRECTLY_CONSOLIDATED_BY` defines direct child
- `IS_FUND-MANAGED_BY` defines fund managed by
"""

TEXT_TO_SQL_PROMPT = """
Given an input question, construct a syntactically correct {dialect} SQL query to run, then look at the results of the query and return a comprehensive and detailed answer. Ensure that you:
- Select only the relevant columns needed to answer the question.
- Use correct column and table names as provided in the schema description. Avoid querying for columns that do not exist.
- Qualify column names with the table name when necessary, especially when performing joins.
- Use aggregate functions appropriately and include performance optimizations such as WHERE clauses and indices.
- Add additional related information for the user.
- Use background & definitions provided for more detailed answer. Follow the instructions.
- Avoid hallucination. If you can't find an answer, say I'm not sure.


Special Instructions:
- Treat "province" and "region" as interchangeable terms in your queries.
- Default to using averages for aggregation if not specified by the user question.
- Recognize both short and full forms of Canadian provinces.
- If the question involves a KPI not listed below, inform the user by showing the list of available KPIs.
- If the requested date range is not available in the database, inform the user that data is not available for that time period.
- Use bold and large fonts to highlight keywords in your answer.
- If the date is not available, your answer will be: Data is not available for the requested date range. Please modify your query to include a valid date range.
- Calculate date ranges dynamically based on the current date or specific dates mentioned in user queries. Use relative time expressions such as "last month" or "past year".
- If a query fails to execute, suggest debugging tips or provide alternative queries. Ensure to handle common SQL errors gracefully."
- If the query is ambiguous, generate a clarifying question to better understand the user's intent or request additional necessary parameters.
- Use indexed columns for joins and WHERE clauses to speed up query execution. Use `EXPLAIN` plans for complex queries to ensure optimal performance.

Following fields store data in string format. so always convert it first to datatime before doing any comparision or any operation
- Entity_EntityCreationDate
- Registration_InitialRegistrationDate
- Registration_LastUpdateDate
- Registration_NextRenewalDate

Additional Instructions:
- Encourage users to provide specific date ranges or intervals for more accurate results.
- Mention the importance of specifying provinces or regions for targeted analysis.
- Provide examples of common SQL syntax errors and how to correct them.
- Offer guidance on interpreting query results, including outliers or unexpected patterns.
- Emphasize the significance of data integrity and potential implications of incomplete or inaccurate data.

You are required to use the following format, each taking one line:
Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Use these real examples for complex queries:

Example 1:
Question: Give me the direct children for <entity name>?
SQLQuery: SELECT Entity_LegalName AS direct_child_name
FROM EntityInformation ent
JOIN Relationship_StartNode_NodeID rel ON ent.LEI = rel.Relationship_StartNode_NodeID
WHERE rel.Relationship_RelationshipType = 'IS_DIRECTLY_CONSOLIDATED_BY'
AND rel.Relationship_EndNode_NodeID = (SELECT LEI FROM EntityInformation WHERE Entity_LegalName = 'A');

SQLResult:
direct_child_name         | avg_volte_accessibility
--------------------------
quebec | 80.98
Answer: Direct child of <entity_name> are as <direct_child_name>

Question: Give me the direct children for <LEI>?
SQLQuery: SELECT Entity_LegalName AS direct_child_name
FROM EntityInformation ent
JOIN Relationship_StartNode_NodeID rel ON ent.LEI = rel.Relationship_StartNode_NodeID
WHERE rel.Relationship_RelationshipType = 'IS_DIRECTLY_CONSOLIDATED_BY'
AND rel.Relationship_EndNode_NodeID = LEI;

SQLResult:
direct_child_name         | avg_volte_accessibility
--------------------------
quebec | 80.98
Answer: Direct child of <entity_name> are as <direct_child_name>

Question: Give me the ultimate child for <entity name>?
SQLQuery: SELECT Entity_LegalName AS ultimate_child_name
FROM EntityInformation ent
JOIN Relationship_StartNode_NodeID rel ON ent.LEI = rel.Relationship_StartNode_NodeID
WHERE rel.Relationship_RelationshipType = 'IS_ULTIMATELY_CONSOLIDATED_BY'
AND rel.Relationship_EndNode_NodeID = (SELECT LEI FROM EntityInformation WHERE Entity_LegalName = 'A');

SQLResult:
ultimate_child_name         | avg_volte_accessibility
--------------------------
quebec | 80.98
Answer: Direct child of <entity_name> are as <ultimate_child_name>

Question: Give me the ultimate children for <LEI>?
SQLQuery: SELECT Entity_LegalName AS ultimate_child_name
FROM EntityInformation ent
JOIN Relationship_StartNode_NodeID rel ON ent.LEI = rel.Relationship_StartNode_NodeID
WHERE rel.Relationship_RelationshipType = 'IS_ULTIMATELY_CONSOLIDATED_BY'
AND rel.Relationship_EndNode_NodeID = LEI;

SQLResult:
ultimate_child_name         | avg_volte_accessibility
--------------------------
quebec | 80.98
Answer: Direct child of <entity_name> are as <ultimate_child_name>

Only use tables listed below.
{schema}

Question: {query_str}
SQLQuery:
"""
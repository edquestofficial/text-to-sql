from src.preprocess import preprocess
from src.llama_program import create_program
from src.get_table_info import get_tableinfo_with_index
from src.sql import create_table_from_dataframe
from src.query_pipeline import create_query_pipeline, prepare_query_pipeline
from src.sql_obj_retriver import get_obj_retriver
# from src.logging import start_log

from config.dev.constants import TABLE_SUMMARY, TABLE_SCHEMA_PATH, TEXT_TO_SQL_PROMPT,ALL_DATA, REL_DATA, DATA_BASE_PATH, UI_TITLE
from config.dev.secrets import LLM_KEY
from config.dev.query import QUERIES

import json
import random
import importlib
import os
import sys
import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
from sqlalchemy.orm import declarative_base, sessionmaker
# import phoenix as px
import llama_index.core
import gradio as gr
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.openai import OpenAI
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.llms import ChatResponse
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
)

Base = declarative_base()

def parse_response_to_sql(response: ChatResponse) -> str:
    """Parse response to SQL."""
    response = response.message.content
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        # TODO: move to removeprefix after Python 3.9+
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:") :]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    return response.strip().strip("```").strip()

def get_table_context_str(table_schema_objs: List[SQLTableSchema]):
    """Get table context string."""
    context_strs = []
    for table_schema_obj in table_schema_objs:
        table_info = sql_database.get_single_table_info(
            table_schema_obj.table_name
        )
        if table_schema_obj.context_str:
            table_opt_context = " The table description is: "
            table_opt_context += table_schema_obj.context_str
            table_info += table_opt_context

        context_strs.append(table_info)
    return "\n\n".join(context_strs)

def run_query(message, history):
    print(f"query coming from gradio.......", message)
    response = qp.run(
        query=message
    )
    return str(response)

if __name__ == "__main__":
    # Read Data from csv and preprocess data
    df_lei = preprocess.get_processed_data(f"{DATA_BASE_PATH}{ALL_DATA}")
    df_rel = preprocess.get_processed_data(f"{DATA_BASE_PATH}{REL_DATA}")
    
    # List of dataframes
    dfs = [df_lei.head(2), df_rel.head(2)] # for testing end-to-end
    # dfs = [df_lei, df_rel]
    
    # Set openAI key in enviorment variable
    os.environ["OPENAI_API_KEY"] = LLM_KEY
    
    # create program instance of Llama index
    program = create_program()
    
    # initialize blank variables
    table_names = set()
    table_infos = []

    # Iterate dataframe list
    for idx, df in enumerate(dfs):
        table_info = get_tableinfo_with_index(idx)
        print("table_info -- ", table_info)
        if table_info:
            table_infos.append(table_info)
        else:
            while True:
                df_str = df.head(10).to_csv()
                table_info = program(
                    table_str = df_str,
                    exclude_table_name_list = str(list(table_names))
                )
                print("table_info -->> ", table_info)
                table_name = table_info.table_name
                print(f"Processed table: {table_name}")
                if table_name not in table_names:
                    #sanitize table name
                    table_name = table_name.replace(" ", "_")
                    print(":::::table_name:::::",table_name)
                    table_names.add(table_name)
                    break
                else:
                    print(f"Table name {table_name} already exist, trying again.")
                    pass
            table_info.table_name = table_info.table_name.replace(" ", "_")
            print("table_info -->> ", table_info)
            out_file = f"{TABLE_SCHEMA_PATH}/{idx}_{table_name}.json"
            #create .json file that contains table_name and table_summary
            json.dump(table_info.dict(), open(out_file, "w"))
        table_infos.append(table_info)

    # update table info summary
    table_infos[1].table_summary = TABLE_SUMMARY
    engine = create_engine("sqlite:///sql_db/gleif.db")
    metadata_obj = MetaData()
    for idx, df in enumerate(dfs):
        tableinfo = get_tableinfo_with_index(idx)
        print(f"Creating table: {tableinfo.table_name}")
        create_table_from_dataframe(df, tableinfo.table_name, engine, metadata_obj)

    # setup Arize Phoenix for logging/observability
    # start_log()
    
    #Create SQL Database engine
    sql_database = SQLDatabase(engine)
    obj_retriever = get_obj_retriver(sql_database, table_infos)
    
    # SQL Retriver
    sql_retriever = SQLRetriever(sql_database)
    table_parser_component = FnComponent(fn=get_table_context_str)
    
    #SQL Table Parser
    sql_parser_component = FnComponent(fn=parse_response_to_sql)

    text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
        dialect=engine.dialect.name
    )
    # Reference: https://github.com/run-llama/llama_index/discussions/13098
    text2sql_prompt.template = TEXT_TO_SQL_PROMPT
    # print(text2sql_prompt.template)
    
    # Response synthesis prompt
    response_synthesis_prompt_str = (
        "Given an input question, synthesize a response from the query results.\n"
        "Query: {query_str}\n"
        "SQL: {sql_query}\n"
        "SQL Response: {context_str}\n"
        "Response: "
    )
    response_synthesis_prompt = PromptTemplate(
        response_synthesis_prompt_str,
    )
    
    # Create Query Pipeline
    qp = create_query_pipeline(obj_retriever, table_parser_component, text2sql_prompt, sql_parser_component, sql_retriever, response_synthesis_prompt)
    
    # Prepare query pipeline
    qp = prepare_query_pipeline(qp)
    
    # pick query from constants
    query = random.choice(QUERIES) # What is the legal address of <entity name>?
    print(f"Query1 : {query}")
    response = qp.run(
        query=query
    )
    print(f"response: {str(response)}")
    # Run query and print its response
    # print(run_query(query, query))
    print("Query ran sucessfully........")

    # Start UI
    ui = gr.ChatInterface(fn=run_query, examples=QUERIES, title=UI_TITLE)
    ui.launch(debug=True, share=True)

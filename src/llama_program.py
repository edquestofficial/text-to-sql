from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.openai import OpenAI

from config.dev.constants import TABLE_SCHEMA_PROMPT
from src.table_info import TableInfo


def create_program():
    return LLMTextCompletionProgram.from_defaults(
        output_cls = TableInfo,
        llm = OpenAI(model="gpt-3.5-turbo"),
        prompt_template_str = TABLE_SCHEMA_PROMPT
    )
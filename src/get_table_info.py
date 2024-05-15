import json
from pathlib import Path
from src.table_info import TableInfo
from config.dev.constants import TABLE_SCHEMA_PATH

def get_tableinfo_with_index(idx: int) -> str:
  results_gen = Path(TABLE_SCHEMA_PATH).glob(f"{idx}_*")
  results_list = list(results_gen)
  if len(results_list) == 0:
    return None
  elif len(results_list) == 1:
    path = results_list[0]
    return TableInfo.parse_file(path)
  else:
    raise ValueError(
        f"More than one file matching index: {list(results_gen)}"
    )
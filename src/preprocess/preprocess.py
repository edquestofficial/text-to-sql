import pandas as pd

def get_processed_data(file):
    return synthesize_col_name(pd.read_csv(file))

def synthesize_col_name(df):
  columns = df.columns
  updated_columns = []
  for col in columns:
    new_col = col.replace(".", "_")
    updated_columns.append(new_col)
  df.columns = updated_columns
  return df
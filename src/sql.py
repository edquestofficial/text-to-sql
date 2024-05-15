import re
import pandas as pd

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)

# Function to create a table from a DataFrame using SQLAlchemy
def create_table_from_dataframe(
    df: pd.DataFrame,
    table_name: str,
    engine,
    metadata_obj):

  # Dynamically create columns based on DataFrame columns and data types
  columns = [
      Column(col, String if dtype == "Object" else Integer)
      for col, dtype in zip(df.columns, df.dtypes)
  ]

  # Create a Table with the defined columns
  table = Table(table_name, metadata_obj, *columns)

  # Create the table in database
  metadata_obj.create_all(engine)

  # Insert data from DataFrame into the table
  with engine.connect() as conn:
    for _, row in df.iterrows():
      insert_stmt = table.insert().values(**row.to_dict())
      print(insert_stmt)
      conn.execute(insert_stmt)
    conn.commit()
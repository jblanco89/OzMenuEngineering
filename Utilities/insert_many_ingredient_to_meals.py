import pandas as pd
import duckdb as dk

conn = dk.connect(database='./DB/engineMenu_v43.db')
cursor = conn.cursor()

with open('./SQL/insert_meals_ingredients_data.sql','r') as sql_file:
    query_insert = sql_file.read()

cursor.execute(query=query_insert)
cursor.commit()
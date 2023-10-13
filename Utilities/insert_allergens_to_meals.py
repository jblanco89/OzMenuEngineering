import pandas as pd
import duckdb as dk

conn = dk.connect(database='./DB/engineMenu_v43.db')
cursor = conn.cursor()

with open('./SQL/insert_allergens_to_meals.sql','r') as sql_file:
    query = sql_file.read()

cursor.execute(query=query)
cursor.commit()
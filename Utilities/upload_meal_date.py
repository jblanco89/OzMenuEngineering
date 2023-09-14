from datetime import date
import time
import duckdb as dk

# Establish a connection to your DuckDB database
conn = dk.connect(database='./DB/engineMenu_v43.db')

date = date.today()

update_query = "UPDATE platos SET Fecha = ?"

conn.execute(update_query, (date,))

conn.commit()

# Close the connection
conn.close()

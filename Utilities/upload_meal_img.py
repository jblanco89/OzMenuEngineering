import duckdb
import base64

# Establish a connection to your DuckDB database
conn = duckdb.connect(database='./DB/engineMenu_v43.db')

# Read the image file as binary data
with open('./img/oz_logo.jpg', 'rb') as image_file:
    image_data = image_file.read()

image_data = base64.b64encode(image_data).decode('utf-8')    

# Prepare the UPDATE query to set the same image for all rows
update_query = "UPDATE platos SET foto_plato = ?"

# Execute the query, passing the image data as a parameter
conn.execute(update_query, (image_data,))

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

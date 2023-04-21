import duckdb as dk

class ConnectionDB:
    def __init__(self, database):
        self.con = dk.connect(database=database)

    def execute(self, query):
        return self.con.execute(query)
    
    def cursor(self):
       return self.con.cursor()

    def close(self):
        self.con.close()
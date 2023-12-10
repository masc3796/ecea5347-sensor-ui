import sqlite3
conn = sqlite3.connect('sensor_data.db')
c = conn.cursor()

#Create the Videos Table
data_table = """CREATE TABLE 
'data' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'timestamp' TEXT,
    'temperature' REAL,
    'humidity' REAL
    )
"""

c.execute(data_table) 
conn.commit()
conn.close()

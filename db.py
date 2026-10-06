from dotenv import load_dotenv
import os
import mysql.connector
load_dotenv()
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("dbpass"),
    database="mydb"
)
cursor = con.cursor()
print("")

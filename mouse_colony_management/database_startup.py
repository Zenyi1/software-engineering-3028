import mysql.connector
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Load environment variables from a .env file

dataBase = mysql.connector.connect(

    host="localhost",
    user="root",
    passwd="Gonzaloescolar1!",

)

cursorObject = dataBase.cursor()

try:
    cursorObject.execute("CREATE DATABASE mouse_colony_db")
    print("Database set successfully")
except:
    print("Error creating database")
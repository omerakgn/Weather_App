import sqlite3
import main
from main import WeatherApp

def Sql_connect():
   database = sqlite3.connect("database.db")
   cursor = database.cursor()

   create_table = "CREATE TABLE IF NOT EXISTS weather(city_name TEXT ,main_weather TEXT,temperature INT,humidity TEXT,wind_speed INT,time INT)"

   cursor.execute(create_table)


   database.close()







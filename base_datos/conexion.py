
import mysql.connector
from mysql.connector import Error


DB_HOST = "localhost"                       
DB_USER = "root"            
DB_PASSWORD = "ISAAC030313"     
DB_NAME = "gogym"            
                           
def obtener_conexion():
   
    try:
       
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        
        return conexion

    except Error as e:
       
        print(f"Error al conectar a MySQL: {e}")

       
        return None
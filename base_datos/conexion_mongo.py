"""
Conexion a MongoDB para la base de datos gogym_mongo.

Mismo principio que base_datos/conexion.py (Responsabilidad Unica /
Inversion de Dependencias): este es el UNICO archivo de todo el
programa que sabe como conectarse a MongoDB. Los modelos que usen
Mongo (por ejemplo notificacion_modelo.py) nunca deben importar
pymongo directamente para conectarse; llaman a obtener_bd_mongo() de
aqui.

Por que es una base de datos APARTE de MySQL: MongoDB es un motor
completamente distinto, no "vive dentro" de MySQL ni se relaciona con
el con llaves foraneas. Es una segunda base de datos independiente,
para guardar cosas que no necesitan la estructura rigida de tablas
(en este proyecto: la bitacora de actividad reciente de los alumnos).
"""
from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"
MONGO_DB_NOMBRE = "gogym_mongo"

_cliente = None


def obtener_bd_mongo():
    """
    Devuelve la base de datos de Mongo (gogym_mongo) ya lista para
    usarse. Si no se puede conectar (por ejemplo, MongoDB no esta
    corriendo), devuelve None, para que quien la use pueda revisar
    ese caso sin que el programa se caiga.
    """
    global _cliente
    try:
        if _cliente is None:
            _cliente = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
            _cliente.admin.command("ping")

        return _cliente[MONGO_DB_NOMBRE]
    except Exception as e:
        print("Error al conectar a MongoDB:", e)
        _cliente = None
        return None
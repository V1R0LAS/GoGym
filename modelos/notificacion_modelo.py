from abc import ABC, abstractmethod
from datetime import datetime
from base_datos.conexion_mongo import obtener_bd_mongo


class RepositorioNotificaciones(ABC):
    

    @abstractmethod
    def guardar(self, id_profesional, id_alumno, nombre_alumno, tipo, texto, datos_extra=None):
      
        pass

    @abstractmethod
    def obtener_por_profesional(self, id_profesional, limite=5):
     
        pass

class RepositorioNotificacionesMongo(RepositorioNotificaciones):
    def guardar(self, id_profesional, id_alumno, nombre_alumno, tipo, texto, datos_extra=None):
        bd = obtener_bd_mongo()
        if bd is None:
            return False

        documento = {
            "id_profesional": id_profesional,
            "id_alumno": id_alumno,
            "nombre_alumno": nombre_alumno,
            "tipo": tipo,
            "texto": texto,
            "fecha": datetime.now(),
        }
        if datos_extra:
            documento.update(datos_extra)

        try:
            bd.notificaciones.insert_one(documento)
            return True
        except Exception as e:
            print("Error al guardar notificacion en Mongo:", e)
            return False

    def obtener_por_profesional(self, id_profesional, limite=5):
        bd = obtener_bd_mongo()
        if bd is None:
            return []

        try:
            cursor = bd.notificaciones.find(
                {"id_profesional": id_profesional}
            ).sort("fecha", -1).limit(limite)
            return list(cursor)
        except Exception as e:
            print("Error al leer notificaciones de Mongo:", e)
            return []


_repositorio = RepositorioNotificacionesMongo()
def registrar_notificacion(id_profesional, id_alumno, nombre_alumno, tipo, texto, datos_extra=None):
    return _repositorio.guardar(id_profesional, id_alumno, nombre_alumno, tipo, texto, datos_extra)


def obtener_notificaciones_profesional(id_profesional, limite=5):
    return _repositorio.obtener_por_profesional(id_profesional, limite)

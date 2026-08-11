"""
Persistencia de la sesion activa.

Guarda en un archivo de texto (JSON) quien inicio sesion la ultima
vez, para que la app no pida iniciar sesion de nuevo cada vez que se
abre el programa. Solo se olvida cuando el usuario da clic en
"Cerrar Sesion" explicitamente.

Responsabilidad Unica: este archivo SOLO lee/escribe ese archivo en
disco. No sabe nada de MySQL ni de la interfaz; validar si la cuenta
sigue activa es trabajo de usuario_modelo.py.
"""
import os

# "json" es una libreria de la libreria estandar de Python para
# convertir entre 2 formas de representar datos:
#   - Un diccionario de Python "en memoria" (ej. {"rol": "Alumno"})
#   - Un archivo de TEXTO en formato JSON (ej. {"rol": "Alumno"} pero
#     como texto plano guardado en disco).
# JSON (JavaScript Object Notation) es un formato universal que
# entienden practicamente todos los lenguajes de programacion, muy
# usado para guardar datos estructurados simples en archivos.
import json

# Carpeta raiz del proyecto (2 niveles arriba: utilidades/ -> gogym_app/).
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta completa donde va a vivir el archivo de sesion: justo en la
# raiz del proyecto (junto a principal.py), con el nombre
# "sesion_activa.json".
RUTA_SESION = os.path.join(CARPETA_BASE, "sesion_activa.json")


def guardar_sesion(usuario):
    """Guarda los datos minimos del usuario que inicio sesion
    (id_usuario, correo, rol), para poder recuperarlos despues."""
    try:
        # "with open(archivo, 'w', encoding='utf-8') as archivo:" abre
        # (o CREA, si no existe) el archivo en modo ESCRITURA ("w" de
        # "write"; si el archivo ya existia con contenido viejo, se
        # SOBREESCRIBE por completo). El "with" garantiza que el
        # archivo se cierre automaticamente al terminar el bloque,
        # aunque ocurra un error adentro (es el equivalente, para
        # archivos, del patron try/finally que ya vimos con las
        # conexiones a MySQL).
        with open(RUTA_SESION, "w", encoding="utf-8") as archivo:
            # "json.dump(diccionario, archivo)" toma un diccionario de
            # Python y lo escribe DIRECTO al archivo, ya convertido al
            # formato de texto JSON. Aqui se guarda un diccionario
            # "a mano", extrayendo SOLO 3 llaves del diccionario
            # "usuario" completo (que podria traer mas datos, como la
            # contrasenia, que NO queremos guardar en este archivo por
            # seguridad).
            json.dump({
                "id_usuario": usuario["id_usuario"],
                "correo": usuario["correo"],
                "rol": usuario["rol"],
            }, archivo)
    except Exception as e:
        # Si por algun motivo no se pudo escribir el archivo (por
        # ejemplo, la carpeta del proyecto esta en modo "solo lectura"
        # en esa computadora), se atrapa el error para que la app NO
        # se caiga solo por no poder guardar la sesion — el usuario
        # simplemente tendria que volver a iniciar sesion la proxima
        # vez, pero el programa seguiria funcionando con normalidad.
        print("No se pudo guardar la sesion:", e)


def obtener_sesion():
    """Lee la sesion guardada, si existe. Devuelve None si nunca se
    guardo ninguna, o si el archivo esta corrupto/incompleto."""
    # Antes de intentar abrir el archivo, se revisa si de verdad
    # existe. Si nunca se ha guardado ninguna sesion (por ejemplo, la
    # primera vez que se usa la app en una computadora nueva), este
    # archivo simplemente no existira todavia.
    if not os.path.exists(RUTA_SESION):
        return None

    try:
        # Se abre el archivo en modo LECTURA ("r" de "read").
        with open(RUTA_SESION, "r", encoding="utf-8") as archivo:
            # "json.load(archivo)" hace lo contrario de json.dump():
            # LEE el texto en formato JSON del archivo y lo convierte
            # de vuelta a un diccionario normal de Python.
            datos = json.load(archivo)

        # Se revisa que el diccionario leido de verdad tenga las 2
        # llaves minimas que se necesitan ("id_usuario" y "rol"). Esto
        # protege contra el caso de que alguien edite el archivo a
        # mano y lo deje incompleto, o que una version futura del
        # programa cambiara el formato guardado.
        if "id_usuario" in datos and "rol" in datos:
            return datos
        return None
    except Exception as e:
        # Si el archivo existe pero su contenido no es JSON valido
        # (por ejemplo, se corrompio, o alguien escribio texto
        # cualquiera adentro a mano), json.load() lanzaria un error;
        # se atrapa aqui para que la app simplemente trate esa sesion
        # como "no valida" en vez de tronar.
        print("No se pudo leer la sesion guardada:", e)
        return None


def borrar_sesion():
    """Borra la sesion guardada. Se usa al dar clic en 'Cerrar Sesion'."""
    # Se revisa primero que el archivo exista, para no intentar borrar
    # algo que ya no esta (eso lanzaria un error innecesario).
    if os.path.exists(RUTA_SESION):
        try:
            # "os.remove(ruta)" borra el archivo del disco por
            # completo.
            os.remove(RUTA_SESION)
        except Exception as e:
            print("No se pudo borrar la sesion guardada:", e)
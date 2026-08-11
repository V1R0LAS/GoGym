"""
Consultas relacionadas con el ALUMNO: su dashboard (Inicio), sus rutinas
y sus metricas (mediciones de peso/altura).
"""

# "date" y "timedelta" son 2 herramientas de la libreria estandar de
# Python para trabajar con fechas:
#   - date.today() devuelve la fecha de HOY.
#   - timedelta(days=1) representa "un dia de diferencia", y se puede
#     RESTAR a una fecha para obtener el dia anterior.
from datetime import date, timedelta
from base_datos.conexion import obtener_conexion
from modelos.notificacion_modelo import registrar_notificacion


# ---------------------------------------------------------------------
# INICIO (dashboard)
# ---------------------------------------------------------------------

def obtener_resumen_dashboard(id_alumno):
    """Junta los 3 datos de arriba en Inicio: rutinas completadas este
    mes, peso actual y racha de dias."""
    conexion = obtener_conexion()
    if conexion is None:
        # Si no hay conexion, devolvemos un diccionario con ceros en
        # vez de None: asi, la vista puede seguir haciendo
        # resumen["rutinas_mes"] sin que truene por intentar leer una
        # llave de un objeto que no existe.
        return {"rutinas_mes": 0, "peso_actual": 0, "racha_dias": 0}

    # "dictionary=True" le dice al cursor que cada fila que regrese
    # MySQL se entregue como un diccionario (ej. {"total": 5}) en vez
    # de una tupla posicional (ej. (5,)). Asi se puede escribir
    # fila["total"] en vez de tener que recordar que la columna estaba
    # en la posicion 0.
    cursor = conexion.cursor(dictionary=True)

    # Rutinas completadas este mes.
    # MONTH(...) y YEAR(...) son FUNCIONES DE MYSQL (no de Python) que
    # extraen el mes/anio de una fecha. CURDATE() es otra funcion de
    # MySQL que da la fecha de hoy segun el SERVIDOR de base de datos.
    # Esta consulta cuenta cuantas rutinas "Realizada" tiene el alumno
    # cuyo mes y anio coinciden con el mes y anio actuales.
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM rutina r
        JOIN estado_realizacion e ON e.id_estado_realizacion = r.id_estado_realizacion
        WHERE r.id_alumno = %s
          AND e.tipo_estado = 'Realizada'
          AND MONTH(r.fecha_inicio) = MONTH(CURDATE())
          AND YEAR(r.fecha_inicio) = YEAR(CURDATE())
        """,
        (id_alumno,),
    )
    # cursor.fetchone() trae SOLO la primera fila del resultado (aqui
    # solo hay una, porque COUNT(*) siempre regresa un unico numero).
    rutinas_mes = cursor.fetchone()["total"]

    # Peso actual: la ultima medicion registrada.
    # "ORDER BY fecha DESC" ordena de la fecha mas reciente a la mas
    # vieja, y "LIMIT 1" se queda solo con la primera fila de ese
    # orden (osea, la medicion mas reciente).
    cursor.execute(
        "SELECT peso FROM medicion WHERE id_alumno = %s ORDER BY fecha DESC LIMIT 1",
        (id_alumno,),
    )
    fila_peso = cursor.fetchone()
    # Esta linea es un "operador ternario": es una forma corta de
    # escribir un if/else en una sola linea. Se lee: "si fila_peso
    # existe (no es None), usa float(fila_peso['peso']); si no, usa 0".
    # Se necesita convertir a float() porque MySQL regresa los
    # DECIMAL como un tipo especial de Python (Decimal), y es mas facil
    # trabajar con el peso como un numero normal.
    peso_actual = float(fila_peso["peso"]) if fila_peso else 0

    cursor.close()
    conexion.close()

    return {
        "rutinas_mes": rutinas_mes,
        "peso_actual": peso_actual,
        # Aqui se llama a OTRA funcion de este mismo archivo (definida
        # justo abajo) para calcular la racha de dias seguidos.
        "racha_dias": _calcular_racha_dias(id_alumno),
    }


def _calcular_racha_dias(id_alumno):
    """Cuenta cuantos dias seguidos (desde hoy hacia atras) el alumno
    tiene al menos una rutina 'Realizada'. Se detiene en el primer dia
    sin rutina realizada."""
    # El guion bajo al inicio del nombre ("_calcular_racha_dias") es una
    # CONVENCION de Python: le dice a quien lea el codigo "esta funcion
    # es de USO INTERNO de este archivo, no deberia llamarse desde
    # afuera" (aunque Python no lo prohibe de verdad, es solo una
    # senial para otros programadores).
    conexion = obtener_conexion()
    if conexion is None:
        return 0

    cursor = conexion.cursor(dictionary=True)
    # "SELECT DISTINCT" trae cada fecha SOLO UNA VEZ, aunque el alumno
    # tenga varias rutinas realizadas el mismo dia (por ejemplo, si en
    # el pasado se guardaron 2 antes de nuestro arreglo de "una rutina
    # por dia"). Sin DISTINCT, una misma fecha podria aparecer 2 veces.
    cursor.execute(
        """
        SELECT DISTINCT r.fecha_inicio AS fecha
        FROM rutina r
        JOIN estado_realizacion e ON e.id_estado_realizacion = r.id_estado_realizacion
        WHERE r.id_alumno = %s AND e.tipo_estado = 'Realizada'
        """,
        (id_alumno,),
    )
    # Esto es una "comprension de conjunto" (set comprehension): en
    # una sola linea, arma un CONJUNTO (un tipo de coleccion en Python
    # que no permite valores repetidos y es MUY rapido para preguntar
    # "esta esta fecha adentro?") con todas las fechas que trajo la
    # consulta. Es como decir: "por cada fila en el resultado, agarra
    # su columna 'fecha' y ponla en el conjunto".
    fechas_realizadas = {fila["fecha"] for fila in cursor.fetchall()}
    cursor.close()
    conexion.close()

    # Ahora contamos la racha "hacia atras" empezando desde hoy:
    racha = 0
    dia = date.today()
    # Este "while" se repite MIENTRAS la variable "dia" este dentro del
    # conjunto de fechas realizadas. En cuanto encuentre un dia que NO
    # esta en el conjunto (osea, un dia sin rutina realizada), el
    # ciclo se detiene automaticamente.
    while dia in fechas_realizadas:
        racha += 1
        # "dia -= timedelta(days=1)" le resta un dia a la fecha actual,
        # para revisar el dia anterior en la siguiente vuelta del ciclo.
        dia -= timedelta(days=1)
    return racha


def obtener_proximas_rutinas(id_alumno, limite=3):
    """Trae las siguientes rutinas pendientes (no realizadas), para la
    seccion 'Proximas Rutinas' de Inicio."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT r.nombre_rutina, r.fecha_inicio
        FROM rutina r
        JOIN estado_realizacion e ON e.id_estado_realizacion = r.id_estado_realizacion
        WHERE r.id_alumno = %s AND e.tipo_estado = 'No realizada'
        ORDER BY r.fecha_inicio ASC
        LIMIT %s
        """,
        (id_alumno, limite),
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


def obtener_progreso_peso(id_alumno):
    """Trae todas las mediciones (fecha, peso) ordenadas por fecha,
    para la grafica de progreso de peso."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT fecha, peso FROM medicion WHERE id_alumno = %s ORDER BY fecha ASC",
        (id_alumno,),
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


# ---------------------------------------------------------------------
# MIS RUTINAS
# ---------------------------------------------------------------------

def obtener_rutina_pendiente(id_alumno, nombre_tipo_entrenamiento):
    """Busca la rutina de HOY (fecha_inicio = fecha real de hoy) del
    alumno para el tipo de entrenamiento indicado ('Casa' o
    'Gimnasio'), con sus ejercicios. Devuelve None si no tiene ninguna
    rutina asignada para hoy en ese lugar.

    Se filtra por CURDATE() (el dia real) porque el mockup la llama
    'RUTINA DE HOY': un alumno puede tener una rutina de Casa Y otra de
    Gimnasio el mismo dia (para elegir donde entrenar), pero cada una
    solo debe aparecer el dia exacto para el que fue asignada, no
    quedarse mostrandose para siempre solo por estar pendiente."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT r.id_rutina, r.nombre_rutina, r.fecha_inicio
        FROM rutina r
        JOIN estado_realizacion e ON e.id_estado_realizacion = r.id_estado_realizacion
        JOIN tipo_entrenamiento t ON t.id_tipo_entrenamiento = r.id_tipo_entrenamiento
        WHERE r.id_alumno = %s
          AND e.tipo_estado = 'No realizada'
          AND t.nombre_tipo = %s
          AND r.fecha_inicio = CURDATE()
        ORDER BY r.id_rutina DESC
        LIMIT 1
        """,
        (id_alumno, nombre_tipo_entrenamiento),
    )
    rutina = cursor.fetchone()

    # Si no hay ninguna rutina para hoy en ese lugar, cerramos todo y
    # devolvemos None de una vez (no tiene caso seguir buscando sus
    # ejercicios si la rutina ni siquiera existe).
    if rutina is None:
        cursor.close()
        conexion.close()
        return None

    # Ya que sabemos el id_rutina, buscamos TODOS los ejercicios que le
    # corresponden (puede haber varios, por eso se usa fetchall() en
    # vez de fetchone()).
    cursor.execute(
        """
        SELECT ej.nombre_ejercicio, ej.animacion_ejercicio,
               re.series, re.repeticiones_min, re.repeticiones_max
        FROM rutina_ejercicio re
        JOIN ejercicio ej ON ej.id_ejercicio = re.id_ejercicio
        WHERE re.id_rutina = %s
        """,
        (rutina["id_rutina"],),
    )
    # Le agregamos una llave nueva al diccionario "rutina" (que ya
    # traia id_rutina, nombre_rutina y fecha_inicio), llamada
    # "ejercicios", con la lista de ejercicios que acabamos de traer.
    # Asi, quien reciba "rutina" tiene TODO junto en un solo objeto.
    rutina["ejercicios"] = cursor.fetchall()

    cursor.close()
    conexion.close()
    return rutina


def marcar_rutina_completada(id_rutina):
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT id_estado_realizacion FROM estado_realizacion WHERE tipo_estado = 'Realizada'"
    )
    id_estado_realizada = cursor.fetchone()["id_estado_realizacion"]

    cursor.execute(
        """
        SELECT r.id_alumno, r.fecha_inicio, r.id_profesional, r.nombre_rutina,
               a.nombre, a.ap_paterno
        FROM rutina r
        JOIN alumno a ON a.id_alumno = r.id_alumno
        WHERE r.id_rutina = %s
        """,
        (id_rutina,),
    )
    info_rutina = cursor.fetchone()

    cursor.execute(
        "UPDATE rutina SET id_estado_realizacion = %s WHERE id_rutina = %s",
        (id_estado_realizada, id_rutina),
    )

    cursor.execute(
        """
        SELECT r.id_rutina
        FROM rutina r
        JOIN estado_realizacion e ON e.id_estado_realizacion = r.id_estado_realizacion
        WHERE r.id_alumno = %s
          AND r.fecha_inicio = %s
          AND r.id_rutina != %s
          AND e.tipo_estado = 'No realizada'
        """,
        (info_rutina["id_alumno"], info_rutina["fecha_inicio"], id_rutina),
    )
    otras_rutinas_pendientes = cursor.fetchall()

    for otra in otras_rutinas_pendientes:
        cursor.execute(
            "DELETE FROM rutina_ejercicio WHERE id_rutina = %s", (otra["id_rutina"],)
        )
        cursor.execute("DELETE FROM rutina WHERE id_rutina = %s", (otra["id_rutina"],))

    conexion.commit()
    cursor.close()
    conexion.close()

    nombre_alumno = f"{info_rutina['nombre']} {info_rutina['ap_paterno']}"
    registrar_notificacion(
        info_rutina["id_profesional"], info_rutina["id_alumno"], nombre_alumno,
        tipo="rutina",
        texto=f"{nombre_alumno} completo la rutina",
        datos_extra={"nombre_rutina": info_rutina["nombre_rutina"], "estado": "Realizada"},
    )

    return True


def obtener_historial_entrenamientos(id_alumno, limite=5):
    """Trae las rutinas mas recientes del alumno con su nombre, estado
    y el LUGAR en el que se realizo (Casa o Gimnasio), para el
    'Historial Reciente de Entrenamientos'."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT a.nombre, a.ap_paterno, r.nombre_rutina, r.fecha_inicio,
               e.tipo_estado, t.nombre_tipo AS lugar
        FROM rutina r
        JOIN alumno a ON a.id_alumno = r.id_alumno
        JOIN estado_realizacion e ON e.id_estado_realizacion = r.id_estado_realizacion
        JOIN tipo_entrenamiento t ON t.id_tipo_entrenamiento = r.id_tipo_entrenamiento
        WHERE r.id_alumno = %s
        ORDER BY r.fecha_inicio DESC
        LIMIT %s
        """,
        (id_alumno, limite),
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


# ---------------------------------------------------------------------
# MIS METRICAS
# ---------------------------------------------------------------------

def registrar_medicion(id_alumno, fecha, peso, altura):
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO medicion (id_alumno, fecha, peso, altura)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE peso = VALUES(peso), altura = VALUES(altura)
            """,
            (id_alumno, fecha, peso, altura),
        )
        conexion.commit()

        cursor.execute(
            "SELECT nombre, ap_paterno, id_profesional FROM alumno WHERE id_alumno = %s",
            (id_alumno,),
        )
        info_alumno = cursor.fetchone()

        if info_alumno and info_alumno["id_profesional"]:
            nombre_alumno = f"{info_alumno['nombre']} {info_alumno['ap_paterno']}"
            registrar_notificacion(
                info_alumno["id_profesional"], id_alumno, nombre_alumno,
                tipo="medicion",
                texto=f"{nombre_alumno} registro su peso",
                datos_extra={"peso_kg": float(peso)},
            )

        return True
    except Exception as e:
        print("Error al registrar medicion:", e)
        return False
    finally:
        cursor.close()
        conexion.close()


def obtener_ultima_medicion(id_alumno):
    """Trae la medicion mas reciente (peso y altura), para el calculo
    del IMC."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT peso, altura FROM medicion WHERE id_alumno = %s ORDER BY fecha DESC LIMIT 1",
        (id_alumno,),
    )
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    return fila


def calcular_imc(peso_kg, altura_cm):
    """Calcula el Indice de Masa Corporal: peso (kg) / altura (m) al
    cuadrado. Devuelve una tupla (valor_imc, rango_texto)."""
    # Si no hay peso o altura (por ejemplo, un alumno que nunca
    # registro ninguna medicion), no se puede calcular nada: se
    # devuelve 0 y un texto explicando que no hay datos, en vez de
    # intentar dividir por cero (lo cual causaria un error de Python).
    if not peso_kg or not altura_cm:
        return 0, "Sin datos"

    # La formula del IMC usa la altura en METROS, pero en la base de
    # datos se guarda en CENTIMETROS, por eso se divide entre 100.
    altura_m = float(altura_cm) / 100
    # "altura_m ** 2" eleva la altura al cuadrado ("**" es el operador
    # de potencia en Python).
    imc = float(peso_kg) / (altura_m ** 2)

    # Esta cadena de if/elif clasifica el resultado en un rango de
    # texto, segun los limites medicos estandar del IMC.
    if imc < 18.5:
        rango = "Bajo peso"
    elif imc < 25:
        rango = "Rango Normal"
    elif imc < 30:
        rango = "Sobrepeso"
    else:
        rango = "Obesidad"

    # round(imc, 1) redondea el numero a 1 decimal (ej. 23.456 -> 23.5),
    # para que se vea mas limpio en pantalla. Se devuelven los 2
    # valores juntos como una TUPLA (imc, rango); quien llame a esta
    # funcion los recibe asi: "valor_imc, texto_rango = calcular_imc(...)".
    return round(imc, 1), rango


# ---------------------------------------------------------------------
# CREACION DE CUENTA Y FOTO (usadas por el Administrador y por el
# propio alumno desde 'Mi Perfil')
# ---------------------------------------------------------------------

def crear_alumno_detalle(id_usuario, nombre, ap_paterno, ap_materno, telefono, id_profesional=None):
    """Crea el registro en la tabla alumno para un usuario recien creado.
    id_profesional es opcional: si no se especifica, queda NULL (sin
    asignar) y se puede asignar despues desde 'Gestion de Usuarios'."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    # "ap_materno or None" es otro uso del operador "or" como atajo:
    # si ap_materno es una cadena vacia (""), se guarda None (NULL en
    # MySQL) en vez de guardar un texto vacio en la base de datos.
    cursor.execute(
        """
        INSERT INTO alumno (id_usuario, id_profesional, nombre, ap_paterno, ap_materno, telefono)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (id_usuario, id_profesional, nombre, ap_paterno, ap_materno or None, telefono or None),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def reasignar_profesional(id_alumno, id_profesional):
    """Actualiza SOLO el profesional asignado a un alumno. Se usa desde
    el dropdown 'Profesional' de la tabla en Gestion de Usuarios, para
    poder reasignar sin tener que abrir el formulario completo."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE alumno SET id_profesional = %s WHERE id_alumno = %s",
        (id_profesional, id_alumno),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def actualizar_foto_alumno(id_alumno, ruta_foto):
    """Guarda en la tabla alumno la ruta (texto) de la foto de perfil.
    La copia real del archivo la hace utilidades/imagenes.py; aqui solo
    se guarda la ruta, por eso la columna es VARCHAR y no una imagen."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE alumno SET foto = %s WHERE id_alumno = %s",
        (ruta_foto, id_alumno),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True
"""
Consultas relacionadas con el PROFESIONAL: su perfil, sus alumnos, la
asignacion de rutinas nuevas, y el catalogo de ejercicios que usa el
formulario "Asignar Rutina".
"""

# "date" se usa mas abajo en crear_rutina_con_ejercicios, para poner
# la fecha de HOY como respaldo si el profesional deja el campo de
# fecha vacio.
from datetime import date
from base_datos.conexion import obtener_conexion
from modelos.notificacion_modelo import obtener_notificaciones_profesional


def crear_profesional_detalle(id_usuario, nombre, ap_paterno, ap_materno, telefono):
    """Crea el registro en la tabla profesional para un usuario recien
    creado (usada por el Administrador en Gestion de Usuarios)."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO profesional (id_usuario, nombre, ap_paterno, ap_materno, telefono)
        VALUES (%s, %s, %s, %s, %s)
        """,
        # "ap_materno or None": si el apellido materno viene vacio
        # (""), se guarda NULL en la base de datos en vez de un texto
        # vacio (es OPCIONAL segun la tabla, por eso se le permite ser
        # NULL).
        (id_usuario, nombre, ap_paterno, ap_materno or None, telefono or None),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def listar_profesionales_activos():
    """Lista de profesionales (id + nombre completo) con cuenta activa,
    para el combo 'Asignar profesional' al crear un alumno nuevo."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    # CONCAT(...) es una funcion de MYSQL (no de Python) que junta
    # varios textos en uno solo. Aqui junta el nombre y el apellido
    # paterno con un espacio en medio, y le pone el alias
    # "nombre_completo" (con "AS") para poder leerlo despues como
    # fila["nombre_completo"].
    cursor.execute(
        """
        SELECT p.id_profesional, CONCAT(p.nombre, ' ', p.ap_paterno) AS nombre_completo
        FROM profesional p
        JOIN usuario u ON u.id_usuario = p.id_usuario
        WHERE u.estado = 'Activo'
        ORDER BY p.nombre
        """
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


# ---------------------------------------------------------------------
# PERFIL DEL PROFESIONAL (pantalla "Mi Perfil")
# ---------------------------------------------------------------------

def obtener_datos_perfil_profesional(id_usuario):
    """Trae los datos personales del profesional para 'Mi Perfil'."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    # Este JOIN junta "usuario" (donde vive el correo y la fecha de
    # registro) con "profesional" (donde viven nombre, apellidos,
    # telefono y foto) para traer TODO en una sola consulta, en vez de
    # hacer 2 consultas separadas.
    cursor.execute(
        """
        SELECT u.correo, u.fecha_registro,
               p.id_profesional, p.nombre, p.ap_paterno, p.ap_materno,
               p.telefono, p.foto
        FROM usuario u
        JOIN profesional p ON p.id_usuario = u.id_usuario
        WHERE u.id_usuario = %s
        """,
        (id_usuario,),
    )
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()

    if datos is None:
        return None

    # Como ap_materno, telefono y foto son columnas OPCIONALES en la
    # base de datos (pueden venir como None/NULL), aqui se reemplaza
    # cualquier None por una cadena vacia (""). Esto evita que la vista
    # tenga que estar revisando "si es None, pon vacio" cada vez que
    # use estos datos; ya llegan "limpios".
    datos["ap_materno"] = datos["ap_materno"] or ""
    datos["telefono"] = datos["telefono"] or ""
    datos["foto"] = datos["foto"] or ""

    # MySQL devuelve las fechas como objetos "datetime" de Python, no
    # como texto. .strftime("%d/%m/%Y") las convierte a un texto con
    # el formato dia/mes/anio (ej. "02/08/2026") para mostrarlas en
    # pantalla.
    if datos["fecha_registro"]:
        datos["fecha_registro"] = datos["fecha_registro"].strftime("%d/%m/%Y")

    return datos


def actualizar_datos_perfil_profesional(id_usuario, id_profesional, nombre,
                                         ap_paterno, ap_materno, correo, telefono):
    """Guarda los cambios que el profesional hizo en su propio perfil."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    # Aqui se ejecutan 2 UPDATE con el MISMO cursor, uno detras de
    # otro: el primero actualiza la tabla "profesional" (nombre,
    # apellidos, telefono), y el segundo actualiza el correo en la
    # tabla "usuario" (porque el correo NO vive en "profesional", vive
    # en "usuario"). Ambos se guardan juntos con un solo commit() al
    # final.
    cursor.execute(
        """
        UPDATE profesional
        SET nombre = %s, ap_paterno = %s, ap_materno = %s, telefono = %s
        WHERE id_profesional = %s
        """,
        (nombre, ap_paterno, ap_materno, telefono, id_profesional),
    )
    cursor.execute(
        "UPDATE usuario SET correo = %s WHERE id_usuario = %s",
        (correo, id_usuario),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def actualizar_foto_profesional(id_profesional, ruta_foto):
    """Guarda en la tabla profesional la ruta (texto) de la foto de perfil."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE profesional SET foto = %s WHERE id_profesional = %s",
        (ruta_foto, id_profesional),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


# ---------------------------------------------------------------------
# INICIO (dashboard del profesional)
# ---------------------------------------------------------------------

def obtener_resumen_dashboard_profesional(id_profesional):
    """Cuenta los alumnos activos del profesional y cuantas rutinas ha
    asignado en total, para las tarjetas de 'Inicio'."""
    conexion = obtener_conexion()
    if conexion is None:
        return {"alumnos_activos": 0, "rutinas_asignadas": 0}

    cursor = conexion.cursor(dictionary=True)

    # Cuenta cuantos alumnos tiene asignados este profesional Y cuya
    # cuenta este "Activo" (un alumno desactivado no cuenta como
    # "activo" en esta tarjeta, aunque siga asignado a el).
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM alumno a
        JOIN usuario u ON u.id_usuario = a.id_usuario
        WHERE a.id_profesional = %s AND u.estado = 'Activo'
        """,
        (id_profesional,),
    )
    alumnos_activos = cursor.fetchone()["total"]

    # Cuenta TODAS las rutinas que este profesional ha creado en
    # total (sin importar si estan realizadas, pendientes, o de que
    # alumno son).
    cursor.execute(
        "SELECT COUNT(*) AS total FROM rutina WHERE id_profesional = %s",
        (id_profesional,),
    )
    rutinas_asignadas = cursor.fetchone()["total"]

    cursor.close()
    conexion.close()
    return {"alumnos_activos": alumnos_activos, "rutinas_asignadas": rutinas_asignadas}


def obtener_actividad_reciente(id_profesional, limite=5):
    """
    Trae los eventos mas recientes de los alumnos de este profesional
    (rutinas completadas y mediciones registradas), leyendo directo de
    la bitacora en MongoDB.

    Antes esto se calculaba con 2 consultas de MySQL (una a rutina,
    otra a medicion) que se juntaban y ordenaban en Python cada vez
    que se abria la pantalla. Ahora, cada evento ya quedo guardado
    como un documento listo en Mongo desde el momento en que ocurrio
    (ver alumno_modelo.marcar_rutina_completada y registrar_medicion),
    asi que aqui solo se leen, sin volver a calcular nada.
    """
    notificaciones = obtener_notificaciones_profesional(id_profesional, limite)

    eventos = []
    for doc in notificaciones:
        eventos.append({
            "texto": doc["texto"],
            "fecha": doc["fecha"],
        })
    return eventos


# ---------------------------------------------------------------------
# MIS ALUMNOS
# ---------------------------------------------------------------------

def listar_mis_alumnos(id_profesional, busqueda=""):
    """Trae los alumnos asignados a este profesional (con su estado de
    cuenta), filtrados por nombre o correo si se escribio algo en el
    buscador."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    # "LIKE %s" con el valor "%busqueda%" (los signos de porcentaje
    # los agrega Python antes de mandarlo) es como decir "que CONTENGA
    # este texto en cualquier parte", no que sea exactamente igual.
    # Se busca en 3 columnas a la vez con OR: nombre, apellido paterno
    # o correo.
    cursor.execute(
        """
        SELECT a.id_alumno, a.nombre, a.ap_paterno, u.correo, u.estado
        FROM alumno a
        JOIN usuario u ON u.id_usuario = a.id_usuario
        WHERE a.id_profesional = %s
          AND (a.nombre LIKE %s OR a.ap_paterno LIKE %s OR u.correo LIKE %s)
        ORDER BY a.nombre
        """,
        (id_profesional, f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"),
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


def obtener_encabezado_alumno(id_alumno):
    """Trae los datos que se muestran arriba de 'Detalle Alumno':
    nombre completo, correo, telefono, foto y fecha de registro."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT a.nombre, a.ap_paterno, a.ap_materno, a.telefono, a.foto,
               u.correo, u.fecha_registro
        FROM alumno a
        JOIN usuario u ON u.id_usuario = a.id_usuario
        WHERE a.id_alumno = %s
        """,
        (id_alumno,),
    )
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()

    if datos and datos["fecha_registro"]:
        datos["fecha_registro"] = datos["fecha_registro"].strftime("%d/%m/%Y")
    return datos


# ---------------------------------------------------------------------
# ASIGNAR / CREAR RUTINA
# ---------------------------------------------------------------------

def obtener_zonas_musculares():
    """Lista de grupos musculares (Pecho, Espalda, Piernas...) para el
    primer combo del formulario de asignar rutina."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_zona_muscular, nombre_zona FROM zona_muscular ORDER BY nombre_zona")
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


def obtener_ejercicios_por_zona_y_lugar(id_zona_muscular, id_tipo_entrenamiento):
    """Lista de ejercicios que pertenecen al grupo muscular Y al lugar
    de entrenamiento elegidos. ejercicio.id_tipo_entrenamiento es una
    llave foranea (INT) a la misma tabla tipo_entrenamiento que ya usa
    rutina, en vez de comparar por el nombre en texto ('Casa'/'Gimnasio')."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    # Los ejercicios se filtran por 2 condiciones AL MISMO TIEMPO (con
    # AND): que sean de la zona muscular elegida, Y que sean del lugar
    # de entrenamiento elegido. Asi, si cambias "Pecho" a "Piernas" en
    # la pantalla, o cambias "Casa" a "Gimnasio", la lista de
    # ejercicios se vuelve a filtrar correctamente.
    cursor.execute(
        """
        SELECT id_ejercicio, nombre_ejercicio
        FROM ejercicio
        WHERE id_zona_muscular = %s AND id_tipo_entrenamiento = %s
        ORDER BY nombre_ejercicio
        """,
        (id_zona_muscular, id_tipo_entrenamiento),
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


def obtener_tipos_entrenamiento():
    """Lista de lugares de entrenamiento (Casa / Gimnasio)."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_tipo_entrenamiento, nombre_tipo FROM tipo_entrenamiento ORDER BY nombre_tipo")
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


def crear_rutina_con_ejercicios(id_alumno, id_profesional, nombre_rutina,
                                 fecha_inicio, id_tipo_entrenamiento, lista_ejercicios):
    """
    Crea la rutina y todos sus ejercicios de un solo golpe.

    lista_ejercicios: lista de diccionarios con id_ejercicio, series,
    repeticiones_min y repeticiones_max (la tabla que arma la vista
    mientras el profesional presiona 'Asignar ejercicio +').

    La rutina se crea siempre con estado 'No realizada', porque la esta
    asignando el profesional apenas ahora; el alumno la marcara como
    realizada despues, desde 'Mis Rutinas'.
    """
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor(dictionary=True)

    # Primero buscamos el ID del estado "No realizada" (recordemos: en
    # la tabla rutina nunca se guarda el TEXTO "No realizada", solo su
    # numero de id, que apunta a la tabla estado_realizacion).
    cursor.execute(
        "SELECT id_estado_realizacion FROM estado_realizacion WHERE tipo_estado = 'No realizada'"
    )
    fila_estado = cursor.fetchone()
    if fila_estado is None:
        # Si por algun motivo esa fila no existe en la base de datos
        # (algo raro, pero posible si se borro el catalogo por
        # accidente), no se puede continuar: se cierra todo y se
        # devuelve False.
        cursor.close()
        conexion.close()
        return False
    id_estado_no_realizada = fila_estado["id_estado_realizacion"]

    try:
        # Se crea la fila principal de la rutina. "fecha_inicio or
        # date.today()" es otro atajo: si no se paso una fecha (o
        # vino vacia), se usa la fecha de HOY como respaldo.
        cursor.execute(
            """
            INSERT INTO rutina (id_alumno, id_profesional, nombre_rutina, fecha_inicio,
                                 id_estado_realizacion, id_tipo_entrenamiento)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id_alumno, id_profesional, nombre_rutina, fecha_inicio or date.today(),
             id_estado_no_realizada, id_tipo_entrenamiento),
        )
        # "cursor.lastrowid" es un atributo especial que trae el ID
        # que MySQL le acaba de asignar automaticamente a la fila que
        # se acaba de insertar (recordemos que id_rutina es
        # AUTO_INCREMENT, asi que nosotros no lo elegimos, MySQL lo
        # genera solo). Lo necesitamos para poder insertar los
        # ejercicios apuntando a ESTA rutina especifica.
        id_rutina_nueva = cursor.lastrowid

        # Recorremos la lista de ejercicios que el profesional armo en
        # pantalla, y por cada uno insertamos una fila en
        # "rutina_ejercicio", relacionandola con la rutina recien
        # creada.
        for ejercicio in lista_ejercicios:
            cursor.execute(
                """
                INSERT INTO rutina_ejercicio (id_rutina, id_ejercicio, series,
                                               repeticiones_min, repeticiones_max)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (id_rutina_nueva, ejercicio["id_ejercicio"], ejercicio["series"],
                 ejercicio["repeticiones_min"], ejercicio["repeticiones_max"]),
            )

        # Solo hasta que TODO (la rutina + todos sus ejercicios) se
        # inserto sin errores, se confirma con commit(). Si algo
        # falla en medio del "for" (por ejemplo, un ejercicio con datos
        # invalidos), el except de abajo lo atrapa y NADA se guarda
        # (gracias al rollback), evitando dejar una rutina "a medias"
        # sin ejercicios.
        conexion.commit()
        return True
    except Exception as e:
        print("Error al crear la rutina:", e)
        # "conexion.rollback()" deshace TODOS los cambios que se
        # hicieron desde el ultimo commit (aqui, el INSERT de la
        # rutina y los INSERT de ejercicios que ya se hubieran
        # alcanzado a hacer antes del error). Es la forma de
        # garantizar que, si algo sale mal, no quede la base de datos
        # en un estado incompleto/inconsistente.
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()
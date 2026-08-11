"""
Este archivo se encarga de todo lo relacionado con el USUARIO:
iniciar sesion, ver su perfil, editarlo y cambiar su contrasenia.

Todas las funciones siguen el mismo patron sencillo:
1. Abrir conexion a la base de datos.
2. Si no se pudo conectar, salir devolviendo None o False.
3. Hacer la consulta (SELECT o UPDATE).
4. Cerrar la conexion.
5. Devolver el resultado.
"""
from base_datos.conexion import obtener_conexion


def validar_login(correo, contrasena):
    """Revisa si el correo y la contrasenia son correctos.
    Si todo esta bien, devuelve los datos del usuario (diccionario).
    Si algo falla (correo no existe, contrasenia mala, cuenta inactiva),
    devuelve None."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_usuario, correo, contrasena, rol, estado FROM usuario WHERE correo = %s",
        (correo,),
    )
    # fetchone() trae la primera (y unica, porque el correo es UNIQUE
    # en la base de datos) fila que coincida con ese correo. Si nadie
    # tiene ese correo registrado, "usuario" queda como None.
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    # Estas 3 validaciones se hacen UNA POR UNA, en orden, y cada una
    # "sale" de la funcion de inmediato con un "return None" si algo
    # esta mal. A esto se le llama a veces "clausula de guarda" (guard
    # clause): en vez de anidar muchos "if" uno dentro de otro, se
    # revisa cada condicion mala y se sale rapido, dejando el resto
    # del codigo mas plano y facil de leer.
    if usuario is None:
        return None  # ese correo no existe

    if usuario["estado"] != "Activo":
        return None  # la cuenta esta desactivada

    # NOTA DE SEGURIDAD: aqui se compara la contrasenia tal cual como
    # texto plano. En un sistema real de produccion, NUNCA se guarda
    # ni se compara asi: se usaria una funcion de "hash" (como bcrypt)
    # para que ni siquiera el administrador de la base de datos pueda
    # ver la contrasenia real de nadie. Para este proyecto escolar se
    # simplifico a texto plano.
    if usuario["contrasena"] != contrasena:
        return None  # la contrasenia no coincide

    # Si paso las 3 validaciones, se devuelve el diccionario completo
    # del usuario (id_usuario, correo, contrasena, rol, estado), que
    # principal.py usara para decidir que menu mostrar.
    return usuario


def obtener_datos_perfil(id_usuario):
    """Trae los datos personales del alumno para mostrarlos en 'Mi Perfil'."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.correo, u.fecha_registro,
               a.id_alumno, a.nombre, a.ap_paterno, a.ap_materno,
               a.telefono, a.fecha_nacimiento, a.foto
        FROM usuario u
        JOIN alumno a ON a.id_usuario = u.id_usuario
        WHERE u.id_usuario = %s
        """,
        (id_usuario,),
    )
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()

    if datos is None:
        return None

    # Se limpian los campos opcionales que pudieran venir NULL desde
    # la base de datos, reemplazandolos por cadena vacia, para que la
    # vista no tenga que preocuparse por eso.
    datos["ap_materno"] = datos["ap_materno"] or ""
    datos["telefono"] = datos["telefono"] or ""
    datos["foto"] = datos["foto"] or ""

    # MySQL entrega las fechas como objetos "datetime"/"date" de
    # Python, no como texto. Aqui se convierten a texto con
    # .strftime(formato), usando un formato distinto para cada una:
    # "fecha_registro" se muestra como dia/mes/anio (para el
    # encabezado del perfil)...
    if datos["fecha_registro"]:
        datos["fecha_registro"] = datos["fecha_registro"].strftime("%d/%m/%Y")

    # ...mientras que "fecha_nacimiento" se convierte a anio-mes-dia,
    # porque asi es como espera el TEXTO el campo editable de la
    # pantalla (el formato que usa MySQL tambien por dentro para el
    # tipo DATE), para que el alumno pueda editarla facilmente.
    if datos["fecha_nacimiento"]:
        datos["fecha_nacimiento"] = datos["fecha_nacimiento"].strftime("%Y-%m-%d")
    else:
        datos["fecha_nacimiento"] = ""

    return datos


def actualizar_datos_perfil(id_usuario, id_alumno, nombre, ap_paterno, ap_materno,
                             correo, telefono, fecha_nacimiento):
    """Guarda los cambios que el alumno hizo en su perfil."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    # Igual que en profesional_modelo.py: se hacen 2 UPDATE con el
    # mismo cursor (uno para "alumno", otro para "usuario"), porque el
    # correo vive en una tabla distinta al resto de los datos
    # personales. Ambos se confirman juntos con un solo commit().
    cursor.execute(
        """
        UPDATE alumno
        SET nombre = %s, ap_paterno = %s, ap_materno = %s,
            telefono = %s, fecha_nacimiento = %s
        WHERE id_alumno = %s
        """,
        (nombre, ap_paterno, ap_materno, telefono, fecha_nacimiento, id_alumno),
    )
    cursor.execute(
        "UPDATE usuario SET correo = %s WHERE id_usuario = %s",
        (correo, id_usuario),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def cambiar_contrasena(id_usuario, nueva_contrasena):
    """Cambia la contrasenia del usuario.
    NOTA: en un sistema real esto se guardaria encriptado, no en texto plano."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE usuario SET contrasena = %s WHERE id_usuario = %s",
        (nueva_contrasena, id_usuario),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


# ---------------------------------------------------------------------
# ADMINISTRACION DE CUENTAS (usadas por el Administrador)
#
# Estas funciones solo tocan la tabla "usuario". Van en este archivo
# porque usuario_modelo.py es el UNICO responsable de esa tabla
# (principio de Responsabilidad Unica). admin_modelo.py las importa y
# las combina con alumno_modelo/profesional_modelo cuando necesita crear
# una cuenta completa (usuario + su detalle de alumno o profesional).
# ---------------------------------------------------------------------

def correo_ya_existe(correo):
    """Revisa si ya hay una cuenta registrada con ese correo (evita
    duplicados antes de intentar crear una cuenta nueva)."""
    conexion = obtener_conexion()
    if conexion is None:
        # Si no hay conexion, se devuelve True ("si existe") por
        # seguridad: es mejor BLOQUEAR la creacion de una cuenta por
        # error, que arriesgarse a crear un correo duplicado si de
        # verdad no se pudo checar.
        return True

    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
    # "cursor.fetchone() is not None" es una forma corta de convertir
    # el resultado en un valor Verdadero/Falso: si SI encontro una
    # fila con ese correo, fetchone() regresa esa fila (que no es
    # None), asi que la expresion completa da True. Si NO encontro
    # nada, fetchone() regresa None, y la expresion da False.
    existe = cursor.fetchone() is not None
    cursor.close()
    conexion.close()
    return existe


def crear_usuario(correo, contrasena, rol):
    """Crea el registro base en la tabla usuario (login, rol y estado).
    'rol' debe ser exactamente 'Administrador', 'Profesional' o 'Alumno'
    (asi esta definido el ENUM en la base de datos).
    Devuelve el id_usuario nuevo, o None si algo fallo."""
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor()
    try:
        # El estado siempre se pone "Activo" al crear una cuenta
        # nueva, por eso esta escrito directo en el texto del INSERT
        # (no es un parametro "%s"), no hace falta que cambie nunca en
        # este punto.
        cursor.execute(
            "INSERT INTO usuario (correo, contrasena, rol, estado) VALUES (%s, %s, %s, 'Activo')",
            (correo, contrasena, rol),
        )
        conexion.commit()
        # De nuevo, "cursor.lastrowid" trae el id_usuario que MySQL
        # genero automaticamente (AUTO_INCREMENT) para esta fila
        # nueva, para poder usarlo despues al crear el "alumno" o
        # "profesional" correspondiente.
        id_usuario_nuevo = cursor.lastrowid
        return id_usuario_nuevo
    except Exception as e:
        print("Error al crear usuario:", e)
        return None
    finally:
        cursor.close()
        conexion.close()


def listar_todos_los_usuarios(busqueda="", filtro_rol="Todos"):
    """Trae la lista de cuentas para la pantalla 'Gestion de Usuarios',
    con el nombre completo (si tiene, segun sea alumno o profesional) y
    el nombre del profesional asignado (solo aplica a alumnos)."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)

    # Esta es la consulta mas compleja del proyecto. Se arma como una
    # cadena de texto en una variable ("consulta"), en vez de
    # escribirla directo dentro de cursor.execute(...), porque mas
    # abajo se le agrega un pedazo EXTRA de texto solo si el
    # administrador eligio un filtro de rol especifico.
    #
    # Usa 3 "LEFT JOIN": a diferencia de un JOIN normal (que solo trae
    # filas que SI coinciden en ambas tablas), un LEFT JOIN trae TODAS
    # las filas de "usuario", aunque no tengan pareja en "alumno" o
    # "profesional" (por ejemplo, un Administrador no tiene fila en
    # ninguna de esas 2 tablas, pero igual debe aparecer en la lista).
    #
    # COALESCE(...) es una funcion de MySQL que revisa varios valores
    # en orden y regresa el PRIMERO que no sea NULL. Aqui se usa para
    # decidir el "nombre_completo": si el usuario es alumno, usa su
    # nombre+apellido de la tabla alumno; si es profesional, usa el de
    # profesional; si no es ninguno de los 2 (es Administrador), usa
    # una cadena vacia.
    #
    # El segundo LEFT JOIN a "profesional" (con el alias "pa", de
    # "profesional asignado") es para poder mostrar, en la columna
    # "Profesional" de la tabla, el NOMBRE del entrenador que tiene
    # asignado cada alumno (si es que tiene uno).
    consulta = """
        SELECT u.id_usuario, u.correo, u.rol, u.estado,
               a.id_alumno AS id_detalle_alumno,
               COALESCE(
                   CONCAT(a.nombre, ' ', a.ap_paterno),
                   CONCAT(p.nombre, ' ', p.ap_paterno),
                   ''
               ) AS nombre_completo,
               a.id_profesional AS id_profesional_asignado,
               CONCAT(pa.nombre, ' ', pa.ap_paterno) AS profesional_asignado
        FROM usuario u
        LEFT JOIN alumno a ON a.id_usuario = u.id_usuario
        LEFT JOIN profesional p ON p.id_usuario = u.id_usuario
        LEFT JOIN profesional pa ON pa.id_profesional = a.id_profesional
        WHERE (u.correo LIKE %s OR a.nombre LIKE %s OR p.nombre LIKE %s)
    """
    # "parametros" es una LISTA (no una tupla) porque mas abajo,
    # dependiendo del filtro elegido, se le puede AGREGAR un elemento
    # mas con .append(...). Las listas se pueden modificar despues de
    # creadas; las tuplas no.
    parametros = [f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"]

    # Si el administrador eligio un rol especifico en el dropdown de
    # filtro (en vez de "Todos"), se le agrega una condicion EXTRA a
    # la consulta ("AND u.rol = %s"), y su valor correspondiente a la
    # lista de parametros.
    if filtro_rol != "Todos":
        consulta += " AND u.rol = %s"
        parametros.append(filtro_rol)

    consulta += " ORDER BY u.id_usuario"

    # cursor.execute() espera que los parametros vengan como una
    # TUPLA, no como lista; por eso se convierte aqui con tuple(...)
    # justo antes de usarlos.
    cursor.execute(consulta, tuple(parametros))
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


def actualizar_estado_usuario(id_usuario, nuevo_estado):
    """Activa o desactiva una cuenta. nuevo_estado debe ser 'Activo' o
    'Inactivo' (los valores exactos del ENUM)."""
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE usuario SET estado = %s WHERE id_usuario = %s",
        (nuevo_estado, id_usuario),
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def contar_usuarios_por_rol():
    """Cuenta cuantos usuarios hay en total y cuantos de cada rol, para
    las tarjetas del dashboard del Administrador."""
    conexion = obtener_conexion()
    if conexion is None:
        return {"total": 0, "profesionales": 0, "alumnos": 0}

    cursor = conexion.cursor(dictionary=True)
    # "SUM(rol = 'Profesional')" es un truco muy comun en SQL: la
    # comparacion "rol = 'Profesional'" da 1 (verdadero) o 0 (falso)
    # por cada fila; SUM() de esos 1s y 0s termina contando cuantas
    # filas cumplen esa condicion. Asi, en UNA SOLA consulta se sacan
    # los 3 numeros (total, profesionales, alumnos) en vez de hacer 3
    # consultas separadas.
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(rol = 'Profesional') AS profesionales,
            SUM(rol = 'Alumno') AS alumnos
        FROM usuario
        """
    )
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()

    # "int(fila['profesionales'] or 0)" convierte el resultado de SUM()
    # a un entero normal de Python (SUM a veces regresa un tipo
    # Decimal o None si la tabla estuviera vacia), con 0 como respaldo
    # si viniera None.
    return {
        "total": fila["total"] or 0,
        "profesionales": int(fila["profesionales"] or 0),
        "alumnos": int(fila["alumnos"] or 0),
    }


def verificar_sesion_valida(id_usuario, rol):
    """
    Revisa que una sesion guardada en disco todavia sea valida:
    que la cuenta siga existiendo, que su rol no haya cambiado, y que
    su estado siga siendo 'Activo' (por si un administrador la
    desactivo mientras la app estaba cerrada).
    """
    conexion = obtener_conexion()
    if conexion is None:
        return False

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT rol, estado FROM usuario WHERE id_usuario = %s", (id_usuario,)
    )
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()

    # Si no se encontro ninguna fila con ese id_usuario (la cuenta se
    # borro por completo), la sesion definitivamente ya no es valida.
    if fila is None:
        return False

    # "and" aqui exige que las 2 condiciones sean verdaderas al mismo
    # tiempo: que el rol guardado en el archivo de sesion coincida CON
    # el rol actual en la base de datos, Y que el estado actual sea
    # "Activo". Si cualquiera de las 2 fallo, la funcion completa
    # regresa False.
    return fila["rol"] == rol and fila["estado"] == "Activo"
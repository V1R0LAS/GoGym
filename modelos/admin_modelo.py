"""
Logica del ADMINISTRADOR: dashboard general y creacion/gestion de
cuentas de usuario.

Responsabilidad Unica, pero con un matiz importante: crear una cuenta
completa involucra 2 tablas (usuario + alumno/profesional), y cada una
de esas tablas ya tiene su propio "duenio" (usuario_modelo.py,
alumno_modelo.py, profesional_modelo.py). Por eso admin_modelo.py NO
hace INSERT directo a esas tablas; solo ORQUESTA llamando a las
funciones que ya existen en esos archivos. Esto es el principio de
Inversion de Dependencias aplicado de forma sencilla: admin_modelo
depende de funciones (abstracciones), no del detalle SQL de cada tabla.
"""

# Importamos los 3 modelos que este archivo va a "orquestar". Se
# importa el MODULO completo (no funciones sueltas con "from ... import"),
# por eso mas abajo se usa "usuario_modelo.crear_usuario(...)" en vez
# de solo "crear_usuario(...)". Esto deja mas claro, con solo leer el
# codigo, DE DONDE viene cada funcion que se esta llamando.
from modelos import usuario_modelo
from modelos import alumno_modelo
from modelos import profesional_modelo


def obtener_resumen_dashboard_admin():
    """Numeros para las tarjetas de 'Inicio' del Administrador."""
    # Le pedimos el conteo (ya calculado) a usuario_modelo, que es el
    # UNICO responsable de la tabla "usuario" (de donde sale el rol de
    # cada cuenta). "conteo" es un diccionario con las llaves "total",
    # "profesionales" y "alumnos".
    conteo = usuario_modelo.contar_usuarios_por_rol()

    # Armamos un diccionario NUEVO, con nombres de llave mas
    # "amigables" para la vista (ej. "usuarios_totales" en vez de
    # "total"). Esto separa el nombre interno que usa el modelo del
    # nombre que espera la pantalla, por si un dia cambia uno sin
    # tener que tocar el otro.
    return {
        "usuarios_totales": conteo["total"],
        "profesionales": conteo["profesionales"],
        "alumnos": conteo["alumnos"],
    }


def listar_usuarios(busqueda="", filtro_rol="Todos"):
    """Lista de cuentas para la tabla de 'Gestion de Usuarios'."""
    # "busqueda" y "filtro_rol" son PARAMETROS CON VALOR POR DEFECTO:
    # si quien llama a esta funcion no le pasa nada, se usan estos
    # valores automaticamente (buscador vacio, sin filtrar por rol).
    # Aqui simplemente se le "reenvia" la peticion a usuario_modelo,
    # que es quien de verdad sabe hacer el JOIN entre usuario/alumno/
    # profesional para armar esa tabla.
    return usuario_modelo.listar_todos_los_usuarios(busqueda, filtro_rol)


def listar_profesionales_disponibles():
    """Lista de profesionales activos para el combo 'Asignar profesional'.
    Se reexpone aqui para que la vista solo importe admin_modelo y nunca
    tenga que hablarle directo a profesional_modelo (Responsabilidad Unica:
    la vista de Administrador solo conoce admin_modelo)."""
    # Esta funcion "no hace nada nuevo": solo llama a la funcion real
    # que vive en profesional_modelo.py y regresa su resultado tal
    # cual. Se le llama "reexponer" (o a veces "delegar"): existe para
    # que la vista de Administrador SOLO necesite importar
    # admin_modelo, sin tener que saber que profesional_modelo.py
    # existe. Si el dia de manana cambia como se consiguen los
    # profesionales, solo se toca esta linea.
    return profesional_modelo.listar_profesionales_activos()


def crear_cuenta(tipo_cuenta, nombre, ap_paterno, ap_materno, correo, telefono, contrasena):
    """
    Crea una cuenta nueva completa.

    tipo_cuenta: 'Alumno', 'Profesional' o 'Administrador' (tal cual
    los valores del ENUM de la base de datos).

    Devuelve (True, "") si todo salio bien, o (False, "mensaje de error")
    para que la vista le muestre al administrador que fue lo que fallo.
    """
    # Validacion 1: campos obligatorios para CUALQUIER tipo de cuenta.
    # "not correo" es Verdadero si correo es una cadena vacia (""),
    # None, o cualquier valor que Python considere "vacio".
    if not correo or not contrasena:
        return False, "Correo y contrasenia son obligatorios."

    # Validacion 2: el nombre solo es obligatorio si la cuenta va a
    # tener una tabla de detalle (Alumno o Profesional). El
    # Administrador no guarda nombre en ningun lado, por eso no aplica
    # para el.
    # "tipo_cuenta in ('Alumno', 'Profesional')" revisa si el valor de
    # tipo_cuenta esta DENTRO de esa lista (tupla) de opciones.
    if tipo_cuenta in ("Alumno", "Profesional") and not nombre:
        return False, "El nombre es obligatorio para Alumno y Profesional."

    # Validacion 3: que el correo no este ya usado por otra cuenta
    # (la tabla usuario tiene una restriccion UNIQUE en correo, pero es
    # mejor avisarle al administrador ANTES de intentar el INSERT, con
    # un mensaje claro, en vez de dejar que MySQL truene con un error
    # tecnico dificil de entender).
    if usuario_modelo.correo_ya_existe(correo):
        return False, "Ya existe una cuenta registrada con ese correo."

    # 1. Se crea primero el registro base en "usuario" (login + rol).
    # "crear_usuario" devuelve el id_usuario nuevo (un numero), o None
    # si algo salio mal en el INSERT.
    id_usuario_nuevo = usuario_modelo.crear_usuario(correo, contrasena, tipo_cuenta)
    if id_usuario_nuevo is None:
        return False, "No se pudo crear la cuenta. Intenta de nuevo."

    # 2. Segun el tipo de cuenta, se crea el detalle correspondiente
    #    en la tabla que le toca (alumno o profesional). El
    #    Administrador no tiene tabla de detalle (no guarda nombre en
    #    ningun otro lado ademas de "usuario").
    if tipo_cuenta == "Alumno":
        # Como el Administrador ya no asigna el profesional desde este
        # formulario (eso se hace despues, desde la tabla), aqui
        # siempre se crea "sin profesional asignado" (None).
        exito_detalle = alumno_modelo.crear_alumno_detalle(
            id_usuario_nuevo, nombre, ap_paterno, ap_materno, telefono, id_profesional=None
        )
    elif tipo_cuenta == "Profesional":
        exito_detalle = profesional_modelo.crear_profesional_detalle(
            id_usuario_nuevo, nombre, ap_paterno, ap_materno, telefono
        )
    else:
        # Si no es Alumno ni Profesional, es Administrador: no hay
        # nada mas que guardar, asi que se considera "exitoso" de una
        # vez (True), sin llamar a ningun otro modelo.
        exito_detalle = True

    # Si el detalle fallo (por ejemplo, un error de MySQL al insertar
    # en "alumno"), la cuenta de acceso YA se creo en "usuario", pero
    # sin sus datos personales. Se le avisa al administrador de este
    # caso especifico, para que sepa que algo quedo a medias.
    if not exito_detalle:
        return False, "La cuenta de acceso se creo, pero fallo al guardar los datos personales."

    # Si todo salio bien: exito=True, y el mensaje de error va vacio
    # (no se necesita, porque no hubo error).
    return True, ""


def establecer_estado_usuario(id_usuario, nuevo_estado):
    """Pone el estado exacto que se elige en el dropdown de la tabla
    ('Activo' o 'Inactivo'), sin necesidad de saber el estado anterior."""
    # Esta es otra funcion de "reexponer": simplemente le pasa el
    # trabajo real a usuario_modelo, que es quien sabe hacer el UPDATE
    # a la tabla "usuario".
    return usuario_modelo.actualizar_estado_usuario(id_usuario, nuevo_estado)


def reasignar_profesional_alumno(id_alumno, id_profesional):
    """Cambia el profesional asignado a un alumno directamente desde
    el dropdown 'Profesional' de la tabla (id_profesional puede ser
    None para dejarlo sin asignar)."""
    return alumno_modelo.reasignar_profesional(id_alumno, id_profesional)


def restablecer_contrasena(id_usuario, nueva_contrasena):
    """Restablece la contrasenia de cualquier cuenta. Se reutiliza la
    misma funcion que usa el propio usuario en 'Mi Perfil', porque la
    operacion (UPDATE a la tabla usuario) es exactamente la misma."""
    return usuario_modelo.cambiar_contrasena(id_usuario, nueva_contrasena)
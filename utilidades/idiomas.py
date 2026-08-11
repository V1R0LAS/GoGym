"""
Sistema simple de idiomas (Espaniol / Ingles) para la app.

Responsabilidad Unica: este archivo SOLO guarda los textos traducidos
y cual idioma esta activo en este momento. No dibuja nada, no sabe
nada de customtkinter; las vistas le piden el texto ya traducido con
obtener_texto('clave') y lo muestran donde les corresponda.
"""

# Variable de modulo: el idioma activo ahora mismo para TODA la app
# (empieza en espaniol por defecto).
IDIOMA_ACTUAL = "es"

# Diccionario de traducciones: cada 'clave' (ej. "correo") tiene un
# texto distinto segun el idioma. Para agregar una pantalla nueva a
# este sistema, solo hay que agregar sus claves aqui, en los 2 idiomas.
TEXTOS = {
    "es": {
        "correo": "Correo electronico",
        "contrasenia": "Contrasenia",
        "iniciar": "Iniciar",
        "error_titulo": "Error de inicio de sesion",
        "error_mensaje": "Correo o contrasenia incorrectos, o la cuenta esta inactiva.",
        "aviso_privacidad_link": "Aviso de Privacidad",
        "aviso_privacidad_titulo": "Aviso de Privacidad",
        "aviso_privacidad_cuerpo": (
            "GoGym recaba tus datos personales (nombre, correo, telefono, fecha de "
            "nacimiento, mediciones de peso/altura y fotografia de perfil) unicamente "
            "para brindarte el servicio de seguimiento de entrenamiento dentro de la "
            "aplicacion. Tus datos no se comparten con terceros ajenos al gimnasio. "
            "Tienes derecho a acceder, corregir o solicitar la eliminacion de tu "
            "informacion personal en cualquier momento, contactando a un administrador "
            "de tu gimnasio."
        ),
    },
    "en": {
        "correo": "Email",
        "contrasenia": "Password",
        "iniciar": "Sign In",
        "error_titulo": "Login Error",
        "error_mensaje": "Incorrect email or password, or the account is inactive.",
        "aviso_privacidad_link": "Privacy Notice",
        "aviso_privacidad_titulo": "Privacy Notice",
        "aviso_privacidad_cuerpo": (
            "GoGym collects your personal data (name, email, phone number, date of "
            "birth, weight/height measurements, and profile photo) solely to provide "
            "you with the workout tracking service within the application. Your data "
            "is not shared with third parties outside the gym. You have the right to "
            "access, correct, or request the deletion of your personal information at "
            "any time by contacting an administrator at your gym."
        ),
    },
}


def obtener_texto(clave):
    """
    Devuelve el texto traducido para 'clave', segun el idioma activo
    en este momento. Si la clave no existiera en el diccionario (por
    ejemplo, si se le olvido a alguien agregarla), devuelve la clave
    tal cual, en vez de tronar — asi nunca se ve un error feo en
    pantalla por una traduccion faltante.
    """
    return TEXTOS.get(IDIOMA_ACTUAL, {}).get(clave, clave)


def cambiar_idioma(nuevo_idioma):
    """Cambia el idioma activo de toda la app ('es' o 'en')."""
    global IDIOMA_ACTUAL
    if nuevo_idioma in TEXTOS:
        IDIOMA_ACTUAL = nuevo_idioma


def idioma_contrario():
    """Devuelve el OTRO idioma (el que no esta activo ahorita), para
    poner en el boton de cambiar idioma (ej. si estoy en espaniol, el
    boton debe ofrecer 'EN')."""
    return "en" if IDIOMA_ACTUAL == "es" else "es"
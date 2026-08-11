"""
Manejo de la foto de perfil del usuario (alumno o profesional).

Responsabilidad Unica: este archivo SOLO se encarga de archivos e
imagenes (copiar la foto elegida a la carpeta del proyecto, recortarla
en circulo y cargarla como CTkImage). No sabe nada de MySQL: guardar
la ruta de la foto en la base de datos es trabajo de los modelos
(alumno_modelo.actualizar_foto_alumno / profesional_modelo.actualizar_foto_profesional).

Por que se guarda solo la RUTA y no la imagen dentro de la base de
datos: la columna "foto" es un VARCHAR(255), pensada para un texto
corto (la ruta del archivo), no para guardar los bytes de la imagen.
"""
import os

# "shutil" es una libreria de la libreria estandar de Python
# especializada en operaciones de archivos "de alto nivel" (copiar,
# mover, borrar carpetas completas, etc.) - mas comoda que manipular
# los bytes del archivo a mano.
import shutil

# "uuid" (Universally Unique Identifier) es una libreria que genera
# identificadores UNICOS al azar, practicamente imposibles de repetir
# por accidente (la probabilidad de que 2 se generen iguales es
# astronomicamente baja). Se usa aqui para nombrar cada foto subida
# con un nombre que nunca choque con el de otra.
import uuid
import customtkinter as ctk

# "Image" ya la conocemos (abrir/procesar imagenes). "ImageDraw" es la
# herramienta de Pillow para DIBUJAR formas encima de una imagen
# (lineas, circulos, rectangulos, etc.) - aqui se usa para dibujar el
# circulo que se usa como "molde" de recorte.
from PIL import Image, ImageDraw

# Carpeta raiz del proyecto (2 niveles arriba: utilidades/ -> gogym_app/)
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta completa a la carpeta donde se van a guardar TODAS las fotos de
# perfil de TODOS los usuarios (alumnos y profesionales por igual).
CARPETA_PERFILES = os.path.join(CARPETA_BASE, "recursos", "imagenes", "perfiles")


def guardar_foto_perfil(ruta_origen):
    """
    Copia la imagen que el usuario eligio (de cualquier carpeta de su
    computadora) hacia recursos/imagenes/perfiles/, con un nombre unico
    para que nunca se sobreescriba la foto de otro usuario.

    Devuelve la ruta RELATIVA (a partir de la carpeta del proyecto) que
    se debe guardar en la base de datos.
    """
    # "os.makedirs(carpeta, exist_ok=True)" crea la carpeta de
    # perfiles si todavia no existe (por ejemplo, la primerisima vez
    # que alguien sube una foto en una instalacion nueva del proyecto).
    # "exist_ok=True" evita que truene con un error si la carpeta YA
    # existia (sin ese parametro, intentar crear una carpeta que ya
    # existe lanzaria una excepcion).
    os.makedirs(CARPETA_PERFILES, exist_ok=True)

    # "os.path.splitext(ruta_origen)" separa una ruta de archivo en 2
    # partes: el nombre y la extension. Por ejemplo,
    # "C:/fotos/mia.jpg" se separa en ("C:/fotos/mia", ".jpg"). Al
    # poner "[1]" nos quedamos solo con la segunda parte (la
    # extension, con todo y el punto). "or '.png'" es un respaldo por
    # si el archivo elegido no tuviera ninguna extension reconocible.
    extension = os.path.splitext(ruta_origen)[1] or ".png"

    # "uuid.uuid4()" genera un identificador aleatorio unico.
    # ".hex" lo convierte a una cadena de texto hexadecimal (solo
    # numeros y letras de la a a la f), algo como
    # "a1b2c3d4e5f6...". Se le pega la extension al final para
    # armar el nombre final del archivo, por ejemplo:
    # "a1b2c3d4e5f6....jpg". Asi, aunque 2 usuarios distintos suban
    # una foto llamada "perfil.jpg" cada uno, nunca se van a pisar
    # entre si en el disco.
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"

    # Se arma la ruta COMPLETA (absoluta) de donde va a quedar
    # guardada la copia, dentro de la carpeta de perfiles.
    ruta_destino_absoluta = os.path.join(CARPETA_PERFILES, nombre_archivo)

    # "shutil.copy(origen, destino)" hace la copia real del archivo:
    # toma la imagen de donde sea que el usuario la eligio en su
    # computadora (puede estar en Descargas, Escritorio, donde sea), y
    # la duplica dentro de la carpeta del proyecto. El archivo
    # ORIGINAL se queda intacto donde estaba; solo se hace una copia.
    shutil.copy(ruta_origen, ruta_destino_absoluta)

    # Se guarda relativa para que el proyecto siga funcionando aunque
    # se copie a otra computadora en otra carpeta.
    # Se devuelve la ruta RELATIVA (ej. "recursos/imagenes/perfiles/
    # a1b2c3...jpg"), NO la ruta absoluta completa (que incluiria algo
    # como "C:/Users/Sergio/Desktop/gogym_app/..."). Esto es
    # importante: si guardaramos la ruta absoluta en la base de datos,
    # la app dejaria de encontrar las fotos en cuanto se copiara el
    # proyecto a otra computadora (donde la ruta absoluta seria
    # distinta).
    return os.path.join("recursos", "imagenes", "perfiles", nombre_archivo)


def _recortar_en_circulo(imagen, tamanio):
    """Recorta cualquier imagen rectangular para que se vea como un
    circulo perfecto (usando una mascara de transparencia)."""
    # Primero se cambia el tamanio de la imagen al que se pidio, y se
    # convierte a modo "RGBA" (Rojo, Verde, Azul, y un cuarto canal
    # llamado "Alpha" que controla la TRANSPARENCIA de cada pixel).
    # Sin este canal Alpha, no seria posible hacer que las esquinas se
    # vean "invisibles" en vez de blancas o negras.
    imagen = imagen.resize(tamanio).convert("RGBA")

    # Se crea una "mascara": una imagen en blanco y negro (modo "L" =
    # escala de grises, un solo canal) del mismo tamanio, TODA NEGRA
    # (el "0" al final significa "negro" en escala de grises, que va
    # de 0=negro a 255=blanco). Esta mascara sera el "molde" de
    # recorte.
    mascara = Image.new("L", tamanio, 0)

    # "ImageDraw.Draw(mascara)" prepara la mascara para poder dibujar
    # sobre ella. ".ellipse(...)" dibuja un OVALO (o circulo, si el
    # ancho y alto son iguales) DENTRO de las coordenadas dadas
    # (0, 0) hasta (ancho, alto) -osea, ocupando toda la imagen-,
    # relleno ("fill=255") de color BLANCO. Al final, la mascara queda
    # con un circulo blanco sobre un fondo negro.
    ImageDraw.Draw(mascara).ellipse((0, 0, tamanio[0], tamanio[1]), fill=255)

    # ".putalpha(mascara)" es el paso clave: le dice a la imagen
    # original "usa esta mascara como tu canal de transparencia". Como
    # la mascara tiene un circulo blanco (255 = totalmente visible)
    # sobre fondo negro (0 = totalmente transparente), el resultado es
    # que SOLO la parte circular de la imagen original queda visible;
    # las 4 esquinas se vuelven transparentes.
    imagen.putalpha(mascara)
    return imagen


def cargar_foto_circular(ruta_relativa, tamanio=(60, 60)):
    """
    Carga la foto de perfil guardada en la base de datos y la devuelve
    lista para mostrarse en un CTkLabel (recortada en circulo).

    Devuelve None si no hay foto guardada o si el archivo ya no existe
    en el disco, para que quien la use pueda mostrar un circulo gris
    de respaldo en su lugar (ver utilidades/componentes.py, funcion
    crear_avatar).
    """
    # Si "ruta_relativa" viene vacia, None, o cualquier valor "falso"
    # de Python, no tiene caso ni intentar buscar el archivo: se
    # devuelve None de inmediato.
    if not ruta_relativa:
        return None

    # Se convierte la ruta relativa (guardada en la base de datos) a
    # una ruta absoluta real en ESTA computadora, uniendola con la
    # carpeta base del proyecto.
    ruta_completa = os.path.join(CARPETA_BASE, ruta_relativa)
    if not os.path.exists(ruta_completa):
        # Si el archivo ya no existe fisicamente (por ejemplo, alguien
        # lo borro a mano de la carpeta), tambien se devuelve None, en
        # vez de tronar al intentar abrir un archivo que no esta.
        return None

    try:
        imagen = Image.open(ruta_completa)
        # Se manda a recortar en circulo usando la funcion de arriba.
        imagen_circular = _recortar_en_circulo(imagen, tamanio)
        # Se envuelve el resultado en un CTkImage (el formato que
        # customtkinter necesita para poder mostrar imagenes en sus
        # widgets), lista para usarse directo en un CTkLabel.
        return ctk.CTkImage(light_image=imagen_circular, dark_image=imagen_circular, size=tamanio)
    except Exception as e:
        # Si el archivo existe pero esta corrupto, o no es una imagen
        # valida a pesar de su extension, se atrapa el error para no
        # tronar la app, y se avisa por consola.
        print("Error al cargar la foto de perfil:", e)
        return None
"""
Reproductor de animaciones (GIF) de los ejercicios.

Responsabilidad Unica: este archivo SOLO sabe cargar un archivo GIF y
reproducirlo en bucle dentro de un CTkLabel. No sabe nada de MySQL ni
de rutinas; la ruta del GIF se la pasa quien lo use (viene de
ejercicio.animacion_ejercicio, leida por alumno_modelo.py).
"""
import os
import customtkinter as ctk

# "Image" es la clase de Pillow para abrir cualquier tipo de imagen
# (png, jpg, gif, etc). "ImageSequence" es una herramienta especial de
# Pillow, especifica para trabajar con imagenes que tienen VARIOS
# cuadros dentro del mismo archivo, como los GIF animados.
from PIL import Image, ImageSequence

# Carpeta raiz del proyecto (2 niveles arriba: utilidades/ -> gogym_app/).
# Se usa para poder armar la ruta COMPLETA del archivo GIF a partir de
# la ruta RELATIVA que viene guardada en la base de datos (ej.
# "recursos/imagenes/ejercicios/PEC-CASA-01.gif").
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cargar_cuadros_gif(ruta_relativa, tamanio):
    """Abre el archivo GIF y separa todos sus cuadros (frames) en una
    lista de CTkImage, junto con cuanto dura cada uno en pantalla.
    Devuelve None si el archivo no existe o no se pudo leer."""
    # Se une la carpeta base del proyecto con la ruta relativa que
    # viene de la base de datos, para obtener la ruta REAL en el disco
    # de esta computadora (que puede ser distinta en cada maquina
    # donde corra el proyecto).
    ruta_completa = os.path.join(CARPETA_BASE, ruta_relativa)
    if not os.path.exists(ruta_completa):
        # Si el archivo no existe (por ejemplo, el profesional aun no
        # ha subido ese GIF), se devuelve None de inmediato, sin
        # intentar abrirlo (eso evitaria un error mas feo mas abajo).
        return None

    try:
        # Image.open() abre el archivo, pero OJO: un GIF animado, por
        # dentro, es un solo archivo que contiene VARIAS imagenes
        # (cuadros) una detras de otra. Al abrirlo asi, Pillow solo
        # "ve" el primer cuadro por defecto.
        imagen_gif = Image.open(ruta_completa)
        cuadros = []       # aqui se van a guardar las imagenes ya listas para CTk
        duraciones = []    # aqui se guarda cuanto tiempo dura cada cuadro en pantalla

        # "ImageSequence.Iterator(imagen_gif)" es lo que permite
        # RECORRER, uno por uno, TODOS los cuadros que tiene el GIF por
        # dentro (como si fuera una lista de imagenes), en vez de
        # quedarse solo con el primero.
        for cuadro in ImageSequence.Iterator(imagen_gif):
            # ".convert('RGBA')" asegura que la imagen tenga canal de
            # transparencia (Alpha) en un formato consistente (algunos
            # GIF vienen en modos de color raros que dan problemas al
            # mostrarse). ".resize(tamanio)" ajusta el cuadro al
            # tamanio que se le pidio a la funcion (ej. 260x260).
            cuadro_rgba = cuadro.convert("RGBA").resize(tamanio)

            # "ctk.CTkImage(...)" es el tipo de imagen que entienden
            # los widgets de customtkinter (no se les puede poner una
            # imagen de Pillow directamente, hay que "envolverla" en
            # este objeto). "light_image" y "dark_image" se ponen
            # iguales porque esta imagen no necesita cambiar entre modo
            # claro/oscuro.
            cuadros.append(
                ctk.CTkImage(light_image=cuadro_rgba, dark_image=cuadro_rgba, size=tamanio)
            )

            # Cada cuadro de un GIF trae guardada, dentro de su propia
            # informacion ("cuadro.info"), la duracion en milisegundos
            # que debe mostrarse antes de pasar al siguiente. Se usa
            # ".get('duration', 100)" para tomar ese valor, o usar 100
            # milisegundos como respaldo si el GIF no trajera esa
            # informacion por alguna razon.
            duraciones.append(cuadro.info.get("duration", 100))

        # Se devuelven las 2 listas juntas, como una TUPLA (cuadros,
        # duraciones). Quien llame a esta funcion las recibe asi:
        # "cuadros, duraciones = _cargar_cuadros_gif(...)".
        return cuadros, duraciones
    except Exception as e:
        # Si algo sale mal al abrir o procesar el archivo (por ejemplo,
        # el archivo esta corrupto, o no es realmente un GIF valido a
        # pesar de tener esa extension), se atrapa el error para que
        # no tumbe toda la aplicacion, y se avisa por consola.
        print("Error al cargar la animacion:", e)
        return None


def crear_reproductor_gif(parent, ruta_gif, tamanio=(260, 260)):
    """
    Crea un CTkLabel que reproduce el GIF indicado EN BUCLE (se repite
    para siempre mientras la ventana este abierta).

    Si no hay ruta guardada, o el archivo no existe todavia (por
    ejemplo, si aun no se ha subido esa animacion), se muestra un
    mensaje de texto en su lugar, en vez de tronar.
    """
    # "if ruta_gif else None" cubre el caso en que ni siquiera venga
    # una ruta (por ejemplo, un ejercicio que nunca tuvo animacion
    # asignada en la base de datos, con animacion_ejercicio = NULL).
    resultado = _cargar_cuadros_gif(ruta_gif, tamanio) if ruta_gif else None

    if resultado is None:
        # Si no se pudo cargar la animacion (por cualquier motivo:
        # sin ruta, archivo faltante, o archivo corrupto), se devuelve
        # una etiqueta de texto explicando la situacion, en vez de
        # dejar un espacio vacio sin explicacion o tronar el programa.
        return ctk.CTkLabel(
            parent, text="Animacion no disponible para este ejercicio",
            text_color="gray", width=tamanio[0], height=tamanio[1],
        )

    # Si SI se pudo cargar, se desempaqueta la tupla en sus 2 partes.
    cuadros, duraciones = resultado

    # Se crea una etiqueta (CTkLabel) vacia, que ira mostrando los
    # cuadros del GIF uno tras otro.
    etiqueta = ctk.CTkLabel(parent, text="")

    # Estas 2 lineas hacen algo un poco especial: le estan agregando
    # ATRIBUTOS NUEVOS al objeto "etiqueta" (que normalmente solo
    # tendria los atributos que trae CTkLabel por defecto). Python
    # permite esto libremente. Se hace por 2 razones:
    #   1. "_cuadros_gif": si no se guardara la lista de cuadros en
    #      algun lado que "sobreviva", Python la borraria de memoria
    #      en cuanto la funcion crear_reproductor_gif() terminara de
    #      correr, y la animacion dejaria de funcionar casi de
    #      inmediato (las imagenes desaparecerian).
    #   2. "_indice_actual": es un CONTADOR que recuerda "en que cuadro
    #      vamos" cada vez que se llama a la funcion de abajo.
    etiqueta._cuadros_gif = cuadros
    etiqueta._indice_actual = 0

    # Esta es una FUNCION ANIDADA (una funcion definida DENTRO de otra
    # funcion). Se define aqui adentro para que tenga acceso directo a
    # las variables "etiqueta", "cuadros" y "duraciones" de su
    # alrededor, sin tener que pasarlas como parametros cada vez.
    def _mostrar_siguiente_cuadro():
        # "etiqueta.winfo_exists()" pregunta si ese widget SIGUE
        # existiendo de verdad en la pantalla (no fue destruido). Esto
        # es MUY importante: si el usuario cierra la ventana de la
        # animacion, este chequeo evita que el programa siga
        # intentando actualizar una imagen que ya no existe (lo cual
        # causaria un error).
        if not etiqueta.winfo_exists():
            return

        # Se toma el indice actual (en que cuadro vamos), se le pone
        # esa imagen a la etiqueta, y se calcula cual sera el
        # SIGUIENTE indice.
        indice = etiqueta._indice_actual
        etiqueta.configure(image=cuadros[indice])

        # "(indice + 1) % len(cuadros)" es la formula clasica para
        # hacer un CICLO que se repite para siempre: el simbolo "%" es
        # el "modulo" (el residuo de una division). Cuando "indice + 1"
        # llega al final de la lista, el modulo lo regresa a 0 en vez
        # de dejarlo seguir creciendo. Ejemplo con 5 cuadros: 0,1,2,3,4,
        # 0,1,2,3,4,0... (nunca llega a "5", porque 5 % 5 = 0).
        etiqueta._indice_actual = (indice + 1) % len(cuadros)

        # "etiqueta.after(milisegundos, funcion)" es un metodo de
        # tkinter que dice "despues de tantos milisegundos, vuelve a
        # llamar a esta funcion". Aqui se usa para llamarse A SI MISMA
        # despues de esperar la duracion de este cuadro (esto se llama
        # RECURSION mediante el "reloj" de tkinter, y es la forma
        # estandar de hacer animaciones en tkinter/customtkinter, ya
        # que no existe un "while True" que espere sin congelar toda
        # la ventana).
        etiqueta.after(duraciones[indice] or 100, _mostrar_siguiente_cuadro)

    # Se llama UNA VEZ a la funcion de arriba, para "arrancar" el
    # primer cuadro. A partir de ahi, ella sola se sigue reprogramando
    # una y otra vez usando .after(), sin que nadie mas tenga que
    # llamarla de nuevo.
    _mostrar_siguiente_cuadro()

    # Se devuelve la etiqueta ya lista (con la animacion corriendo por
    # dentro), para que quien llamo a crear_reproductor_gif() solo
    # tenga que hacer ".pack()" con ella, como con cualquier otro
    # widget normal.
    return etiqueta
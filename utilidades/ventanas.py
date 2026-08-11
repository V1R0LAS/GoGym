"""
Icono de las ventanas de la app.

Responsabilidad Unica: este archivo SOLO sabe poner el logo de GoGym
como icono de una ventana. Se usa tanto para la ventana principal como
para cualquier ventana emergente (CTkToplevel), para que ninguna se
quede con el icono por defecto (la "pluma" de tkinter, o el icono azul
generico de Windows).

Por que se genera un .ico: en Windows, iconphoto() con un .png SOLO
cambia el icono chico de la esquina de la ventana; la barra de tareas
sigue mostrando el icono por defecto. La forma confiable de cambiar
TAMBIEN la barra de tareas es con iconbitmap() usando un archivo .ico
de verdad. Como el proyecto solo trae logo.png, aqui se genera
automaticamente un logo.ico (una sola vez) a partir de esa imagen,
usando Pillow (que ya es una dependencia del proyecto).
"""
import os

# "PhotoImage" es la clase de tkinter (la libreria BASE, no
# customtkinter) que permite cargar imagenes simples como iconos de
# ventana. Se usa aqui como RESPALDO, para sistemas que no son
# Windows (Mac/Linux), donde el metodo con .ico no aplica igual.
from tkinter import PhotoImage
from PIL import Image

# Carpeta raiz del proyecto (2 niveles arriba: utilidades/ -> gogym_app/).
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas a las 2 versiones del logo: la original en PNG (que ya trae el
# proyecto), y la version en formato ICO (que se genera automaticamente
# la primera vez que hace falta, y luego queda guardada en disco para
# las siguientes veces).
RUTA_LOGO_PNG = os.path.join(CARPETA_BASE, "recursos", "imagenes", "logo.png")
RUTA_LOGO_ICO = os.path.join(CARPETA_BASE, "recursos", "imagenes", "logo.ico")

# --- Variables "de modulo" (viven fuera de cualquier funcion) ---
# Estas 2 variables actuan como una "memoria compartida" entre todas
# las llamadas a las funciones de este archivo, mientras el programa
# este corriendo:
#
# "_icono_photo" guarda la imagen PNG ya cargada, para no tener que
# volver a leerla del disco cada vez que se abre una ventana nueva
# (se carga una sola vez, y se reutiliza).
_icono_photo = None

# "_ya_se_intento_generar_ico" es una "bandera" (flag): empieza en
# False, y se pone en True la primera vez que se intenta generar el
# archivo .ico, para asegurarse de que ese intento SOLO se haga una
# vez por cada vez que se ejecuta el programa (no tiene caso volver a
# intentarlo en cada ventana nueva que se abra).
_ya_se_intento_generar_ico = False


def _generar_ico_si_hace_falta():
    """Convierte logo.png a logo.ico la primera vez que se necesita.
    Si ya existe el .ico, o no hay logo.png, no hace nada."""
    # "global _ya_se_intento_generar_ico" es OBLIGATORIO aqui: sin
    # esta linea, si dentro de la funcion se escribiera
    # "_ya_se_intento_generar_ico = True", Python crearia una variable
    # NUEVA y LOCAL con ese mismo nombre, solo valida dentro de esta
    # funcion, en vez de modificar la variable de modulo de arriba.
    # "global" le dice a Python "quiero modificar ESA variable de
    # afuera, no crear una nueva aqui adentro".
    global _ya_se_intento_generar_ico

    # Si ya se intento antes (sin importar si funciono o no), no se
    # vuelve a intentar: se sale de la funcion de inmediato.
    if _ya_se_intento_generar_ico:
        return
    _ya_se_intento_generar_ico = True

    # Si el archivo .ico YA existe (de una ejecucion anterior del
    # programa), o si ni siquiera existe el logo.png original (no hay
    # nada de donde generar el .ico), no hay nada que hacer.
    if os.path.exists(RUTA_LOGO_ICO) or not os.path.exists(RUTA_LOGO_PNG):
        return

    try:
        # Se abre el logo.png y se convierte a modo "RGBA" (necesario
        # para que el .ico soporte transparencia correctamente).
        imagen = Image.open(RUTA_LOGO_PNG).convert("RGBA")

        # ".save(ruta, format='ICO', sizes=[...])" es una funcion de
        # Pillow que sabe escribir el formato .ico especificamente.
        # El parametro "sizes" es una lista de TUPLAS (ancho, alto):
        # un archivo .ico, a diferencia de un .png normal, puede
        # contener VARIAS versiones de la misma imagen en distintos
        # tamanios DENTRO DEL MISMO ARCHIVO. Esto es asi porque
        # Windows usa un tamanio distinto segun donde se muestre el
        # icono (16x16 para la barra de titulo chica, 256x256 para
        # cuando se ve el icono grande en el explorador de archivos,
        # etc.), y Pillow genera automaticamente cada version
        # redimensionada a partir de la imagen original.
        imagen.save(
            RUTA_LOGO_ICO, format="ICO",
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        )
    except Exception as e:
        print("No se pudo generar logo.ico a partir de logo.png:", e)


def aplicar_icono(ventana):
    """
    Pone el logo de GoGym como icono de 'ventana' (barra de titulo Y,
    en Windows, tambien la barra de tareas).

    Se debe llamar justo despues de crear cualquier CTk() o
    CTkToplevel() de la app.
    """
    # Primero se asegura de que el .ico exista (lo genera si hace
    # falta; si ya se genero antes, esta llamada no hace nada gracias
    # a la bandera de arriba).
    _generar_ico_si_hace_falta()

    # "os.name" es una variable de la libreria estandar de Python que
    # dice en que TIPO de sistema operativo esta corriendo el
    # programa: "nt" significa Windows ("NT" viene de "Windows NT",
    # el nombre tecnico de la familia de Windows modernos); en
    # Mac/Linux, "os.name" valdria "posix".
    if os.name == "nt" and os.path.exists(RUTA_LOGO_ICO):
        try:
            # "ventana.iconbitmap(ruta)" es el metodo que SI logra
            # cambiar el icono tanto de la ventana como de la barra de
            # tareas en Windows, usando el archivo .ico.
            ventana.iconbitmap(RUTA_LOGO_ICO)

            # "ventana.after(200, funcion)" programa que, 200
            # milisegundos despues, se vuelva a ejecutar
            # "ventana.iconbitmap(...)" una segunda vez. Esto es un
            # "parche" para un comportamiento raro de Windows: en
            # algunas ventanas emergentes (CTkToplevel), Windows pone
            # su propio icono por defecto una fraccion de segundo
            # DESPUES de que la ventana ya se creo, sobreescribiendo el
            # que nosotros pusimos. Al volver a aplicarlo un poquito
            # despues, nos aseguramos de que el logo de GoGym se quede
            # como el definitivo.
            ventana.after(200, lambda: ventana.iconbitmap(RUTA_LOGO_ICO))

            # "return" aqui es importante: si ya se logro poner el
            # icono con el metodo de Windows, NO hace falta seguir
            # ejecutando el codigo de abajo (el respaldo con PNG).
            return
        except Exception as e:
            print("No se pudo poner el icono .ico:", e)
            # OJO: si esto falla, el codigo SIGUE corriendo hacia
            # abajo (no hay return aqui), y se intenta el respaldo con
            # PNG como ultima opcion.

    # --- Respaldo (Mac/Linux, o si el .ico fallo) ---
    global _icono_photo
    if not os.path.exists(RUTA_LOGO_PNG):
        return
    try:
        # Solo se carga el PNG UNA VEZ (si "_icono_photo" ya tiene algo
        # guardado de una llamada anterior, no se vuelve a leer el
        # archivo del disco).
        if _icono_photo is None:
            _icono_photo = PhotoImage(file=RUTA_LOGO_PNG)

        # "iconphoto(False, imagen)" pone esa imagen como icono de
        # ESTA ventana especifica. El primer parametro (False) le dice
        # a tkinter "aplica esto SOLO a esta ventana, no a todas las
        # ventanas futuras que se abran" (si fuera True, se aplicaria
        # tambien como icono por defecto para cualquier ventana nueva
        # que se cree despues, sin necesidad de llamarla de nuevo).
        ventana.iconphoto(False, _icono_photo)
    except Exception as e:
        print("No se pudo poner el icono de la ventana:", e)
"""
Piezas visuales pequenias que se repiten en varias pantallas de la app
(la barra roja de titulo, las tarjetas de metricas, el avatar de foto
de perfil). Tenerlas aqui evita copiar y pegar el mismo codigo en cada
vista (principio DRY / SRP).
"""
import customtkinter as ctk
from utilidades.estilos import COLOR_ROJO
from utilidades.imagenes import cargar_foto_circular


def crear_encabezado(parent, titulo):
    """Crea la barra roja de titulo que aparece arriba de cada pantalla
    (Inicio, Mis Rutinas, etc.), con el texto del titulo en blanco."""
    # "parent" es el widget DENTRO del cual se va a meter este
    # encabezado (normalmente, la vista completa que lo esta llamando).
    # "height=60" le fija una altura de 60 pixeles a la barra roja.
    encabezado = ctk.CTkFrame(parent, fg_color=COLOR_ROJO, corner_radius=0, height=60)
    encabezado.pack(fill="x")

    # "pack_propagate(False)" es MUY importante aqui: por defecto, un
    # CTkFrame se AJUSTA automaticamente al tamanio de lo que tenga
    # adentro (a esto se le llama "propagar" el tamanio). Si no se
    # pusiera esta linea, la barra roja se encogeria hasta el tamanio
    # exacto del texto de adentro, ignorando el "height=60" que le
    # dimos arriba. Con "propagate(False)", se le dice "quedate con EL
    # TAMANIO QUE TE DI, sin importar lo que tengas adentro".
    encabezado.pack_propagate(False)

    ctk.CTkLabel(
        encabezado, text=titulo, text_color="white",
        font=ctk.CTkFont(size=16, weight="bold"),
    ).pack(side="left", padx=20, pady=15)

    # Se devuelve el encabezado ya armado, por si quien lo uso quiere
    # hacer algo mas con el (aunque casi siempre solo se llama la
    # funcion y no se guarda lo que devuelve, porque ya quedo
    # "pegado" en pantalla con el .pack() de arriba).
    return encabezado


def crear_tarjeta_metrica(parent, etiqueta, valor, subtexto=None, ancho=None):
    """
    Crea una tarjeta blanca con borde: una etiqueta chica arriba y un
    valor grande abajo. Ejemplo: etiqueta='Peso Actual', valor='68.5kg'.

    'ancho' es opcional: si se pasa, todas las tarjetas de una misma
    fila quedan del mismo tamanio (ancho Y alto), en vez de que cada
    una mida distinto segun el largo de su texto.

    OJO: esta funcion NO acomoda la tarjeta en la pantalla (no hace pack),
    eso lo decide quien la use, para poder ponerlas una junto a otra.
    """
    # Esta linea arma un DICCIONARIO de argumentos EXTRA solo si se
    # paso un "ancho". Si "ancho" es None (no se especifico), el
    # diccionario queda vacio ({}). Se hace asi porque CTkFrame NO
    # acepta que se le mande "width=None" directamente (eso causaria un
    # error); asi que en vez de eso, simplemente NO SE MANDA el
    # argumento "width" para nada cuando no hace falta.
    kwargs_tamanio = {"width": ancho, "height": 95} if ancho else {}

    # El "**kwargs_tamanio" al final "desempaqueta" ese diccionario
    # como si fueran argumentos escritos a mano (ej. si
    # kwargs_tamanio = {"width": 170, "height": 95}, esto equivale a
    # escribir "width=170, height=95" directo aqui).
    tarjeta = ctk.CTkFrame(parent, fg_color="white", corner_radius=10,
                           border_width=1, border_color="#E5E5E5", **kwargs_tamanio)

    # Igual que en crear_encabezado: si se le dio un ancho fijo, se
    # evita que la tarjeta cambie de tamanio segun su contenido.
    if ancho:
        tarjeta.pack_propagate(False)

    ctk.CTkLabel(tarjeta, text=etiqueta, text_color="gray",
                 font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(10, 0))

    # El espacio de abajo del "valor" cambia dependiendo de si va a
    # venir un subtexto despues o no: si SI hay subtexto, se deja poco
    # espacio (4) para que quede pegado a el; si NO hay subtexto, se
    # deja mas espacio (10) para que la tarjeta no se vea apachurrada
    # en la parte de abajo.
    espacio_abajo = 4 if subtexto else 10
    ctk.CTkLabel(tarjeta, text=valor, text_color="black",
                 font=ctk.CTkFont(size=18, weight="bold")).pack(
        anchor="w", padx=15, pady=(0, espacio_abajo))

    # El subtexto (por ejemplo, "Rango Normal" debajo del numero del
    # IMC) solo se dibuja SI se paso algo en ese parametro (por
    # defecto es None, y "if subtexto:" es Falso cuando subtexto es
    # None o una cadena vacia).
    if subtexto:
        ctk.CTkLabel(tarjeta, text=subtexto, text_color="gray",
                     font=ctk.CTkFont(size=10)).pack(anchor="w", padx=15, pady=(0, 10))

    return tarjeta


def crear_avatar(parent, nombre_completo, ruta_foto=None, tamanio=48):
    """
    Muestra la foto de perfil del usuario dentro de un circulo. Si no
    tiene foto guardada (o el archivo no se encuentra), muestra en su
    lugar un circulo gris neutro (sin iniciales ni color), para que la
    pantalla nunca se vea con un hueco vacio.

    Devuelve una tupla (widget, imagen): "imagen" hay que guardarla en
    una variable de la vista que la usa (por ejemplo self._avatar_img),
    porque si nadie la referencia, Python la borra de memoria y la foto
    desaparece de la pantalla.
    """
    # Le pide a utilidades/imagenes.py que cargue la foto y la recorte
    # en circulo, PERO solo si de verdad hay una "ruta_foto" (si viene
    # vacia o None, ni siquiera se intenta cargar nada).
    imagen = cargar_foto_circular(ruta_foto, (tamanio, tamanio)) if ruta_foto else None

    if imagen is not None:
        # Si SI se pudo cargar una imagen real, se crea una etiqueta
        # (CTkLabel) que muestra esa imagen en vez de texto ("text=''"
        # la deja sin ningun texto visible).
        widget = ctk.CTkLabel(parent, image=imagen, text="")

        # Se devuelven AMBAS cosas: el widget (para poder hacer
        # .pack() con el) y la imagen (para que quien llamo a esta
        # funcion la guarde en una variable propia, como explica el
        # docstring de arriba, y asi Python no la borre de memoria por
        # accidente).
        return widget, imagen

    # --- Respaldo: circulo gris neutro, cuando no hay foto ---
    # Si no hubo imagen (ya sea porque no habia ruta, o el archivo no
    # se encontro en el disco), se crea un CTkLabel SIN imagen ni
    # texto, pero con un color de fondo gris y "corner_radius" igual a
    # la mitad de su tamanio (esa es la formula para que un cuadrado
    # se vea como un circulo PERFECTO: si mide 48x48, el radio de las
    # esquinas debe ser 24, la mitad).
    widget = ctk.CTkLabel(
        parent, text="", fg_color="#D9D9D9",
        corner_radius=tamanio // 2, width=tamanio, height=tamanio,
    )
    # En este caso se devuelve None en el lugar de la imagen (porque
    # no hay ninguna imagen real que "proteger" de la basura de
    # Python), pero se mantiene la MISMA FORMA de tupla (widget, algo)
    # para que quien use esta funcion pueda escribir siempre el mismo
    # patron: "widget_avatar, self._imagen_avatar = crear_avatar(...)",
    # sin tener que revisar casos distintos segun si hubo foto o no.
    return widget, None
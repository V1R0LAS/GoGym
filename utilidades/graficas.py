"""
Grafica de progreso de peso, reutilizable.

Por que este archivo existe (evita repetir codigo):
Tanto la pantalla de Inicio como la de Mis Metricas necesitan mostrar
la MISMA grafica de peso a lo largo del tiempo. En vez de escribir el
codigo de matplotlib dos veces, lo dejamos en una sola funcion aqui y
la llamamos desde ambas vistas.
"""

# "Figure" es la clase de matplotlib que representa una grafica
# completa "en blanco" (el lienzo donde se va a dibujar todo: ejes,
# lineas, titulos, etc.), antes de que se le agregue nada.
from matplotlib.figure import Figure

# "FigureCanvasTkAgg" es el "puente" entre matplotlib y tkinter: es lo
# que permite tomar una grafica ya dibujada por matplotlib (que por su
# cuenta no sabe nada de tkinter) y convertirla en un WIDGET normal de
# tkinter/customtkinter, que se puede acomodar con .pack() como
# cualquier otro elemento de la interfaz.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Se reutiliza el mismo rojo de marca que usa toda la app, para que la
# linea de la grafica combine con el resto de los colores (en vez de
# usar el azul por defecto de matplotlib).
from utilidades.estilos import COLOR_ROJO


def crear_grafica_peso(contenedor, mediciones):
    """
    Crea y devuelve un widget con una grafica de linea del peso a lo
    largo del tiempo.

    contenedor: el widget (frame) donde se va a colocar la grafica.
    mediciones: lista de diccionarios con "fecha" y "peso" (viene de
                alumno_modelo.obtener_progreso_peso).
    """
    # "Figure(figsize=(5, 3), dpi=100)" crea el "lienzo" de la grafica:
    # figsize=(5, 3) es el tamanio en PULGADAS (5 de ancho, 3 de alto),
    # y dpi=100 es la resolucion (cuantos pixeles representa cada
    # pulgada). Combinados, esta grafica termina midiendo
    # aproximadamente 500x300 pixeles en pantalla.
    figura = Figure(figsize=(5, 3), dpi=100)

    # "add_subplot(111)" agrega un solo "panel" de graficacion dentro
    # de la figura (el numero 111 es una notacion clasica de
    # matplotlib que significa "una cuadricula de 1 fila, 1 columna,
    # y este es el panel numero 1" — para graficas simples con un solo
    # dibujo, siempre se usa 111). "ejes" es el objeto sobre el que se
    # van a dibujar las lineas, puntos, texto, etc.
    ejes = figura.add_subplot(111)

    # Si SI hay mediciones registradas, se dibuja la grafica de verdad.
    if mediciones:
        # Estas son "listas por comprension" (list comprehensions):
        # una forma corta de escribir un ciclo "for" que arma una
        # lista nueva, en una sola linea. Se leen de derecha a
        # izquierda: "por cada 'm' en mediciones, calcula tal cosa, y
        # ponla en la lista".
        #
        # "m['fecha'].strftime('%d/%m')" convierte cada fecha (que
        # viene como objeto date de Python) a un texto corto tipo
        # "02/08" (dia/mes), para que el eje horizontal de la grafica
        # no se vea saturado con fechas completas.
        fechas = [m["fecha"].strftime("%d/%m") for m in mediciones]

        # "float(m['peso'])" convierte cada peso (que puede venir como
        # un tipo especial "Decimal" desde MySQL) a un numero flotante
        # normal de Python, que es lo que matplotlib sabe graficar sin
        # problemas.
        pesos = [float(m["peso"]) for m in mediciones]

        # ".plot(...)" es el metodo que realmente DIBUJA la linea:
        # "fechas" va en el eje horizontal, "pesos" en el vertical,
        # "color=COLOR_ROJO" pinta la linea del rojo de la marca, y
        # "marker='o'" pone un puntito circular en cada medicion real
        # (para que se distinga claramente cada dato, no solo la
        # tendencia general de la linea).
        ejes.plot(fechas, pesos, color=COLOR_ROJO, marker="o")
    else:
        # Si el alumno todavia no tiene mediciones, mostramos un mensaje
        # en vez de una grafica vacia y confusa.
        # ".text(0.5, 0.5, ...)" escribe un texto en el CENTRO exacto
        # del area de la grafica: las coordenadas (0.5, 0.5) no son
        # pixeles, son PROPORCIONES del area total (de 0.0 a 1.0), asi
        # que (0.5, 0.5) siempre es el centro, sin importar el tamanio
        # real de la figura. "ha='center', va='center'" ("horizontal
        # alignment" y "vertical alignment") centran el texto EXACTO
        # sobre ese punto, en vez de que la esquina del texto empiece
        # ahi.
        ejes.text(0.5, 0.5, "Aun no hay mediciones registradas",
                   ha="center", va="center", fontsize=9, color="gray")

        # "set_xticks([])" y "set_yticks([])" quitan las marcas
        # numericas de los ejes (los numeritos que normalmente
        # aparecen junto a los ejes de una grafica), porque no tiene
        # sentido mostrar una escala de numeros si no hay ningun dato
        # que graficar todavia.
        ejes.set_xticks([])
        ejes.set_yticks([])

    # Se pone el fondo del AREA DE DIBUJO (donde va la linea) en
    # blanco...
    ejes.set_facecolor("white")
    # ...y tambien el fondo de TODA la figura (incluyendo los margenes
    # alrededor del area de dibujo), para que combine con el fondo
    # blanco del resto de la aplicacion (por defecto, matplotlib usa un
    # gris clarito que se notaria distinto al resto de la interfaz).
    figura.patch.set_facecolor("white")

    # "tight_layout()" le pide a matplotlib que AJUSTE automaticamente
    # los margenes internos de la grafica, para que las etiquetas de
    # los ejes, titulos, etc. no queden cortados ni con espacios
    # excesivos alrededor.
    figura.tight_layout()

    # Aqui es donde se hace la "conversion" de una grafica de
    # matplotlib a un widget de tkinter: se crea un "lienzo"
    # (FigureCanvasTkAgg) que envuelve la figura ya armada, indicandole
    # que su "master" (el widget padre donde va a vivir) es el
    # "contenedor" que se recibio como parametro.
    lienzo = FigureCanvasTkAgg(figura, master=contenedor)

    # ".draw()" le dice al lienzo que efectivamente RENDERICE (dibuje
    # de verdad, pixel por pixel) todo lo que se configuro arriba. Sin
    # esta linea, el lienzo existiria pero estaria en blanco.
    lienzo.draw()

    # ".get_tk_widget()" es el metodo que finalmente entrega un widget
    # NORMAL de tkinter (algo que se puede acomodar con .pack(), como
    # cualquier CTkFrame o CTkLabel), que por dentro contiene toda la
    # grafica ya dibujada. Esto es lo que se devuelve, para que quien
    # llamo a esta funcion solo tenga que hacer
    # "crear_grafica_peso(...).pack(...)" y ya.
    return lienzo.get_tk_widget()
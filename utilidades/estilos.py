"""
Colores que se usan en toda la aplicacion GoGym.

Por que este archivo existe (principio de Responsabilidad Unica):
en vez de escribir codigos de color como "#C41E24" repetidos en cada
vista, los ponemos UNA sola vez aqui y los importamos donde se necesiten.
Si un dia el cliente pide cambiar el color de marca, solo se edita
este archivo y toda la app se actualiza.
"""

# Los codigos como "#C41E24" son COLORES HEXADECIMALES: la forma
# estandar de escribir colores en programacion web/interfaces
# graficas. El "#" indica que es un color hex, y los 6 caracteres que
# siguen se leen en pares: los primeros 2 son la cantidad de ROJO, los
# siguientes 2 de VERDE, y los ultimos 2 de AZUL (formato "RRGGBB"),
# cada par en un rango de 00 (nada de ese color) a FF (el maximo).

# Rojo principal de la marca GoGym (botones, encabezados, barra lateral).
# Es el color mas usado de toda la app; aparece en fg_color de las
# barras rojas laterales, los encabezados de cada pantalla, y varios
# botones principales.
COLOR_ROJO = "#C41E24"

# Rojo mas oscuro, se usa cuando el mouse pasa encima de un boton
# (hover). Un boton casi siempre necesita 2 tonos del mismo color: uno
# normal, y uno un poco mas oscuro/claro para cuando el mouse esta
# encima, asi el usuario recibe una senial visual de que el boton es
# "clicable".
COLOR_ROJO_OSCURO = "#A5171F"

# Color de texto secundario (por ejemplo, el texto de la version de la
# app, o subtitulos menos importantes que el texto principal). Un gris
# medio, para que se note que es informacion "de fondo", no el
# contenido principal de la pantalla.
COLOR_TEXTO_SECUNDARIO = "#999999"

# Fondo blanco usado en tarjetas y contenedores (por ejemplo, el chip
# blanco con el nombre del usuario dentro de la barra lateral roja).
# Se define como constante en vez de escribir "white" a mano, para
# mantener la misma convencion de que TODOS los colores de marca pasan
# por este archivo (aunque "#FFFFFF" y "white" sean visualmente
# identicos para customtkinter).
COLOR_BLANCO = "#FFFFFF"

# Fondo gris muy claro usado DENTRO de los campos de texto (inputs),
# como los de "Mi Perfil" o el formulario de "Asignar Rutina". Es un
# gris casi blanco, apenas perceptible, para diferenciar visualmente
# un campo editable del fondo blanco puro de la pantalla.
COLOR_FONDO_CAMPO = "#FAFAFA"

# Color del borde/contorno de los campos de texto. Se usa junto con
# COLOR_FONDO_CAMPO en casi todos los CTkEntry del proyecto, para que
# se vea una linea delgada alrededor de cada campo.
COLOR_BORDE = "#DDDDDD"
"""
Menu principal del ADMINISTRADOR: la barra lateral roja (banner, chip
con el texto "Administrador", botones de navegacion, cerrar sesion) +
el area de contenido que cambia segun la opcion elegida.

Responsabilidad Unica: esta clase SOLO arma el menu y decide que vista
de contenido mostrar (igual patron que VistaMenuAlumno). El diseño y
la logica de cada pantalla vive en su propio archivo dentro de
vistas/admin/.
"""
import os
import customtkinter as ctk
from PIL import Image

from utilidades.estilos import COLOR_ROJO, COLOR_ROJO_OSCURO, COLOR_BLANCO

# Se importan las 2 vistas de CONTENIDO que puede mostrar este menu
# (Inicio y Gestion de Usuarios). Este es el UNICO archivo que necesita
# conocerlas a las 2 al mismo tiempo — cada una de esas vistas, por su
# lado, no sabe nada de la otra ni del menu que las contiene.
from vistas.admin.vista_inicio import VistaInicioAdmin
from vistas.admin.vista_gestion_usuarios import VistaGestionUsuarios

CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_BANNER = os.path.join(CARPETA_BASE, "recursos", "imagenes", "banner.png")

# Ancho fijo de la barra lateral roja, en pixeles. Se usa como
# constante para que sea igual en los 3 menus (Alumno, Profesional,
# Administrador), y facil de ajustar en un solo lugar si algun dia se
# quisiera cambiar.
ANCHO_BARRA_LATERAL = 220


class VistaMenuAdmin(ctk.CTkFrame):
    def __init__(self, master, id_usuario, correo, al_cerrar_sesion=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_usuario = id_usuario
        self.correo = correo

        # Callback que "principal.py" le paso a esta vista (en la
        # practica, es el metodo "_cerrar_sesion" de AplicacionGoGym,
        # que borra la sesion guardada y regresa al login). Este menu
        # no sabe nada de sesiones ni de login, solo llama a esta
        # funcion cuando corresponda.
        self.al_cerrar_sesion = al_cerrar_sesion

        self._construir_barra_lateral()

        # "_area_contenido" es el "hueco" donde se va a ir intercambiando
        # cada pantalla (Inicio, Gestion Usuarios), segun el boton que
        # el administrador presione en la barra lateral.
        self._area_contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self._area_contenido.pack(side="left", fill="both", expand=True)

        self.mostrar_inicio()  # pantalla que se ve al entrar

    # -----------------------------------------------------------------
    # Construccion de la barra lateral
    # -----------------------------------------------------------------

    def _construir_barra_lateral(self):
        barra = ctk.CTkFrame(self, fg_color=COLOR_ROJO, corner_radius=0, width=ANCHO_BARRA_LATERAL)
        barra.pack(side="left", fill="y")
        # Mismo truco que ya vimos en crear_encabezado(): sin esto, la
        # barra lateral se encogeria a lo ancho, en vez de mantener
        # SIEMPRE los 220 pixeles que se le pidieron.
        barra.pack_propagate(False)

        imagen_banner = self._cargar_banner()
        if imagen_banner is not None:
            ctk.CTkLabel(barra, image=imagen_banner, text="").pack(pady=(20, 20), padx=20)
            # Se guarda la imagen del banner en "self", por la misma
            # razon de siempre: para que no se borre de memoria y el
            # banner desaparezca de la pantalla.
            self._imagen_banner = imagen_banner

        # El Administrador no tiene tabla propia de nombre (no existe
        # tabla "administrador" en la base de datos), asi que el chip
        # simplemente muestra la palabra "Administrador".
        # Esto es DISTINTO a los menus de Alumno y Profesional, que SI
        # usan crear_avatar() y muestran el nombre real del usuario —
        # aqui, como no hay ningun dato personal que mostrar (ni foto,
        # ni nombre), simplemente se pone un texto fijo.
        chip = ctk.CTkFrame(barra, fg_color=COLOR_BLANCO, corner_radius=20)
        chip.pack(padx=20, pady=(0, 20), fill="x")
        ctk.CTkLabel(
            chip, text="Administrador", text_color="black",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(padx=10, pady=8)

        # Se crean los 2 botones de navegacion, usando el metodo
        # auxiliar _crear_boton_nav (definido abajo) para no repetir
        # los mismos 5 parametros de estilo 2 veces.
        self._crear_boton_nav(barra, "Inicio", self.mostrar_inicio)
        self._crear_boton_nav(barra, "Gestion Usuarios", self.mostrar_gestion_usuarios)

        # Esta etiqueta VACIA es un truco de layout muy usado en
        # tkinter: al ponerle "expand=True, fill='both'", ocupa TODO el
        # espacio vertical que quede libre entre los botones de arriba
        # y el boton de "Cerrar Sesion" de abajo — esto es lo que logra
        # que "Cerrar Sesion" quede pegado hasta el fondo de la barra
        # lateral, sin importar cuantos botones de navegacion haya
        # arriba.
        ctk.CTkLabel(barra, text="", fg_color=COLOR_ROJO).pack(expand=True, fill="both")

        ctk.CTkButton(
            barra, text="Cerrar Sesion", fg_color="transparent", hover_color=COLOR_ROJO_OSCURO,
            anchor="w", text_color="white", command=self._al_cerrar_sesion,
        ).pack(fill="x", padx=10, pady=20)

    def _crear_boton_nav(self, barra, texto, comando):
        """Crea un boton de la barra lateral con el estilo comun a
        todos (fondo transparente que se pone rojo oscuro al pasar el
        mouse, texto blanco alineado a la izquierda)."""
        ctk.CTkButton(
            barra, text=texto, fg_color="transparent", hover_color=COLOR_ROJO_OSCURO,
            anchor="w", text_color="white", command=comando,
        ).pack(fill="x", padx=10, pady=2)

    def _cargar_banner(self, tamanio=(150, 40)):
        """Carga recursos/imagenes/banner.png. Devuelve None si no existe."""
        if not os.path.exists(RUTA_BANNER):
            print("banner.png no encontrado en:", RUTA_BANNER)
            return None
        try:
            imagen = Image.open(RUTA_BANNER)
            return ctk.CTkImage(light_image=imagen, dark_image=imagen, size=tamanio)
        except Exception as e:
            print("Error al cargar banner:", e)
            return None

    # -----------------------------------------------------------------
    # Cambio entre pantallas
    # -----------------------------------------------------------------

    def _limpiar_area_contenido(self):
        """Borra lo que se este mostrando actualmente en el area de
        contenido, antes de dibujar la nueva pantalla."""
        for widget in self._area_contenido.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self._limpiar_area_contenido()
        VistaInicioAdmin(self._area_contenido).pack(fill="both", expand=True)

    def mostrar_gestion_usuarios(self):
        self._limpiar_area_contenido()
        VistaGestionUsuarios(self._area_contenido).pack(fill="both", expand=True)

    def _al_cerrar_sesion(self):
        if self.al_cerrar_sesion:
            self.al_cerrar_sesion()
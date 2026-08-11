"""
Vista de Login.

Por que esta clase existe (Responsabilidad Unica):
VistaLogin SOLO se encarga de mostrar la pantalla de login (dibujar
los campos, el boton, el logo) y de reaccionar cuando el usuario
presiona "Iniciar". No sabe nada de MySQL ni de como se valida el
login por dentro; eso se lo pregunta al modelo (usuario_modelo.py).
Esto es Inversion de Dependencias: la vista depende de una funcion
(validar_login) y no de los detalles de la base de datos.

Incluye 2 elementos de inclusion/accesibilidad: cambio de idioma
(Espaniol/Ingles) y un Aviso de Privacidad visible antes de iniciar
sesion.
"""
import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from utilidades.estilos import COLOR_ROJO, COLOR_ROJO_OSCURO, COLOR_TEXTO_SECUNDARIO
from utilidades.idiomas import obtener_texto, cambiar_idioma, idioma_contrario
from utilidades.ventanas import aplicar_icono
from configuracion import VERSION_APP
from modelos.usuario_modelo import validar_login

CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_LOGO = os.path.join(CARPETA_BASE, "recursos", "imagenes", "logo.png")

ANCHO_CAMPO = 300


class VistaLogin(ctk.CTkFrame):
    """Pantalla de inicio de sesion. Hereda de CTkFrame para poder
    "vivir" dentro de la ventana principal como cualquier otro widget."""

    def __init__(self, master, al_iniciar_sesion=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.al_iniciar_sesion = al_iniciar_sesion
        self._construir_interfaz()

    def _cargar_logo(self, tamanio):
        if not os.path.exists(RUTA_LOGO):
            print("logo.png no encontrado en:", RUTA_LOGO)
            return None
        try:
            imagen = Image.open(RUTA_LOGO)
            return ctk.CTkImage(light_image=imagen, dark_image=imagen, size=tamanio)
        except Exception as e:
            print("Error al cargar el logo:", e)
            return None

    def _construir_interfaz(self):
        """Dibuja todos los elementos visuales de la pantalla de login."""

        contenedor = ctk.CTkFrame(
            self, fg_color="white", corner_radius=20,
            border_width=1, border_color="#E5E5E5",
        )
        contenedor.pack(expand=True)

        contenido = ctk.CTkFrame(contenedor, fg_color="white")
        contenido.pack(padx=40, pady=30)

        # --- Boton de cambiar idioma, arriba a la derecha ---
        fila_idioma = ctk.CTkFrame(contenido, fg_color="white")
        fila_idioma.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(
            fila_idioma, text=idioma_contrario().upper(), width=44, height=26,
            fg_color="#E5E5E5", text_color="black", hover_color="#D5D5D5",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._cambiar_idioma,
        ).pack(side="right")

        # --- Logo centrado arriba ---
        self._imagen_logo = self._cargar_logo(tamanio=(90, 90))

        if self._imagen_logo is not None:
            ctk.CTkLabel(contenido, image=self._imagen_logo, text="").pack(pady=(0, 8))
        else:
            marco_logo = ctk.CTkFrame(
                contenido, fg_color=COLOR_ROJO, corner_radius=24, width=90, height=90
            )
            marco_logo.pack(pady=(0, 8))
            marco_logo.pack_propagate(False)
            ctk.CTkLabel(
                marco_logo, text="GYM", text_color="white",
                font=ctk.CTkFont(size=18, weight="bold"),
            ).pack(expand=True)

        ctk.CTkLabel(
            contenido, text="GOGYM", text_color="black",
            font=ctk.CTkFont(family="Impact", size=24),
        ).pack(pady=(0, 25))

        # --- Campo: Correo electronico ---
        ctk.CTkLabel(
            contenido, text=obtener_texto("correo"), text_color="#333333",
            font=ctk.CTkFont(size=12), width=ANCHO_CAMPO, anchor="w",
        ).pack()

        self.campo_correo = ctk.CTkEntry(
            contenido, width=ANCHO_CAMPO, height=40, corner_radius=10,
            border_width=1, border_color="#DDDDDD", fg_color="#FAFAFA",
        )
        self.campo_correo.pack(pady=(4, 14))

        # --- Campo: Contrasenia ---
        ctk.CTkLabel(
            contenido, text=obtener_texto("contrasenia"), text_color="#333333",
            font=ctk.CTkFont(size=12), width=ANCHO_CAMPO, anchor="w",
        ).pack()

        self.campo_contrasenia = ctk.CTkEntry(
            contenido, width=ANCHO_CAMPO, height=40, corner_radius=10,
            border_width=1, border_color="#DDDDDD", fg_color="#FAFAFA", show="*",
        )
        self.campo_contrasenia.pack(pady=(4, 22))

        # --- Boton "Iniciar" ---
        ctk.CTkButton(
            contenido, text=obtener_texto("iniciar"), width=ANCHO_CAMPO, height=42,
            corner_radius=12, fg_color=COLOR_ROJO, hover_color=COLOR_ROJO_OSCURO,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._al_presionar_iniciar,
        ).pack()

        self.campo_contrasenia.bind("<Return>", lambda evento: self._al_presionar_iniciar())

        # --- Aviso de Privacidad ---
        ctk.CTkButton(
            contenido, text=obtener_texto("aviso_privacidad_link"), fg_color="white",
            text_color=COLOR_TEXTO_SECUNDARIO, hover_color="#F5F5F5", corner_radius=0,
            border_width=0, font=ctk.CTkFont(size=11, underline=True),
            command=self._mostrar_aviso_privacidad,
        ).pack(pady=(16, 0))

        # --- Texto de version, hasta abajo ---
        ctk.CTkLabel(
            contenido, text=VERSION_APP, text_color=COLOR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=10),
        ).pack(pady=(4, 0))

    def _cambiar_idioma(self):
        """Se llama al dar clic en el boton ES/EN. Cambia el idioma
        global de la app y vuelve a dibujar esta pantalla con los
        textos ya traducidos."""
        cambiar_idioma(idioma_contrario())
        for widget in self.winfo_children():
            widget.destroy()
        self._construir_interfaz()

    def _mostrar_aviso_privacidad(self):
        """Abre una ventana emergente con el Aviso de Privacidad, en
        el idioma activo en este momento."""
        ventana = ctk.CTkToplevel(self)
        aplicar_icono(ventana)
        ventana.title(obtener_texto("aviso_privacidad_titulo"))
        ventana.geometry("420x320")
        ventana.resizable(False, False)
        ventana.configure(fg_color="white")
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text=obtener_texto("aviso_privacidad_titulo"), text_color="black",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(20, 10), padx=20, anchor="w")

        ctk.CTkLabel(
            ventana, text=obtener_texto("aviso_privacidad_cuerpo"), text_color="#333333",
            font=ctk.CTkFont(size=12), wraplength=380, justify="left", anchor="w",
        ).pack(padx=20, pady=(0, 15), fill="both", expand=True)

        ctk.CTkButton(
            ventana, text="OK", fg_color="black", hover_color="#333333",
            width=100, command=ventana.destroy,
        ).pack(pady=(0, 20))

    def _al_presionar_iniciar(self):
        """Se ejecuta cuando el usuario da clic en 'Iniciar' o presiona Enter."""
        correo = self.campo_correo.get().strip()
        contrasenia = self.campo_contrasenia.get().strip()

        usuario = validar_login(correo, contrasenia)

        if usuario is None:
            messagebox.showerror(
                obtener_texto("error_titulo"),
                obtener_texto("error_mensaje"),
            )
            return

        if self.al_iniciar_sesion:
            self.al_iniciar_sesion(usuario)
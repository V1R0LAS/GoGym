"""
Menu principal del PROFESIONAL: la barra lateral roja (banner, avatar +
nombre, botones de navegacion, cerrar sesion) + el area de contenido
que cambia segun la opcion elegida.

Responsabilidad Unica: esta clase SOLO arma el menu y decide que vista
de contenido mostrar (mismo patron que VistaMenuAlumno y VistaMenuAdmin).
"""
import os
import customtkinter as ctk
from PIL import Image

from utilidades.estilos import COLOR_ROJO, COLOR_ROJO_OSCURO, COLOR_BLANCO
from utilidades.componentes import crear_avatar

# Se importa la funcion del modelo de PROFESIONAL que trae sus datos
# personales (nombre, foto, correo, id_profesional). Es el equivalente
# exacto de "obtener_datos_perfil" que usa VistaMenuAlumno, pero
# apuntando a la tabla "profesional" en vez de "alumno".
from modelos.profesional_modelo import obtener_datos_perfil_profesional

# Se importan las 4 vistas de contenido que puede mostrar este menu:
# Inicio, Mis Alumnos, Detalle de un alumno especifico, y Mi Perfil.
from vistas.profesional.vista_inicio import VistaInicioProfesional
from vistas.profesional.vista_mis_alumnos import VistaMisAlumnos
from vistas.profesional.vista_detalle_alumno import VistaDetalleAlumno
from vistas.profesional.vista_mi_perfil import VistaMiPerfilProfesional

CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_BANNER = os.path.join(CARPETA_BASE, "recursos", "imagenes", "banner.png")

ANCHO_BARRA_LATERAL = 220


class VistaMenuProfesional(ctk.CTkFrame):
    def __init__(self, master, id_usuario, correo, al_cerrar_sesion=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_usuario = id_usuario
        self.correo = correo
        self.al_cerrar_sesion = al_cerrar_sesion

        # Traemos los datos de perfil una vez al entrar, para saber el
        # nombre/foto a mostrar en la barra lateral y el id_profesional
        # a usar en el resto de las consultas.
        # Igual que en el Alumno: se consulta UNA SOLA VEZ aqui, y se
        # reutiliza el resultado en toda la barra lateral, en vez de
        # volver a pedirlo cada vez que se dibuja algo.
        self.datos_perfil = obtener_datos_perfil_profesional(id_usuario) or {}

        # "id_profesional" es el identificador que van a necesitar las
        # 4 pantallas de contenido para saber DE QUIEN traer los
        # alumnos, rutinas, etc. (es distinto de "id_usuario", que solo
        # identifica la cuenta de acceso).
        self.id_profesional = self.datos_perfil.get("id_profesional")

        self._construir_barra_lateral()

        self._area_contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self._area_contenido.pack(side="left", fill="both", expand=True)

        self.mostrar_inicio()

    # -----------------------------------------------------------------
    # Construccion de la barra lateral
    # -----------------------------------------------------------------

    def _construir_barra_lateral(self):
        barra = ctk.CTkFrame(self, fg_color=COLOR_ROJO, corner_radius=0, width=ANCHO_BARRA_LATERAL)
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)

        imagen_banner = self._cargar_banner()
        if imagen_banner is not None:
            ctk.CTkLabel(barra, image=imagen_banner, text="").pack(pady=(20, 20), padx=20)
            self._imagen_banner = imagen_banner

        # --- Chip con foto/avatar + nombre del profesional ---
        # Identico patron al del Alumno: se junta nombre + apellido
        # paterno (sin materno), y se llama a crear_avatar() con la
        # ruta de foto guardada en "datos_perfil".
        nombre_completo = (
            f"{self.datos_perfil.get('nombre', '')} "
            f"{self.datos_perfil.get('ap_paterno', '')}"
        ).strip()

        chip = ctk.CTkFrame(barra, fg_color=COLOR_BLANCO, corner_radius=20)
        chip.pack(padx=20, pady=(0, 20), fill="x")

        widget_avatar, self._imagen_avatar_chip = crear_avatar(
            chip, nombre_completo or self.correo,
            ruta_foto=self.datos_perfil.get("foto"), tamanio=32,
        )
        widget_avatar.pack(side="left", padx=(8, 6), pady=6)

        ctk.CTkLabel(
            chip, text=nombre_completo or self.correo, text_color="black",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 10), pady=8)

        # --- Botones de navegacion: solo 3 (a diferencia de los 4 del Alumno) ---
        # Nota que aqui NO hay boton para "Detalle Alumno" — esa
        # pantalla no se accede desde la barra lateral directamente,
        # solo se llega a ella dando clic en "ver alumno" desde "Mis
        # Alumnos" (ver el metodo mostrar_detalle_alumno mas abajo).
        self._crear_boton_nav(barra, "Inicio", self.mostrar_inicio)
        self._crear_boton_nav(barra, "Mis Alumnos", self.mostrar_mis_alumnos)
        self._crear_boton_nav(barra, "Mi Perfil", self.mostrar_mi_perfil)

        ctk.CTkLabel(barra, text="", fg_color=COLOR_ROJO).pack(expand=True, fill="both")

        ctk.CTkButton(
            barra, text="Cerrar Sesion", fg_color="transparent", hover_color=COLOR_ROJO_OSCURO,
            anchor="w", text_color="white", command=self._al_cerrar_sesion,
        ).pack(fill="x", padx=10, pady=20)

    def _crear_boton_nav(self, barra, texto, comando):
        ctk.CTkButton(
            barra, text=texto, fg_color="transparent", hover_color=COLOR_ROJO_OSCURO,
            anchor="w", text_color="white", command=comando,
        ).pack(fill="x", padx=10, pady=2)

    def _cargar_banner(self, tamanio=(150, 40)):
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
        for widget in self._area_contenido.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self._limpiar_area_contenido()
        VistaInicioProfesional(self._area_contenido, self.id_profesional).pack(fill="both", expand=True)

    def mostrar_mis_alumnos(self):
        self._limpiar_area_contenido()
        # Aqui es donde se conecta el CALLBACK de navegacion: se le
        # pasa a VistaMisAlumnos el metodo "mostrar_detalle_alumno" de
        # ESTA MISMA clase (definido justo abajo), para que lo llame
        # cuando el profesional de clic en "ver alumno". La vista de
        # Mis Alumnos nunca sabe que existe una pantalla de "Detalle
        # Alumno" — solo sabe que debe llamar a la funcion que le
        # dieron, pasandole el id_alumno correspondiente.
        VistaMisAlumnos(
            self._area_contenido, self.id_profesional,
            al_ver_alumno=self.mostrar_detalle_alumno,
        ).pack(fill="both", expand=True)

    def mostrar_detalle_alumno(self, id_alumno):
        """Se llama cuando el profesional da clic en 'ver alumno' desde
        'Mis Alumnos'."""
        self._limpiar_area_contenido()
        # Se le pasa "al_volver=self.mostrar_mis_alumnos": otro
        # callback, esta vez en la direccion CONTRARIA (de "Detalle
        # Alumno" de vuelta hacia "Mis Alumnos"), para el boton de
        # "← Volver a Mis Alumnos" que vimos en vista_detalle_alumno.py.
        VistaDetalleAlumno(
            self._area_contenido, id_alumno, self.id_profesional,
            al_volver=self.mostrar_mis_alumnos,
        ).pack(fill="both", expand=True)

    def mostrar_mi_perfil(self):
        self._limpiar_area_contenido()
        VistaMiPerfilProfesional(
            self._area_contenido, self.id_usuario, self.id_profesional,
            al_guardar=self._refrescar_datos_perfil,
        ).pack(fill="both", expand=True)

    def _refrescar_datos_perfil(self):
        """Cuando el profesional guarda cambios en Mi Perfil (incluida
        la foto), volvemos a cargar sus datos y redibujamos la barra
        lateral para que el chip se actualice de inmediato."""
        # Identico patron al de VistaMenuAlumno: se vuelve a pedir la
        # informacion fresca, se destruye TODA la vista, y se
        # reconstruye desde cero, quedandose en la misma pantalla de
        # Mi Perfil al final.
        self.datos_perfil = obtener_datos_perfil_profesional(self.id_usuario) or {}

        for widget in self.winfo_children():
            widget.destroy()

        self._construir_barra_lateral()

        self._area_contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self._area_contenido.pack(side="left", fill="both", expand=True)

        self.mostrar_mi_perfil()

    def _al_cerrar_sesion(self):
        if self.al_cerrar_sesion:
            self.al_cerrar_sesion()
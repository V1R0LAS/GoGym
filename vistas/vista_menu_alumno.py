"""
Menu principal del ALUMNO: la barra lateral roja (logo, nombre del
usuario, botones de navegacion, cerrar sesion) + el area de contenido
que cambia segun la opcion elegida.

Responsabilidad Unica: esta clase SOLO arma el menu y decide que vista
de contenido mostrar. La logica y el diseño de cada pantalla (Inicio,
Mis Rutinas, Mis Metricas, Mi Perfil) vive en su propio archivo dentro
de vistas/alumno/. Si mañana se agrega una pantalla nueva, solo se crea
su archivo y se agrega un boton aqui; no se toca nada de lo demas
(esto es el principio de Abierto/Cerrado aplicado de forma sencilla).
"""
import os
import customtkinter as ctk
from PIL import Image

from utilidades.estilos import COLOR_ROJO, COLOR_ROJO_OSCURO, COLOR_BLANCO
from utilidades.componentes import crear_avatar
from modelos.usuario_modelo import obtener_datos_perfil

# Se importan las 4 vistas de contenido que puede mostrar este menu.
# Este archivo es el UNICO que necesita conocerlas a las 4 juntas.
from vistas.alumno.vista_inicio import VistaInicioAlumno
from vistas.alumno.vista_mis_rutinas import VistaMisRutinas
from vistas.alumno.vista_mis_metricas import VistaMisMetricas
from vistas.alumno.vista_mi_perfil import VistaMiPerfilAlumno

# Ruta al banner (logo + texto GOGYM), 2 niveles arriba de este archivo
# (vista_menu_alumno.py esta en vistas/, la raiz del proyecto es un nivel mas arriba)
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_BANNER = os.path.join(CARPETA_BASE, "recursos", "imagenes", "banner.png")

ANCHO_BARRA_LATERAL = 220


class VistaMenuAlumno(ctk.CTkFrame):
    def __init__(self, master, id_usuario, correo, al_cerrar_sesion=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_usuario = id_usuario
        self.correo = correo
        self.al_cerrar_sesion = al_cerrar_sesion

        # Traemos los datos de perfil una vez al entrar, para saber el
        # nombre a mostrar en la barra lateral y el id_alumno a usar
        # en el resto de las consultas.
        # Se llama a "obtener_datos_perfil" (la version generica de
        # usuario_modelo.py, la que trae correo/fecha_registro/foto
        # del alumno) UNA SOLA VEZ, aqui en __init__, y se guarda en
        # "self.datos_perfil" para reutilizarla en TODA la barra
        # lateral, en vez de volver a consultar la base de datos cada
        # vez que se dibuja algo.
        self.datos_perfil = obtener_datos_perfil(id_usuario) or {}

        # "id_alumno" es DISTINTO a "id_usuario": id_usuario identifica
        # la CUENTA (tabla usuario), id_alumno identifica el registro
        # especifico en la tabla "alumno". Se saca aqui, una sola vez,
        # para pasarselo a las 4 vistas de contenido (todas lo
        # necesitan para hacer sus propias consultas).
        self.id_alumno = self.datos_perfil.get("id_alumno")

        self._construir_barra_lateral()

        # Area donde se dibuja la pantalla activa (Inicio, Mis Rutinas, etc.)
        self._area_contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self._area_contenido.pack(side="left", fill="both", expand=True)

        self.mostrar_inicio()  # pantalla que se ve al entrar

    # -----------------------------------------------------------------
    # Construccion de la barra lateral
    # -----------------------------------------------------------------

    def _construir_barra_lateral(self):
        barra = ctk.CTkFrame(self, fg_color=COLOR_ROJO, corner_radius=0, width=ANCHO_BARRA_LATERAL)
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)  # evita que la barra cambie de ancho segun su contenido

        # --- Banner (logo + texto GOGYM) arriba ---
        imagen_banner = self._cargar_banner()
        if imagen_banner is not None:
            ctk.CTkLabel(barra, image=imagen_banner, text="").pack(pady=(20, 20), padx=20)
            self._imagen_banner = imagen_banner  # se guarda para que no la borre el recolector de basura

        # --- Chip con foto/avatar + nombre del alumno ---
        # Se junta el nombre y apellido paterno del alumno en un solo
        # texto (sin apellido materno, para que el chip no se vea
        # demasiado largo en la barra lateral, que es angosta).
        nombre_completo = (
            f"{self.datos_perfil.get('nombre', '')} "
            f"{self.datos_perfil.get('ap_paterno', '')}"
        ).strip()

        chip = ctk.CTkFrame(barra, fg_color=COLOR_BLANCO, corner_radius=20)
        chip.pack(padx=20, pady=(0, 20), fill="x")

        # Se llama a la funcion reutilizable crear_avatar (misma que
        # usan las pantallas de Mi Perfil), pasandole la ruta de foto
        # guardada en "datos_perfil". Si no hay foto, se vera el
        # circulo gris de respaldo automaticamente.
        widget_avatar, self._imagen_avatar_chip = crear_avatar(
            chip, nombre_completo or self.correo,
            ruta_foto=self.datos_perfil.get("foto"), tamanio=32,
        )
        widget_avatar.pack(side="left", padx=(8, 6), pady=6)

        # "nombre_completo or self.correo": si por alguna razon el
        # alumno no tuviera nombre guardado (nombre_completo quedaria
        # como cadena vacia, que Python trata como "falso"), se
        # muestra su correo en su lugar, para que el chip nunca se vea
        # completamente vacio.
        ctk.CTkLabel(
            chip, text=nombre_completo or self.correo, text_color="black",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 10), pady=8)

        # --- Botones de navegacion ---
        # Se crean los 4 botones de esta barra lateral, cada uno
        # conectado a un metodo distinto de esta misma clase (definidos
        # mas abajo), que es el que decide que vista dibujar.
        self._crear_boton_nav(barra, "Inicio", self.mostrar_inicio)
        self._crear_boton_nav(barra, "Mis Rutinas", self.mostrar_mis_rutinas)
        self._crear_boton_nav(barra, "Mis Metricas", self.mostrar_mis_metricas)
        self._crear_boton_nav(barra, "Mi Perfil", self.mostrar_mi_perfil)

        # Espaciador vacio que empuja "Cerrar Sesion" hasta el fondo
        ctk.CTkLabel(barra, text="", fg_color=COLOR_ROJO).pack(expand=True, fill="both")

        ctk.CTkButton(
            barra, text="Cerrar Sesion", fg_color="transparent", hover_color=COLOR_ROJO_OSCURO,
            anchor="w", text_color="white", command=self._al_cerrar_sesion,
        ).pack(fill="x", padx=10, pady=20)

    def _crear_boton_nav(self, barra, texto, comando):
        """Crea un boton de la barra lateral con el estilo comun a todos."""
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
        VistaInicioAlumno(self._area_contenido, self.id_alumno).pack(fill="both", expand=True)

    def mostrar_mis_rutinas(self):
        self._limpiar_area_contenido()
        VistaMisRutinas(self._area_contenido, self.id_alumno).pack(fill="both", expand=True)

    def mostrar_mis_metricas(self):
        self._limpiar_area_contenido()
        VistaMisMetricas(self._area_contenido, self.id_alumno).pack(fill="both", expand=True)

    def mostrar_mi_perfil(self):
        self._limpiar_area_contenido()
        # A diferencia de las otras 3 pantallas (que solo necesitan
        # "id_alumno"), esta SI necesita ademas "id_usuario" (porque
        # actualizar el correo o la contrasenia toca la tabla
        # "usuario", no solo "alumno"), y le pasa "al_guardar" apuntando
        # al metodo "_refrescar_datos_perfil" de aqui abajo.
        VistaMiPerfilAlumno(
            self._area_contenido, self.id_usuario, self.id_alumno,
            al_guardar=self._refrescar_datos_perfil,
        ).pack(fill="both", expand=True)

    def _refrescar_datos_perfil(self):
        """Cuando el alumno guarda cambios en Mi Perfil (incluida la
        foto), volvemos a cargar sus datos y redibujamos la barra
        lateral para que el chip se actualice de inmediato."""
        # Se vuelve a pedir "datos_perfil" a la base de datos, para
        # tener los valores FRESCOS (el nombre nuevo, la foto nueva,
        # etc.), ya que lo que se cargo en __init__ ya quedo viejo.
        self.datos_perfil = obtener_datos_perfil(self.id_usuario) or {}

        # Se destruye TODO lo que hay en esta vista completa (tanto la
        # barra lateral como el area de contenido), porque el chip de
        # la barra lateral NO se puede actualizar "solo" facilmente —
        # es mas simple reconstruir todo desde cero con los datos ya
        # actualizados.
        for widget in self.winfo_children():
            widget.destroy()

        self._construir_barra_lateral()

        self._area_contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self._area_contenido.pack(side="left", fill="both", expand=True)

        self.mostrar_mi_perfil()  # se queda en la misma pantalla

    def _al_cerrar_sesion(self):
        if self.al_cerrar_sesion:
            self.al_cerrar_sesion()
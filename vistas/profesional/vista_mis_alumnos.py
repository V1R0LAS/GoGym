"""
Vista 'Mis Alumnos' del Profesional: buscador + tabla con los alumnos
asignados a este profesional, con un enlace "ver alumno" para entrar
al detalle de cada uno.

Responsabilidad Unica: esta clase solo dibuja la pantalla y reacciona
a los clics. La consulta de datos vive en profesional_modelo.py, y la
navegacion hacia el detalle la decide quien use esta vista (le pasamos
una funcion 'al_ver_alumno', no sabemos nada de como se cambia de
pantalla aqui adentro).
"""
import customtkinter as ctk

from utilidades.componentes import crear_encabezado
from utilidades.estilos import COLOR_FONDO_CAMPO, COLOR_BORDE, COLOR_ROJO
from modelos.profesional_modelo import listar_mis_alumnos


class VistaMisAlumnos(ctk.CTkFrame):
    def __init__(self, master, id_profesional, al_ver_alumno=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_profesional = id_profesional

        # Mismo patron de CALLBACK que ya vimos varias veces: esta
        # vista NO sabe como cambiar de pantalla hacia el detalle de un
        # alumno. Solo recibe una funcion (que en la practica es
        # "mostrar_detalle_alumno" de VistaMenuProfesional) y la llama
        # cuando hace falta, sin importarle como esta implementada por
        # dentro.
        self.al_ver_alumno = al_ver_alumno

        crear_encabezado(self, "Mis Alumnos")

        self.cuerpo = ctk.CTkFrame(self, fg_color="white")
        self.cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        self._construir_barra_busqueda()

        self._area_tabla = ctk.CTkScrollableFrame(self.cuerpo, fg_color="white")
        self._area_tabla.pack(fill="both", expand=True, pady=(15, 0))

        self._dibujar_tabla()

    def _construir_barra_busqueda(self):
        fila = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila.pack(fill="x")

        self.campo_busqueda = ctk.CTkEntry(
            fila, placeholder_text="Buscar alumno...", height=36,
            corner_radius=8, border_width=1, border_color=COLOR_BORDE, fg_color=COLOR_FONDO_CAMPO,
        )
        self.campo_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Igual que en "Gestion de Usuarios" del Admin: se puede buscar
        # presionando Enter, sin necesidad de dar clic en el boton.
        self.campo_busqueda.bind("<Return>", lambda evento: self._dibujar_tabla())

        # El boton "Buscar" hace exactamente lo mismo que presionar
        # Enter (llama a _dibujar_tabla), es solo una alternativa
        # visual por si el profesional prefiere darle clic con el mouse
        # en vez de usar el teclado.
        ctk.CTkButton(
            fila, text="Buscar", fg_color="black", hover_color="#333333",
            width=90, command=self._dibujar_tabla,
        ).pack(side="left")

    def _dibujar_tabla(self):
        # Se borra todo lo que hubiera antes en la tabla (mismo patron
        # de "redibujar desde cero" que ya vimos en varias otras
        # vistas).
        for widget in self._area_tabla.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self._area_tabla, text="Alumnos Registrados", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(10, 10))

        encabezado = ctk.CTkFrame(self._area_tabla, fg_color="#EFEFEF", corner_radius=6)
        encabezado.pack(fill="x", pady=(0, 4))
        for texto, ancho in [("Nombre", 220), ("Correo", 220), ("Estado", 100)]:
            ctk.CTkLabel(encabezado, text=texto, text_color="black",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         width=ancho, anchor="w").pack(side="left", padx=5, pady=8)

        busqueda = self.campo_busqueda.get().strip()
        # Se le pide al modelo la lista de alumnos, filtrada por lo
        # que haya escrito el profesional en el buscador (si no
        # escribio nada, "busqueda" queda como cadena vacia, y el
        # LIKE '%%' de la consulta trae a TODOS los alumnos).
        alumnos = listar_mis_alumnos(self.id_profesional, busqueda)

        if not alumnos:
            ctk.CTkLabel(self._area_tabla, text="No tienes alumnos asignados todavia",
                         text_color="gray").pack(pady=15)
            return

        for alumno in alumnos:
            self._dibujar_fila_alumno(alumno)

    def _dibujar_fila_alumno(self, alumno):
        fila = ctk.CTkFrame(self._area_tabla, fg_color="white", border_width=1,
                            border_color="#EEEEEE", corner_radius=6)
        fila.pack(fill="x", pady=2)

        nombre_completo = f"{alumno['nombre']} {alumno['ap_paterno']}"
        ctk.CTkLabel(fila, text=nombre_completo, text_color="black",
                     width=220, anchor="w").pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(fila, text=alumno["correo"], text_color="black",
                     width=220, anchor="w").pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(fila, text=alumno["estado"], text_color="black",
                     width=100, anchor="w").pack(side="left", padx=5, pady=10)

        # El enlace "ver alumno", estilizado como texto rojo (mismo
        # patron visual que "Restablecer contrasenia" en Gestion de
        # Usuarios del Admin).
        enlace = ctk.CTkButton(
            fila, text="ver alumno", fg_color="white", text_color=COLOR_ROJO,
            hover_color="#F5F5F5", corner_radius=0, border_width=0,
            font=ctk.CTkFont(size=12, underline=True),
            # Se usa "lambda: ..." (sin parametro por defecto aqui,
            # porque "alumno" es un parametro NUEVO de esta funcion
            # _dibujar_fila_alumno en cada llamada del ciclo "for" de
            # _dibujar_tabla — cada fila ya tiene SU PROPIO "alumno"
            # correcto, sin necesidad del truco "ej=ejercicio" que
            # vimos en otros archivos donde el ciclo estaba DENTRO de
            # la misma funcion).
            command=lambda: self._ver_alumno(alumno["id_alumno"]),
        )
        enlace.pack(side="left", padx=8, pady=10)

    def _ver_alumno(self, id_alumno):
        """Se llama al dar clic en 'ver alumno'. Delega la navegacion
        al menu (VistaMenuProfesional), esta vista no sabe como se
        cambia de pantalla."""
        # Se revisa primero que SI se haya recibido una funcion
        # "al_ver_alumno" al crear esta vista (por si alguien la usara
        # sin pasarsela, para no tronar intentando llamar a None).
        if self.al_ver_alumno:
            self.al_ver_alumno(id_alumno)
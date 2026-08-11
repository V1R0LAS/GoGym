"""
Vista 'Inicio' del Profesional: dashboard con el resumen de sus
alumnos y rutinas asignadas, y la actividad reciente.

Responsabilidad Unica: esta clase solo dibuja la pantalla y le pide
los numeros a profesional_modelo.py. No hace ningun conteo aqui adentro.
"""
import customtkinter as ctk

from utilidades.componentes import crear_encabezado, crear_tarjeta_metrica
from modelos.profesional_modelo import (
    obtener_resumen_dashboard_profesional,
    obtener_actividad_reciente,
)


class VistaInicioProfesional(ctk.CTkFrame):
    def __init__(self, master, id_profesional):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_profesional = id_profesional
        self._construir_interfaz()

    def _construir_interfaz(self):
        crear_encabezado(self, "Inicio")

        cuerpo = ctk.CTkFrame(self, fg_color="white")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        # Se pide UN diccionario con los 2 numeros de las tarjetas de
        # arriba (alumnos activos, rutinas asignadas). Al igual que en
        # vista_inicio.py del Admin, esta vista no sabe NADA de como
        # se calculan esos numeros por dentro.
        resumen = obtener_resumen_dashboard_profesional(self.id_profesional)

        fila_tarjetas = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_tarjetas.pack(fill="x", pady=(0, 20))

        crear_tarjeta_metrica(
            fila_tarjetas, "Alumnos activos", str(resumen["alumnos_activos"])
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Rutinas Asignadas", str(resumen["rutinas_asignadas"])
        ).pack(side="left")

        # --- Actividad reciente de los alumnos ---
        ctk.CTkLabel(
            cuerpo, text="Actividad Reciente de Alumnos", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        # "obtener_actividad_reciente" devuelve una LISTA de
        # diccionarios, cada uno con "texto" (ya redactado en
        # espaniol, ej. "Sergio Cruz completo la rutina") y "fecha"
        # (un objeto date de Python, no un texto). Recordemos que esta
        # funcion, en profesional_modelo.py, ya se encarga de MEZCLAR
        # y ORDENAR 2 tipos de eventos distintos (rutinas y
        # mediciones) antes de entregarlos aqui.
        eventos = obtener_actividad_reciente(self.id_profesional)

        if not eventos:
            # Si el profesional todavia no tiene ningun alumno con
            # actividad (ni rutinas ni mediciones), se avisa en vez de
            # dejar la seccion vacia sin explicacion.
            ctk.CTkLabel(cuerpo, text="Aun no hay actividad de tus alumnos",
                         text_color="gray").pack(anchor="w")
        else:
            # Se recorre la lista de eventos, y por cada uno se dibuja
            # una "tarjetita" gris con 2 renglones: el texto principal
            # en negrita arriba, y la fecha en gris chico abajo.
            for evento in eventos:
                fila = ctk.CTkFrame(cuerpo, fg_color="#F5F5F5", corner_radius=8)
                fila.pack(fill="x", pady=4)

                ctk.CTkLabel(fila, text=evento["texto"], text_color="black",
                             font=ctk.CTkFont(weight="bold"), anchor="w").pack(
                    fill="x", padx=10, pady=(8, 0))

                # Se convierte la fecha (objeto date) a texto legible
                # con .strftime(), justo aqui en la vista (en vez de
                # hacerlo en el modelo), porque el modelo entrega la
                # fecha "cruda" para que quien la use decida como
                # formatearla — en este caso, dia/mes/anio.
                ctk.CTkLabel(fila, text=evento["fecha"].strftime("%d/%m/%Y"),
                             text_color="gray", font=ctk.CTkFont(size=10), anchor="w").pack(
                    fill="x", padx=10, pady=(0, 8))
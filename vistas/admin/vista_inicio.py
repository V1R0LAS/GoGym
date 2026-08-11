"""
Vista 'Inicio' del Administrador: dashboard con el resumen general de
usuarios registrados en la plataforma.

Responsabilidad Unica: esta clase solo dibuja las 3 tarjetas y le pide
los numeros a admin_modelo.py. No hace ningun conteo ni consulta SQL
aqui adentro.
"""
import customtkinter as ctk

from utilidades.componentes import crear_encabezado, crear_tarjeta_metrica
from modelos.admin_modelo import obtener_resumen_dashboard_admin


class VistaInicioAdmin(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white", corner_radius=0)
        # A diferencia de otras vistas que dibujan todo directo dentro
        # de __init__, aqui se delega ese trabajo a un metodo aparte
        # llamado "_construir_interfaz()". Es un estilo de escritura
        # (a veces se hace, a veces no en este proyecto), pero el
        # resultado final es el mismo: se llama una sola vez, al crear
        # la vista.
        self._construir_interfaz()

    def _construir_interfaz(self):
        crear_encabezado(self, "Panel Administrador")

        cuerpo = ctk.CTkFrame(self, fg_color="white")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        # Se le pide al modelo el resumen YA CALCULADO (cuantos
        # usuarios hay en total, cuantos profesionales, cuantos
        # alumnos). Esta vista no sabe NADA de como se cuenta eso en
        # la base de datos, solo recibe los 3 numeros listos para
        # mostrarse.
        resumen = obtener_resumen_dashboard_admin()

        fila_tarjetas = ctk.CTkFrame(cuerpo, fg_color="white")
        # "anchor='n'" (north/norte) le dice que se posicione pegada
        # arriba del todo dentro de "cuerpo", en vez de quedar centrada
        # verticalmente (util aqui porque "cuerpo" es mas alto que la
        # fila de tarjetas, y sin esto podria verse descentrado hacia
        # abajo).
        fila_tarjetas.pack(fill="x", anchor="n")

        # Se crean las 3 tarjetas, una junto a otra ("side='left'" en
        # las 3), usando la funcion reutilizable crear_tarjeta_metrica
        # que ya vimos en utilidades/componentes.py. Aqui no se les
        # pasa el parametro "ancho", asi que cada tarjeta se ajusta al
        # tamanio de su propio texto (no hace falta que sean parejas
        # en esta pantalla, a diferencia de "Mis Metricas").
        crear_tarjeta_metrica(
            fila_tarjetas, "Usuarios Totales", str(resumen["usuarios_totales"])
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Profesionales", str(resumen["profesionales"])
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Alumnos", str(resumen["alumnos"])
        ).pack(side="left")
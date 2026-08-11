"""
Vista 'Inicio' del Alumno: resumen rapido de su actividad (dashboard).

Responsabilidad Unica: esta clase solo dibuja la pantalla y le pide los
numeros al modelo (alumno_modelo.py). No hace calculos ni consultas SQL
aqui adentro.
"""
import customtkinter as ctk

from utilidades.componentes import crear_encabezado, crear_tarjeta_metrica
from utilidades.graficas import crear_grafica_peso
from modelos.alumno_modelo import (
    obtener_resumen_dashboard,
    obtener_proximas_rutinas,
    obtener_progreso_peso,
)


class VistaInicioAlumno(ctk.CTkFrame):
    def __init__(self, master, id_alumno):
        super().__init__(master, fg_color="white", corner_radius=0)
        # Se guarda "id_alumno" como atributo de la instancia
        # (self.id_alumno), porque se va a necesitar en VARIAS partes
        # de _construir_interfaz() (para pedir el resumen, las
        # proximas rutinas, y el progreso de peso). Guardarlo en
        # "self" evita tener que pasarlo como parametro entre metodos.
        self.id_alumno = id_alumno
        self._construir_interfaz()

    def _construir_interfaz(self):
        crear_encabezado(self, "Inicio")

        cuerpo = ctk.CTkFrame(self, fg_color="white")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        # --- Tarjetas de resumen (arriba) ---
        # Una sola consulta al modelo trae los 3 numeros de las
        # tarjetas juntos (rutinas del mes, peso actual, racha de
        # dias), en vez de 3 consultas separadas.
        resumen = obtener_resumen_dashboard(self.id_alumno)

        fila_tarjetas = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_tarjetas.pack(fill="x", pady=(0, 20))

        crear_tarjeta_metrica(
            fila_tarjetas, "Rutinas Completadas/mes", f"{resumen['rutinas_mes']} Rutinas"
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Peso Actual", f"{resumen['peso_actual']}kg"
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Racha Actual", f"{resumen['racha_dias']} Dias"
        ).pack(side="left")

        # --- Fila inferior: proximas rutinas (izquierda) + grafica (derecha) ---
        # Este frame es el CONTENEDOR de las 2 columnas de abajo. Se
        # crea PRIMERO vacio, y luego se van llenando sus 2 "hijos"
        # (columna_rutinas y columna_grafica), cada uno acomodado con
        # "side='left'" para que queden uno junto al otro
        # (horizontalmente), en vez de uno encima del otro.
        fila_inferior = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_inferior.pack(fill="both", expand=True)

        # --- Columna izquierda: Proximas Rutinas ---
        columna_rutinas = ctk.CTkFrame(fila_inferior, fg_color="white")
        # "expand=True" en AMBAS columnas (esta y la de la grafica) es
        # lo que hace que se REPARTAN el espacio disponible A PARTES
        # IGUALES (cada una toma la mitad del ancho de "fila_inferior"),
        # en vez de que una se quede chiquita y la otra ocupe todo.
        columna_rutinas.pack(side="left", fill="both", expand=True, padx=(0, 20))

        ctk.CTkLabel(
            columna_rutinas, text="Proximas Rutinas", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        proximas = obtener_proximas_rutinas(self.id_alumno)
        if not proximas:
            # Si la LISTA de proximas rutinas viene vacia ("not
            # proximas" es True cuando la lista no tiene ningun
            # elemento), se muestra un mensaje explicando la situacion,
            # en vez de dejar la columna vacia sin explicacion (mismo
            # principio que ya vimos en la grafica de peso).
            ctk.CTkLabel(columna_rutinas, text="No tienes rutinas pendientes",
                         text_color="gray").pack(anchor="w")
        else:
            # Se recorre la lista de rutinas pendientes (maximo 3,
            # segun el "limite" por defecto de
            # obtener_proximas_rutinas), y se dibuja una "tarjetita"
            # gris por cada una, con el nombre de la rutina y su fecha.
            for rutina in proximas:
                texto = f"{rutina['nombre_rutina']} - {rutina['fecha_inicio'].strftime('%d/%m/%Y')}"
                fila = ctk.CTkFrame(columna_rutinas, fg_color="#F5F5F5", corner_radius=8)
                fila.pack(fill="x", pady=4)
                ctk.CTkLabel(fila, text=texto, text_color="black", anchor="w").pack(
                    fill="x", padx=10, pady=8)

        # --- Columna derecha: grafica de progreso de peso ---
        columna_grafica = ctk.CTkFrame(fila_inferior, fg_color="white")
        columna_grafica.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            columna_grafica, text="Progreso de Peso", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        # Se traen las mediciones de peso del alumno, y se le pasan a
        # la funcion REUTILIZABLE crear_grafica_peso (la misma que
        # usa "Mis Metricas"), que devuelve un widget YA LISTO para
        # acomodarse con .pack(). Esta vista no sabe NADA de como se
        # dibuja una grafica con matplotlib por dentro.
        mediciones = obtener_progreso_peso(self.id_alumno)
        widget_grafica = crear_grafica_peso(columna_grafica, mediciones)
        widget_grafica.pack(fill="both", expand=True)
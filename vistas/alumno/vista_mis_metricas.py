"""
Vista 'Mis Metricas' del Alumno: registrar una nueva medicion (peso y
altura) y ver el resumen + la grafica de su evolucion.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from utilidades.componentes import crear_encabezado, crear_tarjeta_metrica
from utilidades.estilos import COLOR_FONDO_CAMPO, COLOR_BORDE
from utilidades.graficas import crear_grafica_peso
from modelos.alumno_modelo import (
    registrar_medicion,
    obtener_ultima_medicion,
    obtener_progreso_peso,
    obtener_resumen_dashboard,
    calcular_imc,
)

# Constante de este archivo: se usa para que las 4 tarjetas de abajo
# (Peso, Racha, Rutinas, IMC) tengan EXACTAMENTE el mismo ancho, en
# vez de que cada una mida distinto segun el largo de su propio texto
# (ver el parametro "ancho" de crear_tarjeta_metrica).
ANCHO_TARJETA = 170  # mismo ancho para las 4 tarjetas, para que se vean parejas


class VistaMisMetricas(ctk.CTkFrame):
    def __init__(self, master, id_alumno):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_alumno = id_alumno

        crear_encabezado(self, "Mis Metricas")

        # A diferencia de otras vistas, aqui "self.cuerpo" se guarda
        # como atributo (self.cuerpo, no una variable local "cuerpo"),
        # porque _dibujar_contenido() necesita poder LIMPIARLO y
        # volver a llenarlo cada vez que se registra una medicion
        # nueva, y para eso necesita poder accederlo desde otro
        # metodo (no solo desde __init__).
        self.cuerpo = ctk.CTkFrame(self, fg_color="white")
        self.cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        self._dibujar_contenido()

    def _dibujar_contenido(self):
        # Se borra todo lo que hubiera antes en "self.cuerpo" (la
        # primera vez que se llama, en __init__, no hay nada que
        # borrar, pero las siguientes veces -despues de guardar una
        # medicion nueva- si hay contenido viejo que limpiar).
        for widget in self.cuerpo.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.cuerpo, text="Registrar Medicion", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 8))

        # --- Formulario de 3 campos + boton, todos en la misma fila ---
        fila_formulario = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila_formulario.pack(fill="x", pady=(0, 20))

        # El campo de fecha viene PRE-LLENADO con la fecha de HOY (para
        # que el alumno no tenga que escribirla a mano cada vez, solo
        # cambiarla si de verdad quiere registrar una fecha distinta).
        self.campo_fecha = ctk.CTkEntry(
            fila_formulario, width=130, fg_color=COLOR_FONDO_CAMPO, border_width=1,
            border_color=COLOR_BORDE, text_color="black", justify="center",
        )
        self.campo_fecha.insert(0, date.today().strftime("%Y-%m-%d"))
        self.campo_fecha.pack(side="left", padx=(0, 10))

        # Estos 2 campos, en cambio, usan "placeholder_text" (el texto
        # gris de ayuda que desaparece al escribir) en vez de un valor
        # ya insertado, porque no tiene sentido "sugerir" un peso o una
        # altura por defecto — cada vez se espera un valor NUEVO.
        self.campo_peso = ctk.CTkEntry(
            fila_formulario, placeholder_text="Peso (kg)", width=110,
            fg_color=COLOR_FONDO_CAMPO, border_width=1,
            border_color=COLOR_BORDE, text_color="black", justify="center",
        )
        self.campo_peso.pack(side="left", padx=(0, 10))

        self.campo_altura = ctk.CTkEntry(
            fila_formulario, placeholder_text="Altura (cm)", width=110,
            fg_color=COLOR_FONDO_CAMPO, border_width=1,
            border_color=COLOR_BORDE, text_color="black", justify="center",
        )
        self.campo_altura.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_formulario, text="Guardar Medicion", fg_color="black",
            hover_color="#333333", command=self._guardar_medicion,
        ).pack(side="left")

        # --- Tarjetas de resumen ---
        # Se piden 2 cosas distintas al modelo: el resumen general
        # (rutinas del mes, peso actual, racha), y ademas la ULTIMA
        # medicion completa (peso Y altura juntos), porque el IMC
        # necesita AMBOS datos para calcularse, y "obtener_resumen_
        # dashboard" solo trae el peso (no la altura).
        resumen = obtener_resumen_dashboard(self.id_alumno)
        ultima = obtener_ultima_medicion(self.id_alumno)

        # "ultima['peso'] if ultima else 0": si el alumno TODAVIA no
        # tiene ninguna medicion registrada, "ultima" seria None, y
        # tratar de leer "ultima['peso']" sobre un None causaria un
        # error. Por eso se revisa primero si "ultima" existe, y si no,
        # se manda 0 como respaldo (que calcular_imc ya sabe manejar,
        # devolviendo "Sin datos" en ese caso, como vimos en
        # alumno_modelo.py).
        imc, rango_imc = calcular_imc(
            ultima["peso"] if ultima else 0,
            ultima["altura"] if ultima else 0,
        )

        fila_tarjetas = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila_tarjetas.pack(fill="x", pady=(0, 20))

        # Las 4 tarjetas se crean con "ancho=ANCHO_TARJETA" para que
        # todas midan exactamente 170 pixeles, sin importar si el
        # texto de una es mas corto o largo que el de otra.
        crear_tarjeta_metrica(
            fila_tarjetas, "Peso Actual", f"{resumen['peso_actual']}kg", ancho=ANCHO_TARJETA
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Racha Actual", f"{resumen['racha_dias']} Dias", ancho=ANCHO_TARJETA
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Rutinas Completadas/mes", f"{resumen['rutinas_mes']} Rutinas", ancho=ANCHO_TARJETA
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "IMC", str(imc), subtexto=rango_imc, ancho=ANCHO_TARJETA
        ).pack(side="left")

        # --- Grafica de progreso ---
        ctk.CTkLabel(
            self.cuerpo, text="Grafica - Peso", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        mediciones = obtener_progreso_peso(self.id_alumno)
        widget_grafica = crear_grafica_peso(self.cuerpo, mediciones)
        widget_grafica.pack(fill="both", expand=True)

    def _guardar_medicion(self):
        # Se leen los 3 campos del formulario como texto.
        fecha_texto = self.campo_fecha.get().strip()
        peso_texto = self.campo_peso.get().strip()
        altura_texto = self.campo_altura.get().strip()

        # Primera validacion: que ningun campo se haya quedado vacio.
        if not fecha_texto or not peso_texto or not altura_texto:
            messagebox.showwarning("Datos incompletos", "Llena fecha, peso y altura.")
            return

        # Segunda validacion: que "peso" y "altura" de verdad sean
        # NUMEROS validos. "float(texto)" intenta convertir el texto
        # escrito a un numero decimal; si el alumno escribio algo que
        # no es un numero (por ejemplo, "abc" o "68,5" con coma en vez
        # de punto), Python lanza un "ValueError", que aqui se atrapa
        # para mostrar un mensaje claro en vez de un error tecnico feo.
        try:
            peso = float(peso_texto)
            altura = float(altura_texto)
        except ValueError:
            messagebox.showerror("Error", "Peso y altura deben ser numeros (ej. 68.5).")
            return

        # Si ambas validaciones pasaron, se manda a guardar. Recordemos
        # que "registrar_medicion" ya sabe manejar el caso de que ya
        # exista una medicion ese mismo dia (la actualiza en vez de
        # tronar), gracias al "ON DUPLICATE KEY UPDATE" que vimos en
        # alumno_modelo.py.
        exito = registrar_medicion(self.id_alumno, fecha_texto, peso, altura)
        if exito:
            messagebox.showinfo("Listo", "Medicion guardada correctamente.")
            # Se vuelve a dibujar TODO el contenido (formulario +
            # tarjetas + grafica), para que las tarjetas y la grafica
            # se actualicen con el dato recien guardado, de inmediato.
            self._dibujar_contenido()
        else:
            messagebox.showerror(
                "Error", "No se pudo guardar la medicion. Revisa el formato de la fecha (AAAA-MM-DD)."
            )
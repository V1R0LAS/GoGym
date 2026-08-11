"""
Vista 'Detalle Alumno' del Profesional: muestra el encabezado del
alumno elegido, con 2 pestanias:
  - 'Asignar Rutina': formulario para crear una rutina nueva con sus
    ejercicios.
  - 'Metricas': el mismo resumen que el alumno ve en su propio 'Mis
    Metricas', para que el profesional pueda revisar su progreso.

Reutilizacion (Open/Closed): las metricas usan las MISMAS funciones de
alumno_modelo.py que ya existen para la vista del propio alumno. No se
duplica ni una consulta; solo se les pasa el id_alumno correspondiente.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from utilidades.componentes import crear_encabezado, crear_tarjeta_metrica, crear_avatar
from utilidades.estilos import COLOR_FONDO_CAMPO, COLOR_BORDE
from utilidades.graficas import crear_grafica_peso
from modelos.profesional_modelo import (
    obtener_encabezado_alumno,
    obtener_zonas_musculares,
    obtener_ejercicios_por_zona_y_lugar,
    obtener_tipos_entrenamiento,
    crear_rutina_con_ejercicios,
)

# Aqui esta el detalle mas importante de este archivo (explicado en el
# docstring de arriba): se importan funciones de alumno_modelo.py,
# NO se copian ni se reescriben. Esta vista del PROFESIONAL usa el
# MISMO codigo que ya existia para la pantalla "Mis Metricas" del
# propio ALUMNO. Solo cambia el id_alumno que se le pasa (el del
# alumno que el profesional esta consultando, en vez de "self mismo").
from modelos.alumno_modelo import (
    obtener_resumen_dashboard,
    obtener_progreso_peso,
    obtener_ultima_medicion,
    obtener_historial_entrenamientos,
    calcular_imc,
)

# Estilo comun para los dropdowns de esta pantalla (Lugar de
# entrenamiento, Grupo Muscular, Ejercicio): un gris claro, para que
# combinen con el resto de cajas grises de la app, en vez del azul por
# defecto de customtkinter.
ESTILO_OPCION_MENU = dict(
    fg_color=COLOR_FONDO_CAMPO, button_color=COLOR_FONDO_CAMPO, button_hover_color="#D5D5D5",
    text_color="black", dropdown_fg_color="white", dropdown_text_color="black",
)


class VistaDetalleAlumno(ctk.CTkFrame):
    def __init__(self, master, id_alumno, id_profesional, al_volver=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_alumno = id_alumno
        self.id_profesional = id_profesional

        # "al_volver" es OPCIONAL (por defecto None): si quien crea
        # esta vista le pasa una funcion (el metodo "mostrar_mis_
        # alumnos" de la barra lateral), aparece el boton de "Volver".
        # Si no se lo pasan, simplemente no se dibuja ese boton (ver
        # mas abajo el "if self.al_volver:").
        self.al_volver = al_volver

        # "pestania_activa" recuerda cual de las 2 pestanias esta
        # visible ahorita ("rutina" o "metricas"). Empieza en "rutina"
        # por defecto, cada vez que se entra a ver un alumno nuevo.
        self.pestania_activa = "rutina"

        # Lista EN MEMORIA (no en la base de datos todavia) de los
        # ejercicios que el profesional va agregando mientras arma una
        # rutina nueva. Se explica mejor mas abajo, en
        # _agregar_ejercicio_temporal.
        self._ejercicios_temporales = []

        crear_encabezado(self, "Mis Alumnos")

        self.cuerpo = ctk.CTkFrame(self, fg_color="white")
        self.cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        self._dibujar_encabezado_alumno()
        self._dibujar_pestanias()

        # "_area_pestania" es el "hueco" donde se va a dibujar el
        # CONTENIDO de la pestania activa (el formulario de Asignar
        # Rutina, o las tarjetas de Metricas). Se guarda como atributo
        # porque _cambiar_pestania() necesita poder LIMPIARLO y volver
        # a llenarlo cada vez que se cambia de pestania.
        self._area_pestania = ctk.CTkFrame(self.cuerpo, fg_color="white")
        self._area_pestania.pack(fill="both", expand=True)

        self._dibujar_pestania_activa()

    def _dibujar_encabezado_alumno(self):
        # El boton de "Volver" solo se dibuja si SI se recibio una
        # funcion "al_volver" al crear esta vista.
        if self.al_volver:
            ctk.CTkButton(
                self.cuerpo, text="← Volver a Mis Alumnos", fg_color="white", text_color="black",
                hover_color="#F5F5F5", corner_radius=0, border_width=0,
                anchor="w", command=self.al_volver,
            ).pack(anchor="w", pady=(0, 10))

        datos = obtener_encabezado_alumno(self.id_alumno) or {}
        nombre_completo = f"{datos.get('nombre','')} {datos.get('ap_paterno','')} {datos.get('ap_materno','')}".strip()

        fila = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila.pack(fill="x", pady=(0, 15))

        widget_avatar, self._imagen_avatar = crear_avatar(
            fila, nombre_completo, ruta_foto=datos.get("foto"), tamanio=56,
        )
        widget_avatar.pack(side="left", padx=(0, 15))

        columna_texto = ctk.CTkFrame(fila, fg_color="white")
        columna_texto.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(columna_texto, text=nombre_completo, text_color="black",
                     font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")

        # "datos.get('telefono','') or '-'" es un doble respaldo: si la
        # llave no existiera, ".get()" devuelve cadena vacia; y si esa
        # cadena vacia llega hasta el "or", se reemplaza por un guion,
        # para no dejar un espacio vacio raro en medio del subtitulo.
        subtexto = f"{datos.get('correo','')} · {datos.get('telefono','') or '-'} · {datos.get('fecha_registro','')}"
        ctk.CTkLabel(columna_texto, text=subtexto, text_color="gray", anchor="w").pack(fill="x")

    def _dibujar_pestanias(self):
        fila = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila.pack(fill="x", pady=(0, 15))

        # Los 2 botones de pestania cambian su color segun cual este
        # "activa" en este momento: la pestania activa se ve negra con
        # texto blanco, y la inactiva gris con texto negro. Se calcula
        # con un operador ternario en cada parametro de color.
        ctk.CTkButton(
            fila, text="Asignar Rutina", width=140,
            fg_color="black" if self.pestania_activa == "rutina" else "#E5E5E5",
            text_color="white" if self.pestania_activa == "rutina" else "black",
            hover_color="#333333" if self.pestania_activa == "rutina" else "#D5D5D5",
            command=lambda: self._cambiar_pestania("rutina"),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila, text="Metricas", width=140,
            fg_color="black" if self.pestania_activa == "metricas" else "#E5E5E5",
            text_color="white" if self.pestania_activa == "metricas" else "black",
            hover_color="#333333" if self.pestania_activa == "metricas" else "#D5D5D5",
            command=lambda: self._cambiar_pestania("metricas"),
        ).pack(side="left")

    def _cambiar_pestania(self, pestania):
        self.pestania_activa = pestania
        # Se destruye TODO lo que hay en "self.cuerpo" (encabezado,
        # pestanias, Y el contenido de la pestania anterior), y se
        # vuelve a construir todo desde cero. Esto es necesario porque
        # cambiar de pestania tambien necesita redibujar los BOTONES de
        # pestania (para que cambien de color al de "activo"), no solo
        # el contenido de abajo.
        for widget in self.cuerpo.winfo_children():
            widget.destroy()
        self._dibujar_encabezado_alumno()
        self._dibujar_pestanias()
        self._area_pestania = ctk.CTkFrame(self.cuerpo, fg_color="white")
        self._area_pestania.pack(fill="both", expand=True)
        self._dibujar_pestania_activa()

    def _dibujar_pestania_activa(self):
        # Segun el valor de "pestania_activa", se llama a UNA de las 2
        # funciones que dibujan el contenido especifico de cada
        # pestania.
        if self.pestania_activa == "rutina":
            self._dibujar_asignar_rutina()
        else:
            self._dibujar_metricas()

    def _dibujar_asignar_rutina(self):
        contenedor = self._area_pestania

        ctk.CTkLabel(contenedor, text="Asignar / Crear Rutina", text_color="black",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(fill="x", pady=(0, 10))

        # --- Fila 1: Nombre de la rutina, Fecha, Lugar de entrenamiento ---
        fila1 = ctk.CTkFrame(contenedor, fg_color="white")
        fila1.pack(fill="x", pady=(0, 15))

        columna_nombre = ctk.CTkFrame(fila1, fg_color="white")
        columna_nombre.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(columna_nombre, text="Nombre de la rutina").pack(anchor="w")
        self.campo_nombre_rutina = ctk.CTkEntry(
            columna_nombre, width=180, fg_color=COLOR_FONDO_CAMPO,
            border_width=1, border_color=COLOR_BORDE, text_color="black",
        )
        self.campo_nombre_rutina.pack()

        columna_fecha = ctk.CTkFrame(fila1, fg_color="white")
        columna_fecha.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(columna_fecha, text="Fecha (AAAA-MM-DD)").pack(anchor="w")
        self.campo_fecha_rutina = ctk.CTkEntry(
            columna_fecha, width=140, fg_color=COLOR_FONDO_CAMPO,
            border_width=1, border_color=COLOR_BORDE, text_color="black",
        )
        # Se prellena con la fecha de HOY, igual que en "Registrar
        # Medicion" del alumno.
        self.campo_fecha_rutina.insert(0, date.today().strftime("%Y-%m-%d"))
        self.campo_fecha_rutina.pack()

        # Se trae la lista de lugares (Casa/Gimnasio) del modelo, y se
        # arma un DICCIONARIO que va de "nombre" a "id" (ej.
        # {"Casa": 1, "Gimnasio": 2}). Esto es MUY util: el dropdown
        # solo puede mostrar TEXTOS (nombres), pero la base de datos
        # necesita el ID NUMERICO para guardar la rutina. Este
        # diccionario permite "traducir" facilmente de uno al otro.
        tipos = obtener_tipos_entrenamiento()
        self._tipos_entrenamiento = {t["nombre_tipo"]: t["id_tipo_entrenamiento"] for t in tipos}
        columna_lugar = ctk.CTkFrame(fila1, fg_color="white")
        columna_lugar.pack(side="left")
        ctk.CTkLabel(columna_lugar, text="Lugar de entrenamiento").pack(anchor="w")
        self.combo_lugar = ctk.CTkOptionMenu(
            columna_lugar, values=list(self._tipos_entrenamiento.keys()) or ["Casa"],
            # Cada vez que se cambia el lugar (Casa/Gimnasio), se
            # vuelve a llamar a _actualizar_ejercicios(), porque los
            # ejercicios disponibles dependen tambien de este valor
            # (no solo del grupo muscular).
            command=lambda valor: self._actualizar_ejercicios(), **ESTILO_OPCION_MENU,
        )
        self.combo_lugar.pack()

        # --- Fila 2: Grupo Muscular, Ejercicio, Series, Repeticiones ---
        fila2 = ctk.CTkFrame(contenedor, fg_color="white")
        fila2.pack(fill="x", pady=(0, 10))

        # Mismo patron de diccionario "nombre -> id" que con los
        # tipos de entrenamiento, ahora para las zonas musculares.
        zonas = obtener_zonas_musculares()
        self._zonas_por_nombre = {z["nombre_zona"]: z["id_zona_muscular"] for z in zonas}

        columna_zona = ctk.CTkFrame(fila2, fg_color="white")
        columna_zona.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(columna_zona, text="Selecciona el Grupo Muscular").pack(anchor="w")
        self.combo_zona = ctk.CTkOptionMenu(
            columna_zona, values=list(self._zonas_por_nombre.keys()) or ["-"],
            command=lambda valor: self._actualizar_ejercicios(), **ESTILO_OPCION_MENU,
        )
        self.combo_zona.pack()

        columna_ejercicio = ctk.CTkFrame(fila2, fg_color="white")
        columna_ejercicio.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(columna_ejercicio, text="Selecciona el ejercicio").pack(anchor="w")
        # Este dropdown empieza con un valor "provisional" (["-"]),
        # porque sus opciones REALES se llenan un poco despues, cuando
        # se llama a self._actualizar_ejercicios() (mas abajo en esta
        # misma funcion), una vez que ya se sabe la zona y el lugar
        # elegidos por defecto.
        self.combo_ejercicio = ctk.CTkOptionMenu(columna_ejercicio, values=["-"], **ESTILO_OPCION_MENU)
        self.combo_ejercicio.pack()

        columna_series = ctk.CTkFrame(fila2, fg_color="white")
        columna_series.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(columna_series, text="Series").pack(anchor="w")
        self.campo_series = ctk.CTkEntry(
            columna_series, width=60, fg_color=COLOR_FONDO_CAMPO,
            border_width=1, border_color=COLOR_BORDE, text_color="black",
        )
        self.campo_series.insert(0, "4")
        self.campo_series.pack()

        columna_repeticiones = ctk.CTkFrame(fila2, fg_color="white")
        columna_repeticiones.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(columna_repeticiones, text="Repeticiones").pack(anchor="w")
        self.campo_repeticiones = ctk.CTkEntry(
            columna_repeticiones, width=60, fg_color=COLOR_FONDO_CAMPO,
            border_width=1, border_color=COLOR_BORDE, text_color="black",
        )
        self.campo_repeticiones.insert(0, "12")
        self.campo_repeticiones.pack()

        ctk.CTkButton(
            fila2, text="Asignar ejercicio +", fg_color="black", hover_color="#333333",
            command=self._agregar_ejercicio_temporal,
        ).pack(side="left", padx=(10, 0), pady=(18, 0))

        # Se llama UNA VEZ, justo despues de crear todos los combos, para
        # llenar el combo de ejercicios con las opciones que le
        # correspondan a la zona/lugar seleccionados POR DEFECTO (los
        # primeros de cada lista).
        self._actualizar_ejercicios()

        # --- Botones Asignar Rutina / Cancelar ---
        fila_botones = ctk.CTkFrame(contenedor, fg_color="white")
        fila_botones.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(
            fila_botones, text="Asignar Rutina", fg_color="black", hover_color="#333333",
            command=self._guardar_rutina,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_botones, text="Cancelar", fg_color="#E5E5E5", text_color="black",
            hover_color="#D5D5D5", command=self._cancelar_rutina,
        ).pack(side="left")

        # --- Tabla de ejercicios ya agregados (en memoria) ---
        ctk.CTkLabel(contenedor, text="Ejercicios", text_color="black",
                     font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(fill="x", pady=(0, 8))

        self._area_ejercicios_temporales = ctk.CTkFrame(contenedor, fg_color="white")
        self._area_ejercicios_temporales.pack(fill="both", expand=True)
        self._dibujar_ejercicios_temporales()

    def _actualizar_ejercicios(self):
        """Se llama cada vez que cambia el Grupo Muscular O el Lugar
        de entrenamiento: vuelve a llenar el combo de Ejercicio con
        las opciones que correspondan a AMBOS valores actuales."""
        nombre_zona = self.combo_zona.get()
        nombre_lugar = self.combo_lugar.get()
        # Se "traduce" cada nombre elegido a su id numerico, usando los
        # diccionarios que se armaron antes.
        id_zona = self._zonas_por_nombre.get(nombre_zona)
        id_tipo_entrenamiento = self._tipos_entrenamiento.get(nombre_lugar)

        # Solo se hace la consulta si SI se pudieron traducir ambos
        # valores (por seguridad, en caso de que algo saliera vacio).
        if id_zona and id_tipo_entrenamiento:
            ejercicios = obtener_ejercicios_por_zona_y_lugar(id_zona, id_tipo_entrenamiento)
        else:
            ejercicios = []

        # Se arma OTRO diccionario "nombre -> id", ahora para los
        # ejercicios (se usa mas abajo en _agregar_ejercicio_temporal,
        # para saber el id_ejercicio real del que se eligio por nombre
        # en el dropdown).
        self._ejercicios_por_nombre = {e["nombre_ejercicio"]: e["id_ejercicio"] for e in ejercicios}

        # Si no hay NINGUN ejercicio para esa combinacion de zona+lugar
        # (por ejemplo, "Pecho" + "Casa" pero todavia no se cargaron
        # ejercicios de Casa para Pecho), se muestra un mensaje en vez
        # de dejar el dropdown vacio.
        opciones = list(self._ejercicios_por_nombre.keys()) or ["Sin ejercicios para esta combinacion"]
        self.combo_ejercicio.configure(values=opciones)
        self.combo_ejercicio.set(opciones[0])

    def _agregar_ejercicio_temporal(self):
        """Se llama al dar clic en 'Asignar ejercicio +'. Solo agrega
        el ejercicio elegido a una LISTA EN MEMORIA (self._ejercicios_
        temporales); todavia NO se guarda nada en la base de datos —
        eso pasa hasta que se de clic en 'Asignar Rutina'."""
        nombre_zona = self.combo_zona.get()
        nombre_ejercicio = self.combo_ejercicio.get()
        id_ejercicio = self._ejercicios_por_nombre.get(nombre_ejercicio)

        # Si "id_ejercicio" viniera None (por ejemplo, si el dropdown
        # esta mostrando el mensaje de "Sin ejercicios para esta
        # combinacion", que no es un ejercicio de verdad), se avisa y
        # no se agrega nada.
        if id_ejercicio is None:
            messagebox.showwarning("Datos incompletos", "Elige un ejercicio valido.")
            return

        try:
            # "int(...)" convierte el texto escrito a un numero
            # ENTERO (sin decimales, a diferencia de "float()" que
            # vimos en Mis Metricas, porque series y repeticiones
            # siempre son numeros enteros).
            series = int(self.campo_series.get().strip())
            repeticiones = int(self.campo_repeticiones.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Series y repeticiones deben ser numeros enteros.")
            return

        # Se agrega un diccionario NUEVO a la lista en memoria, con
        # toda la informacion de este ejercicio (tanto para mostrarlo
        # en la tabla de abajo, como para guardarlo despues en la base
        # de datos si se confirma la rutina).
        self._ejercicios_temporales.append({
            "nombre_zona": nombre_zona,
            "nombre_ejercicio": nombre_ejercicio,
            "id_ejercicio": id_ejercicio,
            "series": series,
            "repeticiones_min": repeticiones,
            "repeticiones_max": repeticiones,
        })
        # Se vuelve a dibujar la tabla de ejercicios agregados, para
        # que se vea el que se acaba de agregar.
        self._dibujar_ejercicios_temporales()

    def _dibujar_ejercicios_temporales(self):
        for widget in self._area_ejercicios_temporales.winfo_children():
            widget.destroy()

        if not self._ejercicios_temporales:
            ctk.CTkLabel(self._area_ejercicios_temporales, text="Aun no has agregado ejercicios",
                         text_color="gray").pack(anchor="w", pady=5)
            return

        encabezado = ctk.CTkFrame(self._area_ejercicios_temporales, fg_color="#EFEFEF")
        encabezado.pack(fill="x")
        for texto, ancho in [("Grupo Muscular", 150), ("Ejercicio", 180), ("Series", 70), ("Repeticiones", 100)]:
            ctk.CTkLabel(encabezado, text=texto, font=ctk.CTkFont(weight="bold"),
                         width=ancho, anchor="w").pack(side="left", padx=5, pady=6)

        # "enumerate(lista)" recorre una lista dandote AMBAS cosas al
        # mismo tiempo: el INDICE (posicion: 0, 1, 2...) y el
        # ELEMENTO en si. Se necesita el indice aqui para saber cual
        # ejercicio borrar despues si el profesional le da clic a
        # "Eliminar" en esa fila especifica.
        for indice, ejercicio in enumerate(self._ejercicios_temporales):
            fila = ctk.CTkFrame(self._area_ejercicios_temporales, fg_color="white")
            fila.pack(fill="x")
            ctk.CTkLabel(fila, text=ejercicio["nombre_zona"], width=150, anchor="w").pack(side="left", padx=5, pady=6)
            ctk.CTkLabel(fila, text=ejercicio["nombre_ejercicio"], width=180, anchor="w").pack(side="left", padx=5, pady=6)
            ctk.CTkLabel(fila, text=str(ejercicio["series"]), width=70, anchor="w").pack(side="left", padx=5, pady=6)
            ctk.CTkLabel(fila, text=str(ejercicio["repeticiones_max"]), width=100, anchor="w").pack(side="left", padx=5, pady=6)

            # Mismo truco de "lambda i=indice: ..." que ya vimos en
            # vista_mis_rutinas.py, para que cada boton "Eliminar"
            # recuerde SU PROPIO indice de fila, y no el ultimo del
            # ciclo.
            ctk.CTkButton(
                fila, text="Eliminar", fg_color="white", text_color="black",
                hover_color="#F5F5F5", corner_radius=0, border_width=0,
                command=lambda i=indice: self._eliminar_ejercicio_temporal(i),
            ).pack(side="left", padx=5, pady=6)

    def _eliminar_ejercicio_temporal(self, indice):
        # "del lista[indice]" borra el elemento que esta en esa
        # posicion de la lista EN MEMORIA (esto NO toca la base de
        # datos para nada, porque este ejercicio nunca se habia
        # guardado todavia).
        del self._ejercicios_temporales[indice]
        self._dibujar_ejercicios_temporales()

    def _guardar_rutina(self):
        """Se llama al dar clic en 'Asignar Rutina'. Aqui SI se guarda
        todo de verdad en la base de datos."""
        nombre_rutina = self.campo_nombre_rutina.get().strip()
        fecha = self.campo_fecha_rutina.get().strip()
        nombre_lugar = self.combo_lugar.get()
        id_tipo_entrenamiento = self._tipos_entrenamiento.get(nombre_lugar)

        if not nombre_rutina:
            messagebox.showwarning("Datos incompletos", "Escribe un nombre para la rutina.")
            return

        if not self._ejercicios_temporales:
            messagebox.showwarning("Sin ejercicios", "Agrega al menos un ejercicio a la rutina.")
            return

        # Se manda TODO junto (la rutina + su lista de ejercicios) a
        # la funcion del modelo que se encarga de insertar ambas cosas
        # de un solo golpe (recordemos: con su propio try/rollback,
        # visto en profesional_modelo.py).
        exito = crear_rutina_con_ejercicios(
            self.id_alumno, self.id_profesional, nombre_rutina, fecha,
            id_tipo_entrenamiento, self._ejercicios_temporales,
        )

        if exito:
            messagebox.showinfo("Listo", "Rutina asignada correctamente.")
            self._cancelar_rutina()
        else:
            messagebox.showerror("Error", "No se pudo asignar la rutina.")

    def _cancelar_rutina(self):
        # Se vacia la lista en memoria (todo lo que se habia agregado
        # se pierde, tanto si se cancela a proposito, como despues de
        # guardar exitosamente una rutina)...
        self._ejercicios_temporales = []
        # ...y se vuelve a dibujar la pestania de "rutina" desde cero,
        # para que el formulario aparezca limpio y listo para armar
        # una rutina nueva.
        self._cambiar_pestania("rutina")

    def _dibujar_metricas(self):
        contenedor = self._area_pestania

        # Estas 5 llamadas son EXACTAMENTE las mismas funciones que usa
        # "Mis Metricas" del propio alumno (vista_mis_metricas.py) —
        # la unica diferencia es que aqui "self.id_alumno" es el ID
        # del alumno que el PROFESIONAL esta consultando, en vez del
        # "yo mismo" que usaria el alumno al ver su propia pantalla.
        resumen = obtener_resumen_dashboard(self.id_alumno)
        ultima = obtener_ultima_medicion(self.id_alumno)
        imc, rango_imc = calcular_imc(
            ultima["peso"] if ultima else 0,
            ultima["altura"] if ultima else 0,
        )

        fila_tarjetas = ctk.CTkFrame(contenedor, fg_color="white")
        fila_tarjetas.pack(fill="x", pady=(0, 20))

        crear_tarjeta_metrica(
            fila_tarjetas, "Rutinas Completadas/mes", f"{resumen['rutinas_mes']} Rutinas", ancho=170
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Peso Actual", f"{resumen['peso_actual']}kg", ancho=170
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "Racha Actual", f"{resumen['racha_dias']} Dias", ancho=170
        ).pack(side="left", padx=(0, 15))

        crear_tarjeta_metrica(
            fila_tarjetas, "IMC", str(imc), subtexto=rango_imc, ancho=170
        ).pack(side="left")

        ctk.CTkLabel(
            contenedor, text="Grafica - Peso", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        mediciones = obtener_progreso_peso(self.id_alumno)
        crear_grafica_peso(contenedor, mediciones).pack(fill="both", expand=True, pady=(0, 15))

        ctk.CTkLabel(
            contenedor, text="Historial Reciente De Entrenamientos", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        historial = obtener_historial_entrenamientos(self.id_alumno)
        if not historial:
            ctk.CTkLabel(contenedor, text="Aun no tiene entrenamientos registrados",
                         text_color="gray").pack(anchor="w")
        else:
            for registro in historial:
                nombre_completo = f"{registro['nombre']} {registro['ap_paterno']}"
                texto = (
                    f"{nombre_completo} - {registro['nombre_rutina']} - "
                    f"{registro['fecha_inicio'].strftime('%d/%m/%Y')} - {registro['lugar']} - {registro['tipo_estado']}"
                )
                fila = ctk.CTkFrame(contenedor, fg_color="#F5F5F5", corner_radius=8)
                fila.pack(fill="x", pady=3)
                ctk.CTkLabel(fila, text=texto, text_color="black", anchor="w").pack(
                    fill="x", padx=10, pady=8)
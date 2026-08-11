"""
Vista 'Mi Perfil' del Alumno: ver y editar sus datos personales (en
cajas grises, como el mockup), cambiar su foto de perfil, y cambiar su
contrasenia.
"""
import customtkinter as ctk

# "filedialog" abre la ventana NATIVA del sistema operativo para
# elegir un archivo (la misma que se abre en cualquier programa
# cuando dices "Abrir archivo..."). Es parte de tkinter.
from tkinter import messagebox, filedialog, simpledialog

from utilidades.componentes import crear_encabezado, crear_avatar
from utilidades.estilos import COLOR_FONDO_CAMPO, COLOR_BORDE
from utilidades.imagenes import guardar_foto_perfil
from modelos.usuario_modelo import obtener_datos_perfil, actualizar_datos_perfil, cambiar_contrasena
from modelos.alumno_modelo import actualizar_foto_alumno


class VistaMiPerfilAlumno(ctk.CTkFrame):
    def __init__(self, master, id_usuario, id_alumno, al_guardar=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_usuario = id_usuario
        self.id_alumno = id_alumno

        # "al_guardar" es un CALLBACK (mismo patron que ya vimos en
        # principal.py): la barra lateral (VistaMenuAlumno) le pasa su
        # propia funcion "_refrescar_datos_perfil" a esta vista, para
        # que la llame cada vez que se guarde un cambio (nombre nuevo,
        # foto nueva), y asi el chip de la barra lateral se actualice
        # tambien, sin que esta vista necesite saber nada de como
        # funciona esa barra lateral por dentro.
        self.al_guardar = al_guardar

        # "_nueva_contrasena" empieza en None: es donde se va a
        # "guardar temporalmente" la nueva contrasenia que el alumno
        # escriba en el dialogo de "Nueva contrasenia", ANTES de que
        # de clic en "Cambiar Contrasenia" para confirmarla de verdad.
        self._nueva_contrasena = None

        self._construir_interfaz()

    def _construir_interfaz(self):
        crear_encabezado(self, "Mi Perfil")

        cuerpo = ctk.CTkFrame(self, fg_color="white")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        # "obtener_datos_perfil(...) or {}": si por alguna razon la
        # funcion devuelve None (por ejemplo, un problema de conexion),
        # se usa un diccionario VACIO como respaldo, para que el resto
        # del codigo pueda seguir usando "datos.get(...)" sin tronar
        # por intentar leer de un None.
        datos = obtener_datos_perfil(self.id_usuario) or {}

        # "datos.get('nombre','')" es distinto a "datos['nombre']": si
        # la llave "nombre" no existiera en el diccionario, ".get()"
        # devuelve el segundo valor (aqui, cadena vacia) EN VEZ DE
        # lanzar un error. Se usa este patron en TODO el archivo
        # porque, si "datos" quedo vacio (por el "or {}" de arriba),
        # cualquier ".get()" sigue funcionando sin problemas.
        nombre_completo = (
            f"{datos.get('nombre','')} {datos.get('ap_paterno','')} "
            f"{datos.get('ap_materno','')}"
        ).strip()

        # --- Fila superior: foto + nombre/datos de contacto ---
        fila_encabezado = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_encabezado.pack(fill="x", pady=(0, 20))

        # Se llama a la funcion reutilizable crear_avatar (de
        # componentes.py), que devuelve 2 cosas: el widget a mostrar, y
        # la imagen (que se guarda en "self._imagen_avatar" para que no
        # se borre de memoria, tal como explica el docstring de esa
        # funcion).
        widget_avatar, self._imagen_avatar = crear_avatar(
            fila_encabezado, nombre_completo or datos.get("correo", ""),
            ruta_foto=datos.get("foto", ""), tamanio=64,
        )
        widget_avatar.pack(side="left", padx=(0, 15))

        columna_texto = ctk.CTkFrame(fila_encabezado, fg_color="white")
        columna_texto.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            columna_texto, text=nombre_completo, text_color="black",
            font=ctk.CTkFont(size=16, weight="bold"), anchor="w",
        ).pack(fill="x")

        subtexto = f"{datos.get('correo','')} · {datos.get('telefono','')} · {datos.get('fecha_registro','')}"
        ctk.CTkLabel(columna_texto, text=subtexto, text_color="gray", anchor="w").pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            columna_texto, text="Cambiar Foto", fg_color="#E5E5E5", text_color="black",
            hover_color="#D5D5D5", width=120, command=self._cambiar_foto,
        ).pack(anchor="w")

        # --- Fila 1: nombre, apellido paterno, apellido materno, correo ---
        fila1 = ctk.CTkFrame(cuerpo, fg_color="white")
        fila1.pack(fill="x", pady=(0, 10))

        # Se crean 4 cajas grises seguidas, usando la funcion
        # _crear_caja (definida abajo en este mismo archivo), y se
        # guarda cada Entry en un atributo de "self" (self.campo_X),
        # para poder leer su valor DESPUES, cuando el alumno de clic en
        # "Guardar Cambios".
        self.campo_nombre = self._crear_caja(fila1, datos.get("nombre", ""), placeholder="Nombre")
        self.campo_ap_paterno = self._crear_caja(fila1, datos.get("ap_paterno", ""), placeholder="Apellido paterno")
        self.campo_ap_materno = self._crear_caja(fila1, datos.get("ap_materno", ""), placeholder="Apellido materno")
        self.campo_correo = self._crear_caja(fila1, datos.get("correo", ""), placeholder="Correo electronico")

        # --- Fila 2: telefono, fecha de nacimiento ---
        fila2 = ctk.CTkFrame(cuerpo, fg_color="white")
        fila2.pack(fill="x", pady=(0, 15))

        self.campo_telefono = self._crear_caja(fila2, datos.get("telefono", ""), placeholder="Telefono")
        self.campo_fecha_nacimiento = self._crear_caja(
            fila2, datos.get("fecha_nacimiento", ""), placeholder="Fecha nacimiento (AAAA-MM-DD)")

        # Linea divisoria horizontal: un CTkFrame SIN nada adentro,
        # con 1 pixel de alto y color gris. Es la forma mas simple de
        # dibujar una "raya" separadora en tkinter (no existe un
        # widget especial de "linea horizontal").
        ctk.CTkFrame(cuerpo, fg_color="#CCCCCC", height=1).pack(fill="x", pady=(0, 15))

        # --- Seccion Seguridad ---
        ctk.CTkLabel(
            cuerpo, text="Seguridad", text_color="black",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 8))

        fila_seguridad = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_seguridad.pack(fill="x", pady=(0, 20))

        # Este campo NUNCA muestra la contrasenia real: siempre trae
        # el texto fijo de asteriscos, y esta DESHABILITADO
        # ("state='disabled'") para que ni siquiera se pueda escribir
        # ahi directamente. Es puramente visual/decorativo, para que se
        # vea "algo" en ese espacio, tal como en el mockup.
        self.campo_contrasena_display = ctk.CTkEntry(
            fila_seguridad, width=500, fg_color=COLOR_FONDO_CAMPO, border_width=1,
            border_color=COLOR_BORDE, text_color="black", justify="center",
        )
        self.campo_contrasena_display.insert(0, "***********")
        self.campo_contrasena_display.configure(state="disabled")
        self.campo_contrasena_display.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_seguridad, text="Nueva contrasenia", fg_color="#E5E5E5", text_color="black",
            hover_color="#D5D5D5", command=self._pedir_nueva_contrasena,
        ).pack(side="left")

        # --- Botones finales ---
        fila_botones = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_botones.pack(fill="x")

        ctk.CTkButton(
            fila_botones, text="Guardar Cambios", fg_color="black",
            hover_color="#333333", command=self._guardar_cambios,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_botones, text="Cambiar Contrasenia", fg_color="#E5E5E5", text_color="black",
            hover_color="#D5D5D5", command=self._cambiar_contrasena,
        ).pack(side="left")

    def _crear_caja(self, contenedor, valor, ancho=200, placeholder=""):
        """Crea una cajita gris (como las del mockup) con el valor ya
        adentro. Si el campo esta vacio, muestra 'placeholder' como
        texto de ayuda (ej. 'Telefono'), para que se sepa que dato va
        ahi. Devuelve el Entry."""
        entrada = ctk.CTkEntry(
            contenedor, width=ancho, fg_color=COLOR_FONDO_CAMPO, border_width=1,
            border_color=COLOR_BORDE, text_color="black", justify="center",
            placeholder_text=placeholder,
        )
        # "entrada.insert(0, valor or '')": se inserta el valor
        # empezando en la posicion 0 (osea, al principio del campo, que
        # esta vacio recien creado). "valor or ''" evita insertar la
        # palabra "None" como texto, si "valor" viniera como None en
        # vez de una cadena vacia.
        entrada.insert(0, valor or "")
        entrada.pack(side="left", padx=(0, 8))
        return entrada

    def _cambiar_foto(self):
        # "filedialog.askopenfilename(...)" abre el explorador de
        # archivos de Windows/Mac, filtrado para mostrar solo
        # imagenes (segun la lista de extensiones en "filetypes").
        # Devuelve la ruta completa del archivo elegido, o una cadena
        # VACIA si el usuario cerro la ventana sin elegir nada.
        ruta_elegida = filedialog.askopenfilename(
            title="Elige tu foto de perfil",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.webp"), ("Todos los archivos", "*.*")],
        )
        if not ruta_elegida:
            # Si el alumno cancelo el dialogo, no hay nada que hacer:
            # se sale de la funcion sin mostrar ningun error (cancelar
            # es una accion valida, no un fallo).
            return

        # Se le pide a utilidades/imagenes.py que copie el archivo
        # elegido a la carpeta del proyecto, y devuelva la ruta
        # RELATIVA que hay que guardar en la base de datos.
        ruta_relativa = guardar_foto_perfil(ruta_elegida)

        # Se guarda esa ruta en la tabla "alumno".
        exito = actualizar_foto_alumno(self.id_alumno, ruta_relativa)

        if not exito:
            messagebox.showerror("Error", "No se pudo guardar la foto de perfil.")
            return

        messagebox.showinfo("Listo", "Tu foto de perfil se actualizo.")

        # Se destruye TODO lo que hay actualmente en esta vista, y se
        # vuelve a construir desde cero llamando otra vez a
        # _construir_interfaz(). Esto es necesario porque la foto
        # nueva no aparece "sola": hay que volver a llamar a
        # crear_avatar() con la ruta actualizada para que se vea el
        # cambio.
        for widget in self.winfo_children():
            widget.destroy()
        self._construir_interfaz()

        # Se avisa al "padre" (la barra lateral) que algo cambio, para
        # que ella tambien actualice su propio chip con la foto nueva.
        if self.al_guardar:
            self.al_guardar()

    def _guardar_cambios(self):
        # Se leen los valores actuales de cada campo de texto.
        # ".get()" trae el texto que hay escrito en el Entry en este
        # momento, y ".strip()" le quita espacios en blanco sueltos al
        # principio/final (por si el alumno escribio " Juan " con
        # espacios de mas por accidente).
        nombre = self.campo_nombre.get().strip()
        ap_paterno = self.campo_ap_paterno.get().strip()
        ap_materno = self.campo_ap_materno.get().strip()
        correo = self.campo_correo.get().strip()
        telefono = self.campo_telefono.get().strip()

        # "or None": si el campo de fecha de nacimiento quedo vacio, se
        # guarda None (NULL en MySQL) en vez de una cadena vacia, ya
        # que la columna fecha_nacimiento es de tipo DATE (MySQL no
        # acepta una cadena vacia como fecha valida, pero SI acepta
        # NULL si la columna lo permite).
        fecha_nacimiento = self.campo_fecha_nacimiento.get().strip() or None

        # Validacion basica ANTES de mandar nada a la base de datos:
        # si falta cualquiera de estos 3 campos obligatorios, se avisa
        # y no se sigue adelante.
        if not nombre or not ap_paterno or not correo:
            messagebox.showwarning(
                "Datos incompletos", "Nombre, apellido paterno y correo son obligatorios.")
            return

        exito = actualizar_datos_perfil(
            self.id_usuario, self.id_alumno, nombre, ap_paterno, ap_materno,
            correo, telefono, fecha_nacimiento,
        )
        if exito:
            messagebox.showinfo("Listo", "Tus datos se guardaron correctamente.")
            if self.al_guardar:
                self.al_guardar()
        else:
            messagebox.showerror("Error", "No se pudieron guardar los cambios.")

    def _pedir_nueva_contrasena(self):
        nueva = simpledialog.askstring(
            "Nueva contrasenia", "Escribe tu nueva contrasenia:", show="*", parent=self,
        )
        # Si el alumno SI escribio algo (y no cancelo el dialogo), se
        # guarda temporalmente en "self._nueva_contrasena". OJO: en
        # este punto TODAVIA no se cambia nada en la base de datos —
        # eso solo pasa cuando se de clic en "Cambiar Contrasenia".
        if nueva:
            self._nueva_contrasena = nueva.strip()
            messagebox.showinfo(
                "Listo", "Ahora da clic en 'Cambiar Contrasenia' para confirmarla.")

    def _cambiar_contrasena(self):
        # Si el alumno nunca uso "Nueva contrasenia" (self._nueva_
        # contrasena sigue en None), se le avisa que falta ese paso
        # antes de intentar cualquier cosa.
        if not self._nueva_contrasena:
            messagebox.showwarning(
                "Falta la nueva contrasenia", "Primero da clic en 'Nueva contrasenia'.")
            return

        exito = cambiar_contrasena(self.id_usuario, self._nueva_contrasena)
        if exito:
            messagebox.showinfo("Listo", "Contrasenia actualizada correctamente.")
            # Se vuelve a poner en None despues de usarla, para evitar
            # que, si el alumno vuelve a dar clic en "Cambiar
            # Contrasenia" por accidente (sin pedir una nueva primero),
            # se intente reusar la misma contrasenia vieja otra vez.
            self._nueva_contrasena = None
        else:
            messagebox.showerror("Error", "No se pudo cambiar la contrasenia.")
"""
Vista 'Mi Perfil' del Profesional: ver y editar sus datos personales
(en cajas grises, como el mockup), cambiar su foto de perfil, y
cambiar su contrasenia.

Mismo patron que vistas/alumno/vista_mi_perfil.py, solo que aqui se
usan las funciones de profesional_modelo.py en vez de alumno_modelo.py.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog

from utilidades.componentes import crear_encabezado, crear_avatar
from utilidades.estilos import COLOR_FONDO_CAMPO, COLOR_BORDE
from utilidades.imagenes import guardar_foto_perfil

# Aqui esta la diferencia clave con la version del Alumno: "cambiar_
# contrasena" SI se sigue importando de usuario_modelo (porque la
# contrasenia vive en la tabla "usuario", sin importar el rol), pero
# "obtener_datos_perfil" y "actualizar_datos_perfil" ya NO vienen de
# usuario_modelo (esos eran especificos de la tabla "alumno") — en su
# lugar, se usan sus equivalentes de profesional_modelo.py.
from modelos.usuario_modelo import cambiar_contrasena
from modelos.profesional_modelo import (
    obtener_datos_perfil_profesional,
    actualizar_datos_perfil_profesional,
    actualizar_foto_profesional,
)


class VistaMiPerfilProfesional(ctk.CTkFrame):
    def __init__(self, master, id_usuario, id_profesional, al_guardar=None):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_usuario = id_usuario
        # Se guarda "id_profesional" (no "id_alumno" como en la otra
        # version), porque las funciones de profesional_modelo.py
        # trabajan con ese identificador para saber a que fila de la
        # tabla "profesional" hay que actualizar.
        self.id_profesional = id_profesional

        # Mismo callback que en la version del Alumno: la barra
        # lateral (VistaMenuProfesional) le pasa su propio metodo de
        # refresco, para poder actualizar el chip cuando algo cambie
        # aqui.
        self.al_guardar = al_guardar

        # Mismo mecanismo de "confirmacion en 2 pasos" para la
        # contrasenia que ya vimos en el Alumno.
        self._nueva_contrasena = None

        self._construir_interfaz()

    def _construir_interfaz(self):
        crear_encabezado(self, "Mi Perfil")

        cuerpo = ctk.CTkFrame(self, fg_color="white")
        cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        # Se usa la funcion de PROFESIONAL, que hace un JOIN entre
        # "usuario" y "profesional" (en vez de "usuario" y "alumno").
        datos = obtener_datos_perfil_profesional(self.id_usuario) or {}

        nombre_completo = (
            f"{datos.get('nombre','')} {datos.get('ap_paterno','')} "
            f"{datos.get('ap_materno','')}"
        ).strip()

        # --- Fila superior: foto + nombre/datos de contacto ---
        fila_encabezado = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_encabezado.pack(fill="x", pady=(0, 20))

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

        self.campo_nombre = self._crear_caja(fila1, datos.get("nombre", ""), placeholder="Nombre")
        self.campo_ap_paterno = self._crear_caja(fila1, datos.get("ap_paterno", ""), placeholder="Apellido paterno")
        self.campo_ap_materno = self._crear_caja(fila1, datos.get("ap_materno", ""), placeholder="Apellido materno")
        self.campo_correo = self._crear_caja(fila1, datos.get("correo", ""), placeholder="Correo electronico")

        # --- Fila 2: telefono (SOLO este campo, a diferencia del Alumno) ---
        fila2 = ctk.CTkFrame(cuerpo, fg_color="white")
        fila2.pack(fill="x", pady=(0, 15))

        # Aqui esta la diferencia visible mas importante con la vista
        # del Alumno: no existe un "self.campo_fecha_nacimiento",
        # porque la tabla "profesional" no tiene esa columna (no tiene
        # sentido pedirle su fecha de nacimiento a un entrenador para
        # este sistema).
        self.campo_telefono = self._crear_caja(fila2, datos.get("telefono", ""), placeholder="Telefono")

        # Linea divisoria (igual que en la version del Alumno).
        ctk.CTkFrame(cuerpo, fg_color="#CCCCCC", height=1).pack(fill="x", pady=(0, 15))

        # --- Seccion Seguridad (identica a la del Alumno) ---
        ctk.CTkLabel(
            cuerpo, text="Seguridad", text_color="black",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 8))

        fila_seguridad = ctk.CTkFrame(cuerpo, fg_color="white")
        fila_seguridad.pack(fill="x", pady=(0, 20))

        # Igual que en el Alumno: un campo deshabilitado que SOLO
        # muestra asteriscos, nunca la contrasenia real.
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
        """Crea una cajita gris con el valor ya adentro, mostrando
        'placeholder' como texto de ayuda cuando el campo esta vacio."""
        entrada = ctk.CTkEntry(
            contenedor, width=ancho, fg_color=COLOR_FONDO_CAMPO, border_width=1,
            border_color=COLOR_BORDE, text_color="black", justify="center",
            placeholder_text=placeholder,
        )
        entrada.insert(0, valor or "")
        entrada.pack(side="left", padx=(0, 8))
        return entrada

    def _cambiar_foto(self):
        # Mismo flujo que en el Alumno: abrir el explorador de
        # archivos, dejar que el usuario elija una imagen o cancele.
        ruta_elegida = filedialog.askopenfilename(
            title="Elige tu foto de perfil",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.webp"), ("Todos los archivos", "*.*")],
        )
        if not ruta_elegida:
            return

        # Se copia el archivo a la carpeta del proyecto (utilidades/
        # imagenes.py, la misma funcion que usa el Alumno; no hay
        # diferencia entre guardar una foto de alumno o de profesional
        # a este nivel, ambas son "una foto de perfil").
        ruta_relativa = guardar_foto_perfil(ruta_elegida)

        # Aqui SI cambia la funcion: se guarda en la tabla
        # "profesional" (no "alumno"), usando su id_profesional.
        exito = actualizar_foto_profesional(self.id_profesional, ruta_relativa)

        if not exito:
            messagebox.showerror("Error", "No se pudo guardar la foto de perfil.")
            return

        messagebox.showinfo("Listo", "Tu foto de perfil se actualizo.")

        # Se reconstruye toda la vista desde cero, para que se vea la
        # foto nueva (mismo patron que el Alumno).
        for widget in self.winfo_children():
            widget.destroy()
        self._construir_interfaz()

        if self.al_guardar:
            self.al_guardar()

    def _guardar_cambios(self):
        nombre = self.campo_nombre.get().strip()
        ap_paterno = self.campo_ap_paterno.get().strip()
        ap_materno = self.campo_ap_materno.get().strip()
        correo = self.campo_correo.get().strip()
        telefono = self.campo_telefono.get().strip()

        # Misma validacion basica: nombre, apellido paterno y correo
        # son obligatorios. Nota que aqui NO hay validacion de fecha de
        # nacimiento (porque ese campo ni siquiera existe en esta
        # pantalla).
        if not nombre or not ap_paterno or not correo:
            messagebox.showwarning(
                "Datos incompletos", "Nombre, apellido paterno y correo son obligatorios.")
            return

        # Se llama a la funcion de PROFESIONAL (que por dentro hace 2
        # UPDATE: uno a "profesional", otro a "usuario" para el
        # correo, tal como vimos en profesional_modelo.py).
        exito = actualizar_datos_perfil_profesional(
            self.id_usuario, self.id_profesional, nombre, ap_paterno, ap_materno, correo, telefono,
        )
        if exito:
            messagebox.showinfo("Listo", "Tus datos se guardaron correctamente.")
            if self.al_guardar:
                self.al_guardar()
        else:
            messagebox.showerror("Error", "No se pudieron guardar los cambios.")

    def _pedir_nueva_contrasena(self):
        # Identico al Alumno: se pide el texto con un dialogo simple,
        # y se guarda TEMPORALMENTE (todavia no se aplica de verdad).
        nueva = simpledialog.askstring(
            "Nueva contrasenia", "Escribe tu nueva contrasenia:", show="*", parent=self,
        )
        if nueva:
            self._nueva_contrasena = nueva.strip()
            messagebox.showinfo(
                "Listo", "Ahora da clic en 'Cambiar Contrasenia' para confirmarla.")

    def _cambiar_contrasena(self):
        if not self._nueva_contrasena:
            messagebox.showwarning(
                "Falta la nueva contrasenia", "Primero da clic en 'Nueva contrasenia'.")
            return

        # "cambiar_contrasena" es la MISMA funcion que usa el Alumno
        # (viene de usuario_modelo.py, no de profesional_modelo.py),
        # porque la contrasenia vive en la tabla "usuario", que es
        # compartida por los 3 roles.
        exito = cambiar_contrasena(self.id_usuario, self._nueva_contrasena)
        if exito:
            messagebox.showinfo("Listo", "Contrasenia actualizada correctamente.")
            self._nueva_contrasena = None
        else:
            messagebox.showerror("Error", "No se pudo cambiar la contrasenia.")
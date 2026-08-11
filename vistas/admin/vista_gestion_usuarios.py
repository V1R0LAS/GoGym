"""
Vista 'Gestion de Usuarios' del Administrador: buscar/filtrar cuentas,
crear cuentas nuevas, cambiar el Estado y reasignar el Profesional
directamente desde la tabla (como en el mockup original), y
restablecer contrasenias.
Responsabilidad Unica: esta clase solo dibuja la pantalla y reacciona
a los clics. Toda la logica de negocio vive en admin_modelo.py.
"""
import customtkinter as ctk

from tkinter import messagebox, simpledialog

from utilidades.componentes import crear_encabezado
from utilidades.ventanas import aplicar_icono
from utilidades.estilos import COLOR_FONDO_CAMPO, COLOR_BORDE, COLOR_ROJO

from modelos.admin_modelo import (
    listar_usuarios,
    crear_cuenta,
    establecer_estado_usuario,
    reasignar_profesional_alumno,
    restablecer_contrasena,
    listar_profesionales_disponibles,
)

TIPOS_CUENTA = ["Alumno", "Profesional", "Administrador"]
FILTROS_ROL = ["Todos", "Alumno", "Profesional", "Administrador"]


SIN_ASIGNAR = "-"
ESTADOS_POSIBLES = ["Activo", "Inactivo"]
ESTILO_OPCION_MENU = dict(
    fg_color="black", button_color="black", button_hover_color="#333333",
    dropdown_fg_color="white", dropdown_text_color="black", text_color="white",
)


class VistaGestionUsuarios(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white", corner_radius=0)

        crear_encabezado(self, "Gestion De Usuarios")

        self.cuerpo = ctk.CTkFrame(self, fg_color="white")
        self.cuerpo.pack(fill="both", expand=True, padx=30, pady=20)
        self._construir_barra_superior()

        self._area_tabla = ctk.CTkScrollableFrame(self.cuerpo, fg_color="white")
        self._area_tabla.pack(fill="both", expand=True, pady=(15, 0))

        self._dibujar_tabla()

    # Barra superior: buscador, filtro por rol, boton +Cuenta

    def _construir_barra_superior(self):
        fila_busqueda = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila_busqueda.pack(fill="x")

        self.campo_busqueda = ctk.CTkEntry(
            fila_busqueda, placeholder_text="Buscar nombre del usuario", height=36,
            corner_radius=8, border_width=1, border_color=COLOR_BORDE, fg_color=COLOR_FONDO_CAMPO,
        )
        self.campo_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.campo_busqueda.bind("<Return>", lambda evento: self._dibujar_tabla())

        self.filtro_rol = ctk.CTkOptionMenu(
            fila_busqueda, values=FILTROS_ROL, width=140, height=36,
            command=lambda valor: self._dibujar_tabla(), **ESTILO_OPCION_MENU,
        )
        self.filtro_rol.set("Todos")
        self.filtro_rol.pack(side="left")

        fila_boton = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila_boton.pack(fill="x", pady=(15, 0))

        ctk.CTkButton(
            fila_boton, text="+ Cuenta", fg_color="black", hover_color="#333333",
            width=110, command=self._abrir_formulario_creacion,
        ).pack(side="left")

    # Ventana emergente: crear una cuenta nueva

    def _abrir_formulario_creacion(self):
        
        ventana = ctk.CTkToplevel(self)
        aplicar_icono(ventana)
        ventana.title("Nueva Cuenta")
        ventana.geometry("400x600")
        ventana.minsize(360, 400)
        ventana.configure(fg_color="white")

  
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()


        contenido = ctk.CTkScrollableFrame(ventana, fg_color="white")
        contenido.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(contenido, text="Nueva Cuenta", text_color="black",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(contenido, text="Tipo de cuenta", text_color="#333333", anchor="w").pack(fill="x")
        combo_tipo_cuenta = ctk.CTkOptionMenu(
            contenido, values=TIPOS_CUENTA,
       
            command=lambda valor: self._al_cambiar_tipo_cuenta(valor, campos),
            **ESTILO_OPCION_MENU,
        )
        combo_tipo_cuenta.pack(fill="x", pady=(2, 12))


        campos = {
            "nombre": self._agregar_campo(contenido, "Nombre"),
            "ap_paterno": self._agregar_campo(contenido, "Apellido paterno"),
            "ap_materno": self._agregar_campo(contenido, "Apellido materno (opcional)"),
            "correo": self._agregar_campo(contenido, "Correo electronico"),
            "telefono": self._agregar_campo(contenido, "Telefono (opcional)"),
            "contrasena": self._agregar_campo(contenido, "Contrasenia inicial", ocultar=True),
        }

        ctk.CTkButton(
            contenido, text="Crear Cuenta", fg_color="black", hover_color="#333333",
            command=lambda: self._crear_cuenta(ventana, campos, combo_tipo_cuenta),
        ).pack(fill="x", pady=(20, 0))

    def _agregar_campo(self, contenedor, etiqueta, ocultar=False):
        """Crea una etiqueta + un CTkEntry debajo, y devuelve el Entry."""
        ctk.CTkLabel(contenedor, text=etiqueta, text_color="#333333", anchor="w").pack(fill="x", pady=(4, 0))
        entrada = ctk.CTkEntry(
            contenedor,
    
            show="*" if ocultar else None, height=34, corner_radius=8,
            border_width=1, border_color=COLOR_BORDE, fg_color="white",
        )
        entrada.pack(fill="x", pady=(2, 0))
        return entrada

    def _al_cambiar_tipo_cuenta(self, tipo_elegido, campos):
        """Si el tipo es 'Administrador', no hay tabla de detalle donde
        guardar nombre/apellidos/telefono, asi que se deshabilitan."""
        estado_campos = "disabled" if tipo_elegido == "Administrador" else "normal"
 
        for clave in ("nombre", "ap_paterno", "ap_materno", "telefono"):
            campos[clave].configure(state=estado_campos)

    def _crear_cuenta(self, ventana, campos, combo_tipo_cuenta):
        """Se llama al dar clic en 'Crear Cuenta'."""
        rol = combo_tipo_cuenta.get()
        nombre = campos["nombre"].get().strip()
        ap_paterno = campos["ap_paterno"].get().strip()
        ap_materno = campos["ap_materno"].get().strip()
        correo = campos["correo"].get().strip()
        telefono = campos["telefono"].get().strip()
        contrasena = campos["contrasena"].get().strip()

        exito, mensaje_error = crear_cuenta(rol, nombre, ap_paterno, ap_materno, correo, telefono, contrasena)

        if not exito:
         
            messagebox.showerror("No se pudo crear la cuenta", mensaje_error, parent=ventana)
            return

        messagebox.showinfo("Listo", f"Cuenta de {rol} creada correctamente.", parent=ventana)
        ventana.destroy()
   
        self._dibujar_tabla()

    # Tabla de usuarios
    def _dibujar_tabla(self):
        """Vuelve a dibujar toda la tabla (se llama al buscar, filtrar,
        crear una cuenta, o cambiar estado/profesional)."""
     
        for widget in self._area_tabla.winfo_children():
            widget.destroy()

        encabezado = ctk.CTkFrame(self._area_tabla, fg_color="#EFEFEF", corner_radius=6)
        encabezado.pack(fill="x", pady=(0, 4))
 
        for texto, ancho in [("Nombre", 160), ("Correo", 170), ("Rol", 95),
                              ("Estado", 110), ("Profesional", 150)]:
            ctk.CTkLabel(encabezado, text=texto, text_color="black",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         width=ancho, anchor="w").pack(side="left", padx=5, pady=8)
  
        ctk.CTkLabel(encabezado, text="Acciones", text_color="black",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     anchor="w").pack(side="left", padx=5, pady=8)

        busqueda = self.campo_busqueda.get().strip()
        filtro = self.filtro_rol.get()
        usuarios = listar_usuarios(busqueda, filtro)

        if not usuarios:
            ctk.CTkLabel(self._area_tabla, text="No se encontraron usuarios",
                         text_color="gray").pack(pady=15)
            return

        profesionales_disponibles = listar_profesionales_disponibles()

        for usuario in usuarios:
            self._dibujar_fila_usuario(usuario, profesionales_disponibles)

    def _dibujar_fila_usuario(self, usuario, profesionales_disponibles):
        fila = ctk.CTkFrame(self._area_tabla, fg_color="white", border_width=1,
                            border_color="#EEEEEE", corner_radius=6)
        fila.pack(fill="x", pady=2)

        ctk.CTkLabel(fila, text=usuario["nombre_completo"] or "-", text_color="black",
                     width=160, anchor="w").pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(fila, text=usuario["correo"], text_color="black",
                     width=170, anchor="w").pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(fila, text=usuario["rol"], text_color="black",
                     width=95, anchor="w").pack(side="left", padx=5, pady=8)

        # --- Estado: dropdown que aplica el cambio de inmediato ---
        combo_estado = ctk.CTkOptionMenu(
            fila, values=ESTADOS_POSIBLES, width=100, height=28,
     
            command=lambda valor: self._cambiar_estado(usuario["id_usuario"], valor),
            **ESTILO_OPCION_MENU,
        )
        combo_estado.set(usuario["estado"])
        combo_estado.pack(side="left", padx=5, pady=8)

        if usuario["rol"] == "Alumno":
       
            opciones_profesional = [SIN_ASIGNAR] + [p["nombre_completo"] for p in profesionales_disponibles]
            combo_profesional = ctk.CTkOptionMenu(
                fila, values=opciones_profesional, width=140, height=28,
                command=lambda valor: self._reasignar_profesional(
                    usuario["id_detalle_alumno"], valor, profesionales_disponibles),
                **ESTILO_OPCION_MENU,
            )
     
            combo_profesional.set(usuario["profesional_asignado"] or SIN_ASIGNAR)
            combo_profesional.pack(side="left", padx=5, pady=8)
        else:
          
            ctk.CTkLabel(fila, text="-", text_color="black", width=140, anchor="w").pack(
                side="left", padx=5, pady=8)

        self._crear_enlace(fila, "Restablecer contrasenia", lambda: self._restablecer_contrasena(usuario["id_usuario"]))

    def _crear_enlace(self, parent, texto, comando):
        """Boton estilizado como un enlace de texto en rojo (igual que
        'Actualizar / Desactivar / Restablecer contrasenia' del mockup),
        en vez de un boton gris tradicional."""
 
        enlace = ctk.CTkButton(
            parent, text=texto, fg_color="white", text_color=COLOR_ROJO,
            hover_color="#F5F5F5", corner_radius=0, border_width=0,
            font=ctk.CTkFont(size=12, underline=True), command=comando,
        )
        enlace.pack(side="left", padx=8, pady=8)
        return enlace

    def _cambiar_estado(self, id_usuario, nuevo_estado):
        """Se llama al cambiar el dropdown de Estado en la tabla."""
        exito = establecer_estado_usuario(id_usuario, nuevo_estado)
        if not exito:
            messagebox.showerror("Error", "No se pudo actualizar el estado de la cuenta.")
     
        self._dibujar_tabla()

    def _reasignar_profesional(self, id_alumno, nombre_elegido, profesionales_disponibles):
        """Se llama al cambiar el dropdown de Profesional en la tabla."""
        id_profesional = None
        if nombre_elegido != SIN_ASIGNAR:
         
            for profesional in profesionales_disponibles:
                if profesional["nombre_completo"] == nombre_elegido:
                    id_profesional = profesional["id_profesional"]
             
                    break

        exito = reasignar_profesional_alumno(id_alumno, id_profesional)
        if not exito:
            messagebox.showerror("Error", "No se pudo reasignar el profesional.")
        self._dibujar_tabla()

    def _restablecer_contrasena(self, id_usuario):
        """Pide la nueva contrasenia con un dialogo simple de texto."""
       
        nueva = simpledialog.askstring(
            "Restablecer contrasenia", "Escribe la nueva contrasenia para esta cuenta:",
            show="*", parent=self,
        )
        if not nueva:
      
            return

        exito = restablecer_contrasena(id_usuario, nueva.strip())
        if exito:
            messagebox.showinfo("Listo", "Contrasenia restablecida correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo restablecer la contrasenia.")
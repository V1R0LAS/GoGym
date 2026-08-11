"""
Vista 'Mis Rutinas' del Alumno: muestra la rutina pendiente segun la
pestania elegida (Casa/Gimnasio), permite marcarla como completada, y
muestra el historial reciente de entrenamientos.
"""
import customtkinter as ctk
from tkinter import messagebox

from utilidades.componentes import crear_encabezado
from utilidades.ventanas import aplicar_icono
from utilidades.animaciones import crear_reproductor_gif
from modelos.alumno_modelo import (
    obtener_rutina_pendiente,
    marcar_rutina_completada,
    obtener_historial_entrenamientos,
)


class VistaMisRutinas(ctk.CTkFrame):
    def __init__(self, master, id_alumno):
        super().__init__(master, fg_color="white", corner_radius=0)
        self.id_alumno = id_alumno

        # "tipo_seleccionado" recuerda cual de las 2 pestanias (Casa o
        # Gimnasio) esta activa en este momento. Empieza en "Casa" por
        # defecto, la primera vez que se abre la pantalla.
        self.tipo_seleccionado = "Casa"

        # "_rutina_pendiente_id" guarda el id_rutina de la rutina que
        # se esta mostrando AHORA MISMO (si hay alguna pendiente). Se
        # necesita guardado aparte porque el boton "Marcar como
        # Completada" lo usa DESPUES, cuando el alumno le da clic, y
        # para entonces ya no se tiene a la mano el diccionario
        # completo de la rutina (solo su id).
        self._rutina_pendiente_id = None

        crear_encabezado(self, "Mis Rutinas")

        self.cuerpo = ctk.CTkFrame(self, fg_color="white")
        self.cuerpo.pack(fill="both", expand=True, padx=30, pady=20)

        self._dibujar_contenido()

    def _dibujar_contenido(self):
        for widget in self.cuerpo.winfo_children():
            widget.destroy()
        # Se reinicia a None cada vez que se vuelve a dibujar: si esta
        # vez SI hay una rutina pendiente, se le asignara su id un poco
        # mas abajo; si no, se queda en None, y el boton de "Marcar
        # como Completada" se deshabilita (mas abajo se ve como).
        self._rutina_pendiente_id = None

        # --- Pestanias Casa / Gimnasio ---
        fila_tabs = ctk.CTkFrame(self.cuerpo, fg_color="white")
        fila_tabs.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(
            fila_tabs, text="Casa", width=100,
            fg_color="black" if self.tipo_seleccionado == "Casa" else "#E5E5E5",
            text_color="white" if self.tipo_seleccionado == "Casa" else "black",
            command=lambda: self._cambiar_tipo("Casa"),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila_tabs, text="Gimnasio", width=100,
            fg_color="black" if self.tipo_seleccionado == "Gimnasio" else "#E5E5E5",
            text_color="white" if self.tipo_seleccionado == "Gimnasio" else "black",
            command=lambda: self._cambiar_tipo("Gimnasio"),
        ).pack(side="left")

        # Se pide la rutina de HOY para el tipo (Casa/Gimnasio) que
        # este seleccionado en este momento.
        rutina = obtener_rutina_pendiente(self.id_alumno, self.tipo_seleccionado)

        if rutina is None:
            # Si no hay ninguna rutina pendiente para hoy en ese lugar,
            # se muestra un mensaje explicando la situacion.
            ctk.CTkLabel(
                self.cuerpo, text=f"Sin rutina pendiente para {self.tipo_seleccionado}",
                text_color="gray", fg_color="#F5F5F5", corner_radius=8,
            ).pack(fill="x", pady=(0, 15), ipady=10)
        else:
            # Si SI hay una rutina, se guarda su id (para el boton de
            # "Marcar como Completada" de mas abajo), y se dibuja toda
            # la tarjeta con sus ejercicios.
            self._rutina_pendiente_id = rutina["id_rutina"]

            tarjeta = ctk.CTkFrame(self.cuerpo, fg_color="#F5F5F5", corner_radius=8)
            tarjeta.pack(fill="x", pady=(0, 15))

            ctk.CTkLabel(
                tarjeta,
                text=f"{rutina['nombre_rutina']} - {rutina['fecha_inicio'].strftime('%d/%m/%Y')}",
                text_color="black", font=ctk.CTkFont(weight="bold"), anchor="w",
            ).pack(fill="x", padx=10, pady=(10, 4))

            # Se recorre la lista de ejercicios de esta rutina, y por
            # cada uno se dibuja una fila con su texto + el boton de
            # ojo para ver la animacion.
            for ejercicio in rutina["ejercicios"]:
                fila_ejercicio = ctk.CTkFrame(tarjeta, fg_color="#F5F5F5")
                fila_ejercicio.pack(fill="x", padx=10, pady=2)

                texto = (
                    f"{ejercicio['nombre_ejercicio']}  -  {ejercicio['series']} series x "
                    f"{ejercicio['repeticiones_min']}-{ejercicio['repeticiones_max']} reps"
                )
                ctk.CTkLabel(fila_ejercicio, text=texto, text_color="#333333", anchor="w").pack(
                    side="left", padx=(10, 0), fill="x", expand=True)

                # "lambda ej=ejercicio: ...": este truco (asignar
                # "ejercicio" a un parametro por defecto "ej" de la
                # propia lambda) es MUY importante dentro de un ciclo
                # "for": sin el "ej=ejercicio", TODOS los botones de
                # ojo terminarian mostrando la animacion del ULTIMO
                # ejercicio del ciclo (un error clasico de Python con
                # lambdas dentro de bucles). Al "congelar" el valor de
                # "ejercicio" en el momento exacto en que se crea cada
                # boton, cada uno queda ligado a SU PROPIO ejercicio.
                ctk.CTkButton(
                    fila_ejercicio, text="👁", width=32, fg_color="#E5E5E5", text_color="black",
                    hover_color="#D5D5D5",
                    command=lambda ej=ejercicio: self._mostrar_animacion(ej),
                ).pack(side="left", padx=(5, 0))

            ctk.CTkLabel(tarjeta, text="", height=5).pack()

        # --- Boton Marcar como Completada ---
        ctk.CTkButton(
            self.cuerpo, text="Marcar como Completada", fg_color="black",
            hover_color="#333333",
            # "state='normal' if self._rutina_pendiente_id else
            # 'disabled'": el boton solo se puede presionar si de
            # verdad hay una rutina pendiente cargada ahorita. Si
            # "_rutina_pendiente_id" es None (no hay ninguna rutina
            # para hoy), el boton aparece "grisado"/deshabilitado, para
            # que no se pueda dar clic en algo que no tiene sentido.
            state="normal" if self._rutina_pendiente_id else "disabled",
            command=self._marcar_completada,
        ).pack(fill="x", pady=(0, 20))

        # --- Historial reciente ---
        ctk.CTkLabel(
            self.cuerpo, text="Historial Reciente De Entrenamientos", text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", pady=(0, 10))

        historial = obtener_historial_entrenamientos(self.id_alumno)
        if not historial:
            ctk.CTkLabel(self.cuerpo, text="Aun no tienes entrenamientos registrados",
                         text_color="gray").pack(anchor="w")
        else:
            for registro in historial:
                nombre_completo = f"{registro['nombre']} {registro['ap_paterno']}"
                texto = (
                    f"{nombre_completo} - {registro['nombre_rutina']} - "
                    f"{registro['fecha_inicio'].strftime('%d/%m/%Y')} - {registro['tipo_estado']}"
                )
                fila = ctk.CTkFrame(self.cuerpo, fg_color="#F5F5F5", corner_radius=8)
                fila.pack(fill="x", pady=3)
                ctk.CTkLabel(fila, text=texto, text_color="black", anchor="w").pack(
                    fill="x", padx=10, pady=8)

    def _cambiar_tipo(self, tipo):
        """Se llama al dar clic en la pestania Casa o Gimnasio."""
        self.tipo_seleccionado = tipo
        # Se vuelve a dibujar TODA la pantalla, para que se muestre la
        # rutina pendiente correspondiente al tipo recien elegido (o
        # el mensaje de "sin rutina pendiente" si no hubiera ninguna).
        self._dibujar_contenido()

    def _marcar_completada(self):
        """Se llama al dar clic en 'Marcar como Completada'."""
        # Verificacion de seguridad: si por alguna razon se llegara a
        # llamar esta funcion sin que hubiera una rutina cargada (no
        # deberia poder pasar, porque el boton estaria deshabilitado),
        # simplemente no se hace nada.
        if not self._rutina_pendiente_id:
            return

        exito = marcar_rutina_completada(self._rutina_pendiente_id)
        if exito:
            messagebox.showinfo("Listo", "Rutina marcada como completada.")
        else:
            messagebox.showerror("Error", "No se pudo actualizar la rutina.")

        # Se redibuja todo, para que la rutina que se acaba de marcar
        # (o la que se elimino automaticamente del otro lugar, segun
        # vimos en alumno_modelo.marcar_rutina_completada) ya no
        # aparezca como pendiente.
        self._dibujar_contenido()

    def _mostrar_animacion(self, ejercicio):
        """Se llama al dar clic en el boton de ojo. Abre una ventana
        emergente con la animacion (GIF) del ejercicio reproduciendose
        en bucle."""
        ventana = ctk.CTkToplevel(self)
        aplicar_icono(ventana)
        ventana.title(ejercicio["nombre_ejercicio"])
        ventana.geometry("300x340")
        ventana.resizable(False, False)
        ventana.configure(fg_color="white")
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text=ejercicio["nombre_ejercicio"], text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(15, 10))

        # Se le pide a la funcion reutilizable crear_reproductor_gif
        # (de utilidades/animaciones.py) que arme el widget de la
        # animacion, usando la ruta guardada en
        # "ejercicio['animacion_ejercicio']" (que puede ser None si ese
        # ejercicio no tiene animacion asignada — en ese caso,
        # crear_reproductor_gif ya sabe mostrar el mensaje de
        # "Animacion no disponible").
        crear_reproductor_gif(
            ventana, ejercicio.get("animacion_ejercicio"), tamanio=(260, 260)
        ).pack(pady=(0, 15))
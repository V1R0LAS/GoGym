import customtkinter as ctk
from configuracion import NOMBRE_APP
from vistas.vista_login import VistaLogin
from vistas.vista_menu_alumno import VistaMenuAlumno
from vistas.vista_menu_admin import VistaMenuAdmin
from vistas.vista_menu_profesional import VistaMenuProfesional
from utilidades.ventanas import aplicar_icono
from utilidades.sesion import guardar_sesion, obtener_sesion, borrar_sesion
from modelos.usuario_modelo import verificar_sesion_valida

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AplicacionGoGym(ctk.CTk):
    """Ventana principal de la aplicacion.
    Todas las vistas (login, menus, etc.) se muestran DENTRO de esta
    misma ventana; se van intercambiando segun lo que el usuario haga."""

    def __init__(self):

        super().__init__()

        self.title(NOMBRE_APP)

        self.geometry("1100x650")

        aplicar_icono(self)

        self._intentar_reanudar_sesion()

    def _intentar_reanudar_sesion(self):
        """Revisa si habia una sesion guardada de la ultima vez que se
        cerro la app. Si existe y sigue siendo valida (la cuenta no se
        borro ni se desactivo), entra directo a su menu. Si no, muestra
        el login normal."""


        sesion = obtener_sesion()
        if sesion and verificar_sesion_valida(sesion["id_usuario"], sesion["rol"]):
         
            self._al_iniciar_sesion(sesion)
        else:
          
            if sesion:
                borrar_sesion()
           
            self._mostrar_login()

    def _mostrar_login(self):
        """Limpia la ventana (por si habia otra vista) y muestra el login."""

      
        for widget in self.winfo_children():
            widget.destroy()

        vista = VistaLogin(self, al_iniciar_sesion=self._al_iniciar_sesion)

      
        vista.pack(expand=True, fill="both")

    def _al_iniciar_sesion(self, usuario):
        """
        Se ejecuta cuando VistaLogin confirma que el login fue correcto,
        O cuando se reanuda una sesion guardada al abrir la app.
        'usuario' trae id_usuario, correo y rol. Segun el rol, se
        muestra un menu distinto, y se guarda la sesion en disco.
        """
      
        guardar_sesion(usuario)

       
        rol = usuario["rol"]

      
        if rol == "Alumno":
            self._mostrar_menu_alumno(usuario)
        elif rol == "Profesional":
            self._mostrar_menu_profesional(usuario)
        elif rol == "Administrador":
            self._mostrar_menu_admin(usuario)

    def _cerrar_sesion(self):
        """Se le pasa a cada menu como 'al_cerrar_sesion'. Borra la
        sesion guardada y regresa al login."""
      
        borrar_sesion()
    
        self._mostrar_login()

    def _mostrar_menu_alumno(self, usuario):
     
        for widget in self.winfo_children():
            widget.destroy()

    
        vista = VistaMenuAlumno(
            self,
            id_usuario=usuario["id_usuario"],
            correo=usuario["correo"],
            al_cerrar_sesion=self._cerrar_sesion,
        )
        vista.pack(expand=True, fill="both")

    def _mostrar_menu_admin(self, usuario):
      
        for widget in self.winfo_children():
            widget.destroy()

        vista = VistaMenuAdmin(
            self,
            id_usuario=usuario["id_usuario"],
            correo=usuario["correo"],
            al_cerrar_sesion=self._cerrar_sesion,
        )
        vista.pack(expand=True, fill="both")

    def _mostrar_menu_profesional(self, usuario):
       
        for widget in self.winfo_children():
            widget.destroy()

        vista = VistaMenuProfesional(
            self,
            id_usuario=usuario["id_usuario"],
            correo=usuario["correo"],
            al_cerrar_sesion=self._cerrar_sesion,
        )
        vista.pack(expand=True, fill="both")



if __name__ == "__main__":
  
    app = AplicacionGoGym()
    app.mainloop()
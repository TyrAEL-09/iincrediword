import customtkinter as ctk
from tkinter import messagebox
from auth.utils import cargar_usuarios, registrar_usuario

def ventana_registro(ventana_login_func):
    ventana = ctk.CTk()
    ventana.title("Registro")
    ventana.geometry("600x500")
    ventana.minsize(400, 400)

    for i in range(10):
        ventana.rowconfigure(i, weight=1)
    ventana.columnconfigure(0, weight=1)

    ctk.CTkLabel(ventana, text="Registro de Usuario", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=5)

    entry_email_r = ctk.CTkEntry(ventana, placeholder_text="Email", height=24, font=ctk.CTkFont(size=13))
    entry_email_r.grid(row=2, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_pass_r = ctk.CTkEntry(ventana, placeholder_text="Contraseña", show="*", height=24, font=ctk.CTkFont(size=13))
    entry_pass_r.grid(row=3, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_conf_r = ctk.CTkEntry(ventana, placeholder_text="Confirmar contraseña", show="*", height=24, font=ctk.CTkFont(size=13))
    entry_conf_r.grid(row=4, column=0, padx=80, pady=(0, 10), sticky="nsew")

    def registrar():
        email = entry_email_r.get().strip()
        password = entry_pass_r.get().strip()
        confirmar = entry_conf_r.get().strip()
        usuarios = cargar_usuarios()

        if not email or not password or not confirmar:
            messagebox.showerror("Error", "Completa todos los campos.")
        elif email in usuarios:
            messagebox.showerror("Error", "El email ya está registrado.")
        elif password != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
        elif len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres.")
        else:
            registrar_usuario(email, password)
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
            ventana.destroy()
            ventana_login_func()

    ctk.CTkButton(ventana, text="Registrar", height=28, font=ctk.CTkFont(size=13), command=registrar).grid(row=5, column=0, pady=(10, 20))

    ventana.mainloop()

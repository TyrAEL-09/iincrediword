from auth import login

def main():
    """
    Punto de entrada principal del sistema.
    Llama a la función de login para iniciar el flujo de la aplicación.
    Args: Ninguno.
    Returns: None.
    Uso: Ejecutado al correr el archivo main.py.
    """
    login.mostrar_login()

if __name__ == "__main__":
    main()
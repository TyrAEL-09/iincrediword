def configurar_ventana(root):
    root.title("Iniciar Sesión en MyFirstChamba-Hub")
    root.geometry("700x500")
    root.minsize(500, 350)
    root.configure(fg_color="black")
    root.attributes("-alpha", 0.0)
    
def configurar_layout(root):
    for i in range(10):
        root.rowconfigure(i, weight=1)
    root.columnconfigure(0, weight=1)
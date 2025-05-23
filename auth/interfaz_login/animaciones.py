def fade_in(root, callback, opacidad=0.0):
    if opacidad < 1.0:
        root.attributes("-alpha", opacidad)
        root.after(50, lambda: fade_in(root, callback, opacidad + 0.05))
    else:
        root.after(3000, callback)

def fade_out(root, splash_frame, mostrar_formulario_func, fade_in_formulario_func, opacidad=1.0):
    if opacidad > 0:
        root.attributes("-alpha", opacidad)
        root.after(50, lambda: fade_out(root, splash_frame, mostrar_formulario_func, fade_in_formulario_func, opacidad - 0.05))
    else:
        splash_frame.destroy()
        mostrar_formulario_func()
        fade_in_formulario_func(0.0)

def fade_in_formulario(root, opacidad=0.0):
    if opacidad <= 1.0:
        root.attributes("-alpha", opacidad)
        root.after(30, lambda: fade_in_formulario(root, opacidad + 0.05))

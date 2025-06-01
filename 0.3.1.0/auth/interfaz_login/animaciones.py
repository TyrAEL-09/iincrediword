def fade_in(root, splash_frame, callback, opacidad=0.0):
    if opacidad < 1.0:
        root.attributes("-alpha", opacidad)
        root.after(50, lambda: fade_in(root, splash_frame, callback, opacidad + 0.05))
    else:
        root.after(3000, lambda: fade_out(root, splash_frame, callback, 1.0))

def fade_out(root, splash_frame, callback, opacidad):
    if opacidad > 0:
        root.attributes("-alpha", opacidad)
        root.after(50, lambda: fade_out(root, splash_frame, callback, opacidad - 0.05))
    else:
        splash_frame.destroy()
        callback()
        fade_in_formulario(root)

def fade_in_formulario(root, opacidad=0.0):
    if opacidad <= 1.0:
        root.attributes("-alpha", opacidad)
        root.after(30, lambda: fade_in_formulario(root, opacidad + 0.05))
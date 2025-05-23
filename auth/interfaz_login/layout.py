def configurar_layout(root):
    for i in range(10):
        root.rowconfigure(i, weight=1)
    root.columnconfigure(0, weight=1)

import sys
import os

# Agrega la carpeta 0.5.0.0 al path para poder importar main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "content"))

import main as app_main

if __name__ == "__main__":
    app_main.main()
    sys.exit(0)
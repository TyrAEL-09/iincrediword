import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "content"))

import main as app_main


if __name__ == "__main__":
    app_main.main()
    sys.exit(0)
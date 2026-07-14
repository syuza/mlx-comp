import sys
from .server import run_server
from .gui import LLMLinguaApp

def main():
    if "--server-only" in sys.argv:
        run_server()
    else:
        LLMLinguaApp().run()

if __name__ == "__main__":
    main()

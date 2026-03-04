"""
NexPlorer — Entry point
Usage:
  python -m nexplorer              → launch GUI
  python -m nexplorer --headless   → CLI mode (future)
"""
import sys

def main():
    args = sys.argv[1:]
    if "--headless" in args or "--cli" in args:
        print("NexPlorer CLI mode — coming in v1.1.0")
        sys.exit(0)
    try:
        from nexplorer.ui.app import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"GUI dependencies missing: {e}")
        print("Install with: pip install customtkinter")
        sys.exit(1)

if __name__ == "__main__":
    main()

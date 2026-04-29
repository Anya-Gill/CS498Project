import subprocess
import threading
import webbrowser
import time
import os
import sys

FRONTEND_FILE = "index.html"
FLASK_APP = "app.py"
FLASK_PORT = 5000

flask_process = None


def start_flask():
    global flask_process
    flask_process = subprocess.Popen(["python", FLASK_APP])
    flask_process.wait()


def open_frontend():
    time.sleep(1.5)
    frontend_path = os.path.abspath(FRONTEND_FILE)
    webbrowser.open(f"file://{frontend_path}")


if __name__ == "__main__":
    print(f"Starting Flask server on port {FLASK_PORT}...")

    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    open_frontend()

    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down...")
        if flask_process is not None:
            flask_process.terminate()
            flask_process.wait()
        sys.exit(0)

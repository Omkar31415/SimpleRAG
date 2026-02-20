import subprocess
import sys
import os
import signal
import time

def main():
    print("Starting RAG News API Backend (Uvicorn on port 8000)...")
    
    # Activate virtual environment if running from root without it
    # We use python executable directly to avoid shell script activation issues
    venv_python = os.path.join("venv", "Scripts", "python.exe") if os.name == 'nt' else "venv/bin/python"
    
    if os.path.exists(venv_python):
        python_cmd = venv_python
    else:
        python_cmd = sys.executable  # Fallback to current python
        
    api_process = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "main:app", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    print("Waiting 3 seconds for API to initialize...")
    time.sleep(3)

    print("Starting Streamlit UI (Port 8501)...")
    ui_process = subprocess.Popen(
        [python_cmd, "-m", "streamlit", "run", "app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    print("\n" + "="*50)
    print("🚀 All systems online!")
    print("👉 API Swagger Docs: http://localhost:8000/docs")
    print("👉 Streamlit Web UI: http://localhost:8501")
    print("="*50 + "\n")

    try:
        # Keep the main process running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down RAG News System...")
        api_process.terminate()
        ui_process.terminate()
        api_process.wait()
        ui_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()

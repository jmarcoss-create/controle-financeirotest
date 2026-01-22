import subprocess
import sys
import os

# Garante execução na pasta correta
base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

# Comando para rodar o Streamlit
cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app.py",
    "--server.headless=true",
    "--server.port=8501"
]

# Inicia o Streamlit
subprocess.Popen(cmd)

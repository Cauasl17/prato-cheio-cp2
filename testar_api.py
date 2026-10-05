"""Executa a suíte isolada sem depender de API externa."""
import subprocess
import sys
raise SystemExit(subprocess.call([sys.executable,"-m","pytest","-q"]))

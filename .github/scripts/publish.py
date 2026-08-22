#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # 1. Kontrola adresáře
    if not os.path.exists("pyproject.toml") and not os.path.exists("setup.py"):
        print("[ERROR] Spusťte skript z kořenové složky projektu.")
        sys.exit(1)

    # 2. Vyčištění starých souborů
    print("[INFO] Čištění starých buildů...")
    subprocess.run("rm -rf build dist *.egg-info", shell=True)

    # 3. Sestavení balíčku
    print("[INFO] Kompilace balíčku...")
    res = subprocess.run([sys.executable, "-m", "build"])
    if res.returncode != 0:
        print("[ERROR] Build selhal.")
        sys.exit(1)

    # 4. Kontrola přes Twine
    print("[INFO] Kontrola balíčku přes Twine...")
    subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"])

    # 5. Nahrání na TestPyPI
    potvrzeni = input("Chcete balíček nahrát na TestPyPI? (y/N): ")
    if potvrzeni.lower() == "y":
        subprocess.run([sys.executable, "-m", "twine", "upload", "--repository", "testpypi", "dist/*"])

if __name__ == "__main__":
    main()

"""
JEEVAN PyInstaller Standalone Executable Packaging Script
Generates standalone JEEVAN.exe for Windows 10/11
"""
import sys
import subprocess
import os

def build_executable():
    print("====================================================")
    print("  JEEVAN Standalone Executable Build Script")
    print("====================================================")
    
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--name=JEEVAN",
        "--add-data=backend;backend",
        "main.py"
    ]

    print(f"Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("\n[SUCCESS] Standalone JEEVAN executable generated in 'dist/JEEVAN/' directory!")

if __name__ == "__main__":
    build_executable()

#!/usr/bin/env python3
"""
TASK PRIME - Build Script
Creates standalone GUI executable (NO TERMINAL)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    try:
        import PyInstaller
        print("✅ PyInstaller available")
        return True
    except ImportError:
        print("❌ Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True


def check_dependencies():
    dependencies = ["pyodbc", "requests"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            print(f"❌ Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    return True


def clean_dirs():
    for d in ["dist", "build"]:
        if Path(d).exists():
            shutil.rmtree(d)
    print("🧹 Cleaned build folders")


def build_exe():
    print("🔨 Building TASK PRIME GUI EXE...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",          # 👈 NO TERMINAL
        "--name", "TASK_PRIME",
        "--clean",
        "--noconfirm",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        "gui_app.py"           # 👈 GUI ENTRY POINT
    ]

    subprocess.check_call(cmd)
    print("✅ TASK_PRIME.exe built successfully")


def create_package():
    deploy_dir = Path("TASK_PRIME_APP")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()

    exe = Path("dist/TASK_PRIME.exe")
    shutil.copy2(exe, deploy_dir / exe.name)
    shutil.copy2("config.json", deploy_dir / "config.json")

    readme = """TASK PRIME - Sync Tool

How to use:
1. Edit config.json
2. Double click TASK_PRIME.exe
3. Click Start Sync

No terminal will appear.
"""

    with open(deploy_dir / "README.txt", "w") as f:
        f.write(readme)

    print("📦 Deployment folder created: TASK_PRIME_APP")


def main():
    print("=" * 60)
    print("      TASK PRIME - GUI Build System")
    print("=" * 60)

    check_dependencies()
    check_pyinstaller()
    clean_dirs()
    build_exe()
    create_package()

    print("\n🎉 BUILD COMPLETED")
    print("👉 Open: TASK_PRIME_APP/TASK_PRIME.exe")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TASK PRIME - Build Script
Creates standalone GUI executable (NO TERMINAL)
With Custom Icon
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


ICON_FILE = "taskprime.ico"   # 👈 your icon file


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
    for d in ["dist", "build", "TASK_PRIME_APP"]:
        if Path(d).exists():
            shutil.rmtree(d)
    print("🧹 Cleaned build folders")


def build_exe():
    print("🔨 Building TASK PRIME GUI EXE...")

    if not Path(ICON_FILE).exists():
        print(f"⚠️ Icon file not found: {ICON_FILE}")
        print("Proceeding without icon...")
        icon_args = []
    else:
        icon_args = ["--icon", ICON_FILE]

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",          # NO TERMINAL
        "--name", "TASK_PRIME",
        "--clean",
        "--noconfirm",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        *icon_args,            # 👈 ICON ADDED HERE
        "gui_app.py"           # GUI ENTRY POINT
    ]

    subprocess.check_call(cmd)
    print("✅ TASK_PRIME.exe built successfully")


def create_package():
    deploy_dir = Path("TASK_PRIME_APP")
    deploy_dir.mkdir()

    exe = Path("dist/TASK_PRIME.exe")
    shutil.copy2(exe, deploy_dir / exe.name)
    shutil.copy2("config.json", deploy_dir / "config.json")

    # Copy icon also into package
    if Path(ICON_FILE).exists():
        shutil.copy2(ICON_FILE, deploy_dir / ICON_FILE)

    readme = """TASK PRIME - Sync Tool

How to use:
1. Edit config.json
2. Double click TASK_PRIME.exe
3. Sync will auto start

This is a standalone application.
No terminal window will appear.
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

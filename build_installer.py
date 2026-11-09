#!/usr/bin/env python
"""Build and package NIFRAP 2.0 into a standalone executable and portable distribution."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
APP_DIST = DIST_DIR / "NIFRAP_2.0"
ZIP_OUTPUT = DIST_DIR / "NIFRAP-2.0-Windows-Portable.zip"


def build_executable():
    print("[1/3] Building executable using PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "nifrap.spec",
        "--noconfirm",
        "--clean",
    ]
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    if result.returncode != 0:
        print("[ERROR] PyInstaller build failed!")
        sys.exit(result.returncode)
    print("[SUCCESS] PyInstaller build completed successfully.")


def create_portable_zip():
    print("[2/3] Creating portable ZIP distribution...")
    if not APP_DIST.exists():
        print(f"[ERROR] Expected build directory {APP_DIST} does not exist.")
        return

    # Add README to dist
    shutil.copy(BASE_DIR / "README.md", APP_DIST / "README.md")

    # Create zip archive
    archive_base = str(DIST_DIR / "NIFRAP-2.0-Windows-Portable")
    zip_path = shutil.make_archive(archive_base, "zip", root_dir=str(DIST_DIR), base_dir="NIFRAP_2.0")
    print(f"[SUCCESS] Portable distribution created at:\n  -> {zip_path}")


def create_inno_setup_script():
    print("[3/3] Generating Inno Setup installer script (installer.iss)...")
    iss_content = f"""[Setup]
AppName=NIFRAP 2.0
AppVersion=2.0.0
AppPublisher=NIFRAP
DefaultDirName={{autopf}}\\NIFRAP
DefaultGroupName=NIFRAP
OutputDir=dist
OutputBaseFilename=NIFRAP_2.0_Setup
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "dist\\NIFRAP_2.0\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\NIFRAP 2.0"; Filename: "{{app}}\\NIFRAP_2.0.exe"
Name: "{{group}}\\Uninstall NIFRAP 2.0"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\NIFRAP 2.0"; Filename: "{{app}}\\NIFRAP_2.0.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\NIFRAP_2.0.exe"; Description: "{{cm:LaunchProgram,NIFRAP 2.0}}"; Flags: nowait postinstall skipifsilent
"""
    iss_file = BASE_DIR / "installer.iss"
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_content)
    print(f"[SUCCESS] Inno Setup script generated at:\n  -> {iss_file}")


if __name__ == "__main__":
    print("==================================================")
    print("        NIFRAP 2.0 Installer Build Pipeline       ")
    print("==================================================")
    build_executable()
    create_portable_zip()
    create_inno_setup_script()
    print("\n[ALL TASKS COMPLETED]")


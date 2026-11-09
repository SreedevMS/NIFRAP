# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import dis

# Monkey-patch dis.get_instructions in memory to prevent Python 3.10 IndexError
# on corrupted/incompatible third-party bytecode installed on the host
_orig_get_instructions = dis.get_instructions

def _safe_get_instructions(x, *args, **kwargs):
    try:
        yield from _orig_get_instructions(x, *args, **kwargs)
    except IndexError:
        pass

dis.get_instructions = _safe_get_instructions

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Collect CustomTkinter assets (themes, fonts, json)
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

hidden_imports = list(set(
    ctk_hiddenimports +
    [
        'openpyxl',
        'xlsxwriter',
        'docx',
        'psutil',
        'PIL',
        'PIL._tkinter_finder',
        'darkdetect',
        'bs4',
        'requests',
        'scapy',
        'scapy.all',
        'scapy.layers.inet',
        'scapy.layers.http',
        'scapy.layers.dns',
        'scapy.layers.tls.all',
        'scapy.layers.tls.extensions',
        'nifrap',
        'nifrap.config',
        'nifrap.core.packet_parser',
        'nifrap.core.sniffer',
        'nifrap.core.scraper',
        'nifrap.core.storage',
        'nifrap.core.pipeline',
        'nifrap.gui.app',
        'nifrap.gui.views.sniffer_view',
        'nifrap.gui.views.scraper_view',
        'nifrap.gui.views.export_view',
        'nifrap.gui.views.settings_view',
    ]
))

# Exclude heavy unrelated libraries installed on this machine that break bytecode analysis
excludes = [
    'numpy',
    'matplotlib',
    'scipy',
    'torch',
    'torchvision',
    'IPython',
    'jupyter',
    'tornado',
    'zmq',
    'sympy',
    'weasel',
    'playwright',
    'crawl4ai',
    'ultralytics',
    'soundfile',
    'cv2',
    'pandas',
]

all_datas = ctk_datas + [
    ('nifrap', 'nifrap'),
]

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=ctk_binaries,
    datas=all_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtimehooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NIFRAP_2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NIFRAP_2.0',
)

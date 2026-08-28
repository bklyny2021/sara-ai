# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for SARA standalone .exe
block_cipher = None

hiddenimports = [
    'sara_brain', 'sara_tools', 'sara_swarm_brain', 'sara_ui',
    'sara_mic_input', 'sara_network_security', 'sara_people_finder',
    'sara_python_course', 'sara_tool_creator', 'sara_vision',
    'sara_voice_output', 'sara_weather', 'sara_web_scraper',
    'sara_wiki_memory', 'startup_consciousness_fixed',
    'sara_scheduler', 'sara_voice_input', 'sara_facts', 'network_scanner', 'network_tool', 'sara_system_info', 'sara_tasks', 'sara_traffic',
    'flask', 'requests', 'psutil',
]

a = Analysis(
    ['sara_web_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sara_ui.html', '.'),
        ('sara_watchowl.py', '.'),
        ('sara_learning_chain.py', '.'),
        ('sara_scheduler.py', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SARA_0.2.0_standalone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # windowless GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

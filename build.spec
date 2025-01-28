# -*- mode: python ; coding: utf-8 -*-

from argparse import ArgumentParser
from platform import system

parser = ArgumentParser()
parser.add_argument("--binary", action="store_true")
options = parser.parse_args()

datas = []
binaries = []
hiddenimports = ["cairo", "gi.repository.Poppler"]

if system() == "Linux":
    datas.append(("/usr/lib/x86_64-linux-gnu/girepository-1.0/Poppler-0.18.typelib", "."))
elif system() == "Darwin":
    datas.append(("/usr/local/lib/girepository-1.0/Poppler-0.18.typelib", "."))
elif system() == "Windows":
    # Adiciona as DLLs necessárias do Poppler
    poppler_dlls = [
        "libpoppler-glib-8.dll"
    ]

    for dll in poppler_dlls:
        dll_path = os.path.join(os.environ["MSYSTEM_PREFIX"], "bin", dll)
        if os.path.exists(dll_path):
            datas.append((dll_path, dll))
    # Adiciona arquivos `.typelib` do GObject Introspection
    typelibs = [
        "Poppler-0.18.typelib"
    ]

    for typelib in typelibs:
        typelib_path = os.path.join(os.environ["MSYSTEM_PREFIX"], "lib", "girepository-1.0", typelib)
        if os.path.exists(typelib_path):
            datas.append((typelib_path, f"lib/girepository-1.0/{typelib}"))

a = Analysis(
    ['helloworldgtk.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('LICENSE', '.')  # Adiciona o arquivo LICENSE
    ] + datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={
        'gi': {
            'icons': ['Adwaita'],
            'themes': ['Adwaita'],
            'module-versions': {
                'Gtk': '3.0'
            }
        }
    },
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

if system() == "Linux":
    if not options.binary:
        exe = EXE(
            pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name='hello-world-gtk',
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
            a.datas,
            strip=False,
            upx=True,
            upx_exclude=[],
            name='hello-world-gtk',
        )
    else:
        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.datas,
            [],
            name='hello-world-gtk',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None,
        )
elif system() == "Darwin":
    if not options.binary:
        exe = EXE(
            pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name='hello-world-gtk',
            icon='macos/org.example.HelloWorldGTK.icns',
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
            a.datas,
            strip=False,
            upx=True,
            upx_exclude=[],
            name='hello-world-gtk',
        )
        app = BUNDLE(
            coll,
            name='Hello World.app',
            icon='macos/org.example.HelloWorldGTK.icns',
            bundle_identifier=None,
            version=None,
        )
    else:
        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.datas,
            [],
            name='hello-world-gtk',
            icon='macos/org.example.HelloWorldGTK.icns',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None,
        )
elif system() == "Windows":
    if not options.binary:
        exe = EXE(
            pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name='hello-world-gtk',
            icon='windows/org.example.HelloWorldGTK.ico',
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
            a.datas,
            strip=False,
            upx=True,
            upx_exclude=[],
            name='hello-world-gtk',
        )
    else:
        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.datas,
            [],
            name='hello-world-gtk',
            icon='windows/org.example.HelloWorldGTK.ico',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None,
        )

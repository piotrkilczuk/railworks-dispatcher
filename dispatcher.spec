# -*- mode: python -*-
a = Analysis(['.\\dispatcher.py'],
             pathex=['C:\\Users\\Piotr\\OpenSource\\railworks-dispatcher-windows'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='dispatcher.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )

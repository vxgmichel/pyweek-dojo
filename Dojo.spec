# -*- mode: python -*-
a = Analysis(['Dojo.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
			 
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
		
pyz = PYZ(a.pure)
exe = EXE(pyz,
          Tree('resource', prefix='resource', excludes=[]),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Dojo.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon="resource/image/Dojo.ico")

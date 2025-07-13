# coding: utf-8

from cx_Freeze import setup, Executable

executables = [Executable('main.py')]

excludes = []

includes = ["keyword","pygame","json","os","pathlib","contextlib","urllib"]

zip_include_packages = []#["pygame","json","os","pathlib","contextlib"]

options = {
    'build_exe': {
        'include_msvcr': True,
        'includes': includes,
        "include_files":["res","internal_system.py","isometry.py","leitmotifplus.py","rails_iso.py","train.py","world.json","elements.json","route_switches.json"]
        #'excludes': excludes,
        #   'zip_include_packages': zip_include_packages,
        #'build_exe': 'build_windows',
    }
}

setup(name='aims',
      version='0.2.9',
      description="Express to Nowhere",
      executables=executables,
      options=options)
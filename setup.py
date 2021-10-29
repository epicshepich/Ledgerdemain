from setuptools import find_packages
from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress'
        ],
        'excludes': ['tkinter']
    }
}

executables = [
    Executable('ledgerdemain.py',
               base='console',
               targetName='ledgerdemain.exe')
]

setup(
    name='ledgerdemain',
    packages=find_packages(),
    version='0.1.2',
    description='A tool for managing ledgers.',
    executables=executables,
    options=options
)

from pathlib import Path

from setuptools import setup

binfiles = Path(Path(__file__).parent, 'pdbtools').resolve().glob('*.py')
bin_py = [
    f.stem + '=zpdbtools.' + f.stem + ':main'
    for f in binfiles
    ]

setup(
    entry_points={
        'console_scripts': bin_py,
        },
    )

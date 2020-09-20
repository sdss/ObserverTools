from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
changelog = (here / 'CHANGELOG.md').open('r').read()
bin = here / 'bin'
bincache = bin / '__pycache__'
if bincache.exists():
    for f in bincache.glob('*.pyc'):
        f.unlink()
    bincache.rmdir()
version = changelog.split('[')[-1].split(']')[0]

setup(
    name='ObserverTools',
    version=version,
    scripts=[str(p) for p in (here / 'bin').glob('*')],
    package_data={
        '': ['*.dat', '*.fits', '*.npy', '*.txt'],
    },
    packages=find_packages('python'),
    description='A library of tools for SDSS telescope operations.',
    url='https://wiki.sdss.org/display/APO/Observing+Scripts',
)
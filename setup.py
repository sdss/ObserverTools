from setuptools import setup
from pathlib import Path

here = Path(__file__).parent
changelog = (here / 'CHANGELOG.md').open('r').read()
bin_dir = here / 'bin'
bin_cache = bin_dir / '__pycache__'
if bin_cache.exists():
    for f in bin_cache.glob('*.pyc'):
        f.unlink()
    bin_cache.rmdir()
version = changelog.split('[')[-1].split(']')[0]
requirements = (here / 'requirements.txt').open('r').readlines()
setup(
    name='sdss-obstools',
    version=version,
    scripts=[str(p) for p in (here / 'bin').glob('*')],
    package_data={
        '': ['*.dat', '*.fits', '*.npy', '*.txt'],
    },
    packages=['python', 'bin'],
    install_requires=requirements,
    description='A library of tools for SDSS telescope operations.',
    url='https://wiki.sdss.org/display/APO/Observing+Scripts',
    test_suite='nose.collector',
    tests_require=['nose']
)

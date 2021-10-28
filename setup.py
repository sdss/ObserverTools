from setuptools import setup, find_packages
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
    scripts=[p.as_posix() for p in (here / 'bin').glob('*')],
    package_data={
        '': ['*.dat', '*.fits', '*.npy', '*.txt'],
        'dat': ['*.npy', '*.dat'],
        'flux': ['*.flux']
    },
    packages=['sdssobstools', 'bin', 'dat', 'tests'],
    install_requires=requirements,
    description='A library of tools for SDSS telescope operations.',
    long_description=(here / 'README.md').open('r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://wiki.sdss.org/display/APO/Observing+Scripts',
    author='Dylan Gatlin, Dmitry Bizyaev',
    author_email='dgatlin@apo.nmsu.edu',
    license='BSD 3-clause',
    license_file='LICENSE.md',
)

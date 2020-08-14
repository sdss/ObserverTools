#!/usr/bin/env python3
"""
sp_version.py

Outputs a list of software versions used that night. Rewritten by Dylan Gatlin
 based on spVersion by Elena Malanushenko

Changelog:
2020-06-08  DG  Ported to ObserverTools in Python 3, replaced os with sub
"""

import subprocess as sub

__version__ = '3.0.0'


def main():
    softwares, versions = [], []
    idlspec2d = sub.Popen('setup idlspec2d; idlspec2d_version', shell=True,
                          stdout=sub.PIPE)
    softwares.append('idlspec2d')
    versions.append(idlspec2d.stdout.read().decode('utf-8').strip('\n'))

    plate_mapper = sub.Popen('setup idlmapper; echo "print, idlmapper_version()'
                             '" | idl 2> /dev/null &', shell=True,
                             stdout=sub.PIPE)
    softwares.append('plate-mapper3')
    versions.append(plate_mapper.stdout.read().decode('utf-8').strip('\n'))

    petunia = sub.Popen('readlink /home/sdss4/products/Linux64/petunia/current',
                        shell=True, stdout=sub.PIPE)
    softwares.append('Petunia')
    versions.append(petunia.stdout.read().decode('utf-8').strip('\n'))

    autoscheduler = sub.Popen('readlink /home/sdss4/products/Linux64/'
                              'autoscheduler/current', shell=True,
                              stdout=sub.PIPE)
    softwares.append('Autoscheduler')
    versions.append(autoscheduler.stdout.read().decode('utf-8').strip('\n'))

    sdss_module = sub.Popen("readlink /home/sdss4/products/Linux64/"
                            "sdss_python_module/current", shell=True,
                            stdout=sub.PIPE)
    softwares.append('SDSS Python Module')
    versions.append(sdss_module.stdout.read().decode('utf-8').strip('\n'))

    mangadrp = sub.Popen("/home/manga/products/Linux64/mangadrp/trunk/bin/"
                         "mangadrp_version", shell=True, stdout=sub.PIPE)
    softwares.append('mangadrp')
    versions.append(mangadrp.stdout.read().decode('utf-8').strip('\n'))

    print('{:-^42}'.format('Other Versions'))
    for s, v in zip(softwares, versions):
        print('{:<20}: {:<20}'.format(s, v))


if __name__ == '__main__':
    main()

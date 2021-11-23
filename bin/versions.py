#!/usr/bin/env python3
"""
sp_version.py

Outputs a list of software versions used that night. Rewritten by Dylan Gatlin
 based on spVersion by Elena Malanushenko

Changelog:
2020-06-08  DG  Ported to ObserverTools in Python 3, replaced os with sub
"""

import subprocess as sub
import tpmdata

__version__ = '3.1.0'


def main():
    softwares, versions = [], []

    sdss_obstools = sub.run('pip list | grep sdss-obstools', shell=True,
                              stdout=sub.PIPE
                           ).stdout.decode('utf-8').strip('\n')
    if len(sdss_obstools) != 0:
        softwares.append(sdss_obstools.split()[0])
        versions.append(sdss_obstools.split()[-1])
    else:
        softwares.append("sdss-obstools")
        versions.append("FAILED")
    
    tpmdata.tinit()
    tpm_packet = tpmdata.packet(1, 1)
    softwares.append("TPM")
    try:
        versions.append(tpm_packet["tpm_vers"])
    except:
        versions.append("FAILED")
    
    softwares.append("MCP")
    try:
        versions.append(tpm_packet["mcp_vers"])
    except:
        versions.append("FAILED")
    
    module_help = sub.run("module --help", shell=True, stdout=sub.PIPE,
                              stderr=sub.PIPE
                              ).stderr.decode("utf-8")
    has_module = "command not found" not in module_help

    if has_module:
        idlspec = sub.run("module load idlspec2d; idlspec2d_version",
                          shell=True,
                          stdout=sub.PIPE).stdout.decode("utf-8").strip('\n')
        softwares.append("idlspec2d")
        versions.append(idlspec.split()[-1])
    
    
    print('{:-^42}'.format('Other Versions'))
    for s, v in zip(softwares, versions):
        print('{:<20}: {:<20}'.format(s, v))


if __name__ == '__main__':
    main()

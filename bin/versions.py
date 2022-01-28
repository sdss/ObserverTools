#!/usr/bin/env python3
"""
versions.py

Outputs a list of software versions used that night. Rewritten by Dylan Gatlin
 based on spVersion by Elena Malanushenko
"""

import subprocess as sub
import tpmdata
import signal
import multiprocessing

__version__ = '3.1.0'


def tpm_timeout(sig, frame):
    raise TimeoutError("TPM Timeout")


def get_tpm_packet(out_dict):
    tpmdata.tinit()
    data = tpmdata.packet(1, 1)
    for key, val in data.items():
        out_dict[key] = val
    return 0


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
        
    data = multiprocessing.Manager().dict()
    tpm_thread = multiprocessing.Process(target=get_tpm_packet, args=(data,))
    tpm_thread.start()

    module_help = sub.run("module --help", shell=True, stdout=sub.PIPE,
                              stderr=sub.PIPE
                              ).stderr.decode("utf-8")
    has_module = "command not found" not in module_help
    
    tpm_thread.join(1)
    
    if tpm_thread.is_alive():
        tpm_thread.kill()   
    softwares.append("TPM")
    softwares.append("MCP")
    softwares.append("PLC")
    softwares.append("Fiducials")
    if tpm_thread.is_alive():
        tpm_thread.kill()
        versions.append("FAILED")
        versions.append("FAILED")
        versions.append("FAILED")
        versions.append("FAILED")
    else:
        versions.append(data["tpm_vers"])
        versions.append(data["mcp_vers"])
        versions.append(data["plc_vers"])
        versions.append(data["fid_vers"])
        
    
    if has_module:
        names = ["idlspec2d", "Kronos", "roboscheduler"]
        cmds = ["module load idlspec2d; idlspec2d_version",
                "module load kronos; kronosversion.py",
                "module load roboscheduler; roboschedulerversion.py"]
        for n, c in zip(names, cmds):
            ver = sub.run(c, shell=True, stdout=sub.PIPE, stderr=sub.PIPE
                          ).stdout.decode("utf-8").rstrip('\n')
            softwares.append(n)
            if ver:
                versions.append(ver)
            else:
                versions.append("FAILED")
    
    print('{:-^42}'.format('Other Versions'))
    for s, v in zip(softwares, versions):
        print('{:<20}: {:<20}'.format(s, v))
    print()

    disk_usage = sub.run('df -h | grep -e " /home\|data"', shell=True,
                         stdout=sub.PIPE).stdout.decode("utf-8")
    print(disk_usage)

if __name__ == '__main__':
    main()

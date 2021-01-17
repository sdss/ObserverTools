#!/usr/bin/env python3

from astropy.time import Time
import sys

try:
    import epics_fetch
except ImportError as e:
    try:
        from bin import epics_fetch
    except ImportError:
        raise ImportError(f'epics_fetch.py not in PYTHONPATH:\n {sys.path}')
try:
    import tpmdata
    tpmdata.tinit()
except ImportError:
    print('tpmdata unavailable')
    tpmdata = None

__version__ = '3.0.0'


def query():
    if tpmdata is None:
        raise ConnectionError('Cannot query the tpm without tpmdata installed')

    data = tpmdata.packet(1, 1)

    t = Time(data['ctime'], format='unix')
    output = f'Status at:  {t.isot[12:19]}Z\n'
    output += (f"Telescope stowed at:  "
               f"{data['az_actual_pos']*data['az_spt']/3600:>5.1f},"
               f" {data['alt_actual_pos']*data['alt_spt']/3600:>5.1f},"
               f" {data['rot_actual_pos']*data['rot_spt']/3600:>5.1f} mount\n")
    epics_data = epics_fetch.get_data(['25m:mcp:instrumentNum'],
                                      start_time=Time.now().to_datetime(),
                                      end_time=Time.now().to_datetime())
    output += f"Instrument mounted:  {epics_data[0].values[-1]}\n"
    output += (f"Counterweights at:  {data['plc_cw_0']:.1f},"
               f" {data['plc_cw_1']:.1f},"
               f" {data['plc_cw_2']:.1f},"
               f" {data['plc_cw_3']:.1f}\n")
    # TODO Check if this is supposed to do something
    output += f"LN2 autofill systems:  Connected and turned on\n"
    output += (f"180L LN2 dewar scale:  SP1 {data['dewar_sp1_lb']:6.1f} lbs,"
               f" {data['dewar_sp1_psi']:6.1f} psi")

    return output


def main():
    print(query())


if __name__ == '__main__':
    main()

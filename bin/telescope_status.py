#!/usr/bin/env python3

import sys

from pathlib import Path
from astropy.time import Time

from bin import sjd, influx_fetch

try:
    import tpmdata
    tpmdata.tinit()
except ImportError:
    print("tpmdata unavailable")
    tpmdata = None

__version__ = "3.0.0"


def query():
    
    t_start = Time(sjd.sjd() - 0.3, format="mjd")
    t_end = Time.now()
    enclosure_path = Path(__file__).parent.parent / "flux/enclosure.flux"
    state = influx_fetch.query(enclosure_path.open('r').read(), t_start, t_end)[0]
    enclosure_hist = ""
    last_state = 0
    for row in state.records:
        if row.get_value() > last_state:
            last_state = row.get_value()
            t = Time(row.get_time())
            enclosure_hist += f"Opened at {t.isot[11:19]}\n"
        elif row.get_value() < last_state:
            last_state = row.get_value()
            t = Time(row.get_time())
            enclosure_hist += f"Closed at {t.isot[11:19]}\n"
    if enclosure_hist == "":
        enclosure_hist = "Closed all night\n"
            
        
    if tpmdata is None:
        raise ConnectionError("Cannot query the tpm without tpmdata installed")
    
    data = tpmdata.packet(1, 1)

    t = Time(data["ctime"], format="unix")
    output = enclosure_hist + '\n'
    output += f"Status at:  {t.isot[12:19]}Z\n"
    output += (f"Telescope stowed at:  "
               f"{data['az_actual_pos']*data['az_spt']/3600:>5.1f},"
               f" {data['alt_actual_pos']*data['alt_spt']/3600:>5.1f},"
               f" {data['rot_actual_pos']*data['rot_spt']/3600:>5.1f} mount\n")
    # epics_data = epics_fetch.get_data(["25m:mcp:instrumentNum"],
                                    #   start_time=Time.now().to_datetime(),
                                    #   end_time=Time.now().to_datetime())
    cart = "ECam" if data["inst_id_0"] == 0 else f"{data['inst_id_0']:.0f}"
    output += f"Instrument mounted:  {cart}\n"
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


if __name__ == "__main__":
    main()

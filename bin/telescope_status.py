#!/usr/bin/env python3

from pathlib import Path
from astropy.time import Time
import multiprocessing

from bin import sjd, influx_fetch

try:
    import tpmdata
except ImportError:
    tpmdata = None

__version__ = "3.0.0"


def get_tpm_packet(out_dict):
    tpmdata.tinit()
    data = tpmdata.packet(1, 1)
    for key, val in data.items():
        out_dict[key] = val
    return 0

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
    
    data = multiprocessing.Manager().dict()
    tpm_thread = multiprocessing.Process(target=get_tpm_packet, args=(data,))
    tpm_thread.start()
    tpm_thread.join(2)
    if tpm_thread.is_alive():
        tpm_thread.kill()
        raise ConnectionError("Could not reach TPM")

    t = Time(data["ctime"], format="unix")
    output = enclosure_hist + '\n'
    output += f"Status at:  {t.isot[12:19]}Z\n"
    output += (f"Telescope Position:  "
               f"{data['az_actual_pos']*data['az_spt']/3600:>5.1f},"
               f" {data['alt_actual_pos']*data['alt_spt']/3600:>5.1f},"
               f" {data['rot_actual_pos']*data['rot_spt']/3600:>5.1f} mount\n")
    # epics_data = epics_fetch.get_data(["25m:mcp:instrumentNum"],
                                    #   start_time=Time.now().to_datetime(),
                                    #   end_time=Time.now().to_datetime())
    cart = "FPS" if data["inst_id_0"] == 0 else f"{data['inst_id_0']:.0f}"
    output += f"Instrument mounted:  {cart}\n"
    output += (f"Counterweights at:  {data['plc_cw_0']:.1f},"
               f" {data['plc_cw_1']:.1f},"
               f" {data['plc_cw_2']:.1f},"
               f" {data['plc_cw_3']:.1f}\n")
    # TODO Check if this is supposed to do something
    if data["dewar_sp1_psi"] > 10:
        output += f"LN2 autofill systems:  Connected and turned on\n"
    else:
        output += f"LN2 autofill systems: Disconnected\n"
    output += (f"180L LN2 dewar scale:  SP1 {data['dewar_sp1_lb']:6.1f} lbs,"
               f" {data['dewar_sp1_psi']:6.1f} psi")

    return output


def main():
    print(query())


if __name__ == "__main__":
    main()

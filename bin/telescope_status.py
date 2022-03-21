#!/usr/bin/env python3
import numpy as np
from pathlib import Path
from astropy.time import Time
import multiprocessing

from bin import sjd, influx_fetch
from sdssobstools import sdss_paths

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

def get_enclosure_state(t_start, t_end, out_dict):
    enclosure_path = Path(
        sdss_paths.__file__).parent.parent / "flux/enclosure.flux"
    with enclosure_path.open('r') as fil:
        state = influx_fetch.query(fil.read(), t_start, t_end, interval="5m")[0]
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
    out_dict["enclosure_hist"] = enclosure_hist

def get_chiller_state(t_start, t_end, out_dict):
    chiller_path = Path(
        sdss_paths.__file__).parent.parent / "flux/chiller_status.flux"
    with chiller_path.open('r') as fil:
        table = influx_fetch.query(fil.read(), t_start, t_end, interval="1m")
    
    chiller_vals = {}
    for col in table:
        for row in col.records:
            if row.get_field() not in chiller_vals.keys():
                chiller_vals[row.get_field()] = row.get_value()
    # print(chiller_vals)
    for k in ["FLOW1", "FLOW2", "STATUS_FLUID_FLOW", "FLOW_USER_SETPOINT",
              "DISPLAY_VALUE"]:
        if k not in chiller_vals.keys():
            chiller_vals[k] = np.nan
    chiller_output = f"Chiller Flow: {chiller_vals['FLOW1']:.2f} L/min to FPS,"
    chiller_output += f" {chiller_vals['FLOW2']:.2f} L/min to GFAs,"
    chiller_output += f" {chiller_vals['STATUS_FLUID_FLOW']:.1f}"
    chiller_output += f"/{chiller_vals['FLOW_USER_SETPOINT']:.1f} gpm total\n"
    chiller_output += f"Chiller Temp: {chiller_vals['DISPLAY_VALUE']:.1f}C\n"
    
    alarms = []
    for key, val in chiller_vals.items():
        if "ALARM" in key:
            if val != 0:
                alarms.append((key, val))
    if len(alarms) == 0:
        chiller_output += "No chiller alarms\n"
    else:
        chiller_output += "Active chiller alarms:\n"
        for name, val in alarms:
            chiller_output += f"{name}: {val}\n"
            
    out_dict["chiller_output"] = chiller_output
        

def query():
    t_start = Time(sjd.sjd() - 0.3, format="mjd")
    t_end = Time.now()
    
    if tpmdata is None:
        raise ConnectionError("Cannot query the tpm without tpmdata installed")

    data = multiprocessing.Manager().dict()
    encl_thread = multiprocessing.Process(target=get_enclosure_state,
                                          args=(t_start, t_end, data))
    chiller_thread = multiprocessing.Process(target=get_chiller_state,
                                             args=(t_end - 15 / 60 / 24, t_end,
                                                   data))
    tpm_thread = multiprocessing.Process(target=get_tpm_packet, args=(data,))
    encl_thread.start()
    chiller_thread.start()
    tpm_thread.start()
    
    tpm_thread.join(2)
    chiller_thread.join(5)
    encl_thread.join(2)
    if tpm_thread.is_alive():
        tpm_thread.kill()
        raise ConnectionError("Could not reach TPM")
    if chiller_thread.is_alive():
        chiller_thread.kill()
        raise ConnectionError("Chiller query timeout")
    if encl_thread.is_alive():
        encl_thread.kill()
        raise ConnectionError("Enclosure query timeout")

    # print(data.keys())    
    t = Time(data["ctime"], format="unix")
    output = data["enclosure_hist"] + '\n'
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
               f" {data['dewar_sp1_psi']:6.1f} psi\n")
    output += data["chiller_output"]

    return output


def main():
    print(query())


if __name__ == "__main__":
    main()

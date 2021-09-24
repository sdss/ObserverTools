#!/usr/bin/env python3

from pathlib import Path

data_path = Path("/data/")  # For hub/normal computers
if not data_path.exists():
    data_path = Path("/data_hub/")  # For obs1 and obs2
    if not data_path.exists():
        data_path = Path.home() / "data/"  # For testing, usually on a Mac
        if not data_path.exists():
            raise FileNotFoundError("Cannot find the SDSS data directory")

ap_utr: Path = data_path / "apogee/utr_cdr"
ap_archive: Path = data_path / "apogee/archive"
ap_qr: Path = data_path / "apogee/quickred"
boss: Path = data_path / "spectro"
dos: Path = data_path / "manga/dos"
sos: Path = data_path / "boss/sos"
ecam: Path = data_path / "ecam"
gcam: Path = data_path / "gcam"
mcp_logs: Path = data_path / "logs/mcp"

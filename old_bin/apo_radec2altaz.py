#!/usr/bin/env python3
"""!/usr/bin/env python

This is a wrapper around RO scripts to
calculate HA, AZ, ALT, Airmass from RA and DEC
 for APO at current Python time

All input and output angles are in Degrees (except for airmass)

ask dmbiz
"""



import RO.Astro.Sph.Airmass
import RO.Astro.Sph.AzAltFromHADec
import RO.Astro.Tm.LMSTFromUT1
import RO.Astro.Tm.UTCFromPySec
from RO.Astro.Sph import AzAltFromHADec
from RO.Astro.Tm import UTCFromPySec

# a=RO.Astro.Tm.UTCFromPySec
# b = RO.Astro.Tm.LMSTFromUT1
# c = RO.Astro.Sph.AzAltFromHADec
# e = RO.Astro.Sph.Airmass
# -- specific APO settings --
lon = -105.820416667
lat = 32.780277777777776



class APOAirmass:

    @staticmethod
    def radec2altaz(ra, dec):
        a = RO.Astro.Tm.UTCFromPySec
        tpy = a.utcFromPySec()

        b = RO.Astro.Tm.LMSTFromUT1
        lmst = b.lmstFromUT1(tpy, lon)
        ha = lmst - ra

        c = RO.Astro.Sph.AzAltFromHADec
        d = c.azAltFromHADec([ha, dec], lat)

        az = d[0][0]
        alt = d[0][1]

        e = RO.Astro.Sph.Airmass
        air = e.airmass(alt)

        return [ha, air, az, alt]

    @staticmethod
    def radec2altaz_t(ra, dec, dt):
        # Same as radec2altaz, but calculates for "dt" seconds ahead
        a = RO.Astro.Tm.UTCFromPySec
        tpy = a.utcFromPySec() + dt / 86400.

        b = RO.Astro.Tm.LMSTFromUT1
        lmst = b.lmstFromUT1(tpy, lon)
        ha = lmst - ra

        c = RO.Astro.Sph.AzAltFromHADec
        d = c.azAltFromHADec([ha, dec], lat)

        az = d[0][0]
        alt = d[0][1]

        e = RO.Astro.Sph.Airmass
        air = e.airmass(alt)

        return [ha, air, az, alt]

    # Use "from RO.StringUtil import degFromDMSStr, dmsStrFromDeg"
    @staticmethod
    def st2ra(rast):
        # - given RAST = "HH:MM:SS.SS" calculates RA in Degrees
        a = rast.split(":")
        ra = 15. * (float(a[0]) + float(a[1]) / 60. + float(
            a[2]) / 3600.)
        return ra

    @staticmethod
    def st2dec(decst):
        # - given DECST = "-DD:MM:SS.SS" calculates DEC in Degrees
        a = decst.split(":")
        dec = abs(float(a[0])) + float(a[1]) / 60. + float(
            a[2]) / 3600.
        sing = 1.
        if float(a[0]) < 0.:
            sing = -1.
        dec = dec * sing
        return dec

# call as:
# import apo_radec2altaz
# a = apo_radec2altaz.apo_airmass()
# --------- a.radec2altaz(100.,20.)
# --------- --> a.ha   a.air  a.az   a.alt
#
# b = a.radec2altaz(100.,20.)        [ ha, air, az, alt ]
# --> [40.845, 1.276, 278.997, 51.52]    
# a.st2dec("-60:00:00.0")
# a.st2ra("12:01:02.345")

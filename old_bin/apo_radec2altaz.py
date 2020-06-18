#!/usr/local/bin/python
#!/usr/bin/env python3
#
# This is a wrapper around RO scripts to 
# calculate HA, AZ, ALT, Airmass from RA and DEC 
#  for APO at current Python time
#  
# All input and output angles are in Degrees (except for airmass)
#
# ask dmbiz

#-- specific APO settings --
lon =  -105.820416667 
lat =  32.780277777777776


from RO.Astro.Tm import UTCFromPySec, LMSTFromUT1
from RO.Astro.Sph import AzAltFromHADec, Airmass
from RO.StringUtil import degFromDMSStr, dmsStrFromDeg

import RO.Astro.Tm.UTCFromPySec
#a=RO.Astro.Tm.UTCFromPySec
import RO.Astro.Tm.LMSTFromUT1
#b = RO.Astro.Tm.LMSTFromUT1   
import RO.Astro.Sph.AzAltFromHADec
#c = RO.Astro.Sph.AzAltFromHADec   
import RO.Astro.Sph.Airmass
#e = RO.Astro.Sph.Airmass   

class apo_airmass:

  def radec2altaz(self, ra, dec):
    a = RO.Astro.Tm.UTCFromPySec
    tpy = a.utcFromPySec()

    b = RO.Astro.Tm.LMSTFromUT1
    lmst = b.lmstFromUT1(tpy, lon)
    ha = lmst - ra
    
    c = RO.Astro.Sph.AzAltFromHADec
    d = c.azAltFromHADec([ha, dec],lat)

    az = d[0][0]
    alt = d[0][1]

    e = RO.Astro.Sph.Airmass
    air = e.airmass(alt)

    return [ ha, air, az, alt ]


  def radec2altaz_t(self, ra, dec, dt):
    # Same as radec2altaz, but calculates for "dt" seconds ahead
    a = RO.Astro.Tm.UTCFromPySec 
    tpy = a.utcFromPySec() + dt/86400.

    b = RO.Astro.Tm.LMSTFromUT1
    lmst = b.lmstFromUT1(tpy, lon)
    ha = lmst - ra

    c = RO.Astro.Sph.AzAltFromHADec
    d = c.azAltFromHADec([ha, dec],lat)

    az = d[0][0]
    alt = d[0][1]

    e = RO.Astro.Sph.Airmass
    air = e.airmass(alt)

    return [ ha, air, az, alt ]





# Use "from RO.StringUtil import degFromDMSStr, dmsStrFromDeg"

  def st2ra(self, rast):
    #- given RAST = "HH:MM:SS.SS" calculates RA in Degrees
    self.a = rast.split(":")
    ra = 15. * (float(self.a[0]) + float(self.a[1])/60. + float(self.a[2])/3600.)
    return ra

  def st2dec(self, decst):
    #- given DECST = "-DD:MM:SS.SS" calculates DEC in Degrees
    self.a = decst.split(":")
    dec = abs(float(self.a[0])) + float(self.a[1])/60. + float(self.a[2])/3600.
    self.sign = 1.
    if float(self.a[0]) < 0.: self.sign = -1.
    dec = dec * self.sign
    return dec




# call as:
# import apo_radec2altaz
# a = apo_radec2altaz.apo_airmass()
#--------- a.radec2altaz(100.,20.)
#--------- --> a.ha   a.air  a.az   a.alt
#
# b = a.radec2altaz(100.,20.)        [ ha, air, az, alt ]
# --> [40.845, 1.276, 278.997, 51.52]    
# a.st2dec("-60:00:00.0")
# a.st2ra("12:01:02.345")

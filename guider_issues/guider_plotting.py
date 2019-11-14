import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import seaborn as sns
from astropy.time import Time
try:
    import starcoder42 as s
except:
    import sys
    sys.path.append('/home/dylangatlin/python/')
    import starcoder42 as s
import argparse

sns.set(style='darkgrid')

parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true',
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 00:00Z")
    parser.add_argument('-m', '--mjd',
                       help='If not today (-t), the mjd to search')
args = parser.parse_args()



ra = np.load('ra.npy')
dec = np.load('dec.npy')
rot = np.load('rot.npy')
times = Time(np.load('times.npy'))
# print(times)
good_exposures = ra > -50000

fig, axs = plt.subplots(3, 1, sharex=True, figsize=(8, 5))
raax, decax, rotax = axs
raax.plot_date(times.plot_date[good_exposures], ra[good_exposures] * 3600,
               alpha=0.85, c=(0.257, 0.451, 0.644), markersize=3)
raax.set_ylim(-4, 4)
raax.set_ylabel("Right Ascension\nError ('')")
# raax.axhline(-0.8, linewidth=0.5)
# raax.axhline(0.8, linewidth=0.5)
# raax.annotate('MaNGA Dither Envelope',
# (Time('2019-11-01 04:00').plot_date, 0.95))

decax.plot_date(times.plot_date[good_exposures], dec[good_exposures] * 3600,
                alpha=0.85, c=(0.386, 0.773, 0.238), markersize=3)
decax.set_ylim(-4, 4)
decax.set_ylabel("Declination\nError ('')")


rotax.plot_date(times.plot_date[good_exposures], rot[good_exposures] * 3600,
                alpha=0.85, c=(0.128, 0.515, 0.193), markersize=3)
rotax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
rotax.set_xlabel('t (UTC)')
rotax.set_ylim(-5, 5)
rotax.set_ylabel("Rotator\nError ('')")

for time in ['2019-11-01 02:04:00', '2019-11-1 10:01:00', '2019-11-1 11:15:00']:
    raax.axvline(Time(time).plot_date, c=(0.700, 0.322, 0.386), alpha=0.4,
            linewidth=10)
    decax.axvline(Time(time).plot_date, c=(0.700, 0.322, 0.386), alpha=0.4,
            linewidth=10)
    rotax.axvline(Time(time).plot_date, c=(0.700, 0.322, 0.386), alpha=0.4,
            linewidth=10)
fig.suptitle('Guider Axis Errors')

except IndexError:
    raise s.GatlinError('Please specify a filename to save to as an'
            ' argument. I recommend axes_errors_<mo>_<day>.png')
fig.savefig(fil_name)

def main():



if __name__ == '__main__':
    main()

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from astropy.time import Time
sns.set(style='dark')

ra = np.load('ra.npy')
dec = np.load('dec.npy')
rot = np.load('rot.npy')
times = Time(np.load('times.npy'))
print(times)
filter = ra > -50000

fig, axs = plt.subplots(3, 1, sharex=True, figsize=(10, 6))
raax, decax, rotax = axs
raax.plot_date(times.plot_date[filter], ra[filter]*3600, alpha=0.8, c='b', markersize=3)
raax.set_ylabel("Right Ascension\nError ('')")
raax.axvline(Time('2019-11-01 02:04:00').plot_date, c='r', alpha=0.3, linewidth=15)
decax.plot_date(times.plot_date[filter], dec[filter]*3600, alpha=0.8, c='g', markersize=3)
decax.set_ylim(-2, 2)
decax.set_ylabel("Declination\nError ('')'")
decax.axvline(Time('2019-11-01 02:04:00').plot_date, c='r', alpha=0.3, linewidth=15)
rotax.plot_date(times.plot_date[filter], rot[filter]*3600, alpha=0.8, c='r', markersize=3)
rotax.set_ylim(-5, 5)
rotax.set_ylabel("Rotator\nError ('')")
rotax.axvline(Time('2019-11-01 02:04:00').plot_date, c='r', alpha=0.3, linewidth=15)
fig.savefig('axes_errors.png')

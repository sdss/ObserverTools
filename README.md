# ObserverTools

This is a home for Python 3 tools which came from the sdss-hub:~/bin directory.
 It is designed primarily for SDSS-V usage. Individual file documentation will
 be on confluence at https://wiki.sdss.org/display/APO/Observing+Scripts.
 
### Moderators
Dylan Gatlin, Dmitry Bizyaev

### Authors
In addition to the moderators who maintain this repo, scripts were written by
 the following authors: Elena Malanushenko, Jon Brinkmann, Viktor Malanushenko,
 Kaike Pan, Stephen Bailey, Bernie
 
## Structure
Files that were once under sdss-hub:~/bin are now under old_bin, and Python 3
 scripts are now under bin. Any non-user tools are stored under python. All
 user tools have tests.

## Code Guidelines
All scripts designed for users should follow the SDSS Coding Standards, include
 a main function,
 and use argparse if arguments are needed. Prefer pathlib and fitsio. Scripts
 should try to be runnable on sdss-hub if possible. Anything in old_bin will
 be left there, but they are intended primarily for reference and you should
 avoid using them.
 
For now, avoid dependencies like opscore, actorkeys, and any other libraries
 that will be changing extensively as they upgrade to Python 3. RO has a Python
 3 PR that should be usable.
 
If a script is moved to bin, it should have a test file in tests that will run
 it in a few ways that we will likely use it during normal observing. Tests
 are critical for us maintaining code dependability.

## TODO
 - This package should be installable on hub using a setuptools or module
 
 - Add Travis CI to GitHub
 
 - Hide info panel and magnifier in ds9_live
  
## TimeTracking
Originally under sdss-hub:~/bin/time_tracking, it contains scripts designed for
 time tracking. These tools should generally be considered separate from the
 rest of the tools here, and are being left as their own "sub-repository" for
 the time being.
 
## Dependencies

### Python
The best way of installing all dependencies is to create an anaconda
 environment. This project will attempt to match STUI's version of Python.
```bash
conda create -f conda_env.yml
```

### Ubuntu
These libraries were needed on Ubuntu 20.04
```bash
sudo apt install libxt-dev libbz2-dev saods9 xpa-tools

```

## License
ObserverTools is licensed under a 3-clause BSD style license - see the
 LICENSE.md file.

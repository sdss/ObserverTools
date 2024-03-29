# ObserverTools

This is a home for Python 3 tools which came from the sdss-hub:~/bin directory.
 It is designed primarily for SDSS-V usage. Individual file documentation will
 be on confluence at <https://wiki.sdss.org/display/APO/Observing+Scripts>.

## Moderators

Dylan Gatlin, Dmitry Bizyaev

## Authors

In addition to the moderators who maintain this repo, scripts were written by
 the following authors: Elena Malanushenko, Jon Brinkmann, Viktor Malanushenko,
 Kaike Pan, Stephen Bailey, Bernie

## Installation

For observers at on their personal laptops, they can install these scripts via
 `pip install sdss-obstools`. The pip page can be found
 [here](https://pypi.org/project/sdss-obstools/). This will install the scripts
 in your current pip environment. To run, you must have proper tunnels to
 Influx/sdss5 servers.

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

If a script is moved to bin, it should have a test file in tests that will run
 it in a few ways that we will likely use it during normal observing. Tests
 are critical for us maintaining code dependability.

## TODO
  
### Python

The best way of installing all dependencies is to create an pyenv
 environment. This project is usually tested on Python 3.9. All the requirements
 can be found in requirements.txt

### Ubuntu

These libraries were needed on Ubuntu 20.04

```bash
sudo apt install libxt-dev libbz2-dev saods9 xpa-tools

```

## License

ObserverTools is licensed under a 3-clause BSD style license - see the
 LICENSE.md file.

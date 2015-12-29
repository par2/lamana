# LamAna

An extensible Python package for laminate analysis

## Installation

**From PyPI**: Install [anaconda](https://www.continuum.io/downloads), then simply run:

    $ pip install -r requirements.txt lamana

**Locally**: For developers, install [anaconda](https://www.continuum.io/downloads) and [git](https://git-scm.com/downloads). Then `git clone` one of the following branches into your development enviromnent: `develop` branch for lastest changes and the `master` branch for stable releases.

    $ git clone -b <branch name> https://github.com/par2/lamana
    $ conda create -n <testenv name> pip nose numpy matplotlib pandas
    $ source activate <testenv name>       # exclude source for Windows
    $ pip install -r requirements.txt
    $ pip install .                        # within lamana directory

*NOTE: installing requirements.txt uses "pinned" dependencies, which may upgrade/downgrade existing packages in your local environment.  See documentation for more details and alternative installation methods (marked for future release).*

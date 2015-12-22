# LamAna

An extensible Python package for laminate analysis

## Installation

**From PyPI**: the recommended option for installing a reproducibly-safe package is simply:

    $ pip install lamana -r requirements.txt

**Locally**: for the latest changes, `git clone` from the `develop` branch into your virtual envelope; clone from `master` for stable releases:


    $ git clone -b <branchname> https://github.com/par2/lamana
    $ pip install -r requirements.txt
    $ pip install -e .

*NOTE: this option installs a source distribution using "pinned" dependencies, which may upgrade/downgrade existing packages in your local environment.  See the documentation for more details and alternative installation options.*

## Details

This installation method assumes three primary dependencies are setup properly in your python environment: `numpy>=1.9.2`, `matplotlib>=1.4.3` and `pandas==0.16.2`.  

When Python 3.5 was released, many packages, including these dependencies, were updated to newer versions compatible with changes in Python 3.5.  Some changes in `pandas` broke this package, which lead to pinning dependencies.  While linux builds passed on travis, manually compiling these dependencies and sub-dependencies proved difficult both on linux and windows envirnments.  

This release therefore represents a stable pip-ready version for linux and local builds using python 2.7, 3.3, 3.4 and 3.5.  Some intermediate computing skill or determination may be required when install these packages.  A simplified pip installation is marked for a future release.

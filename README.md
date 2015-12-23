# LamAna

An extensible Python package for laminate analysis

## Installation

**Locally**: for the latest changes, `git clone` from the `develop` branch into your virtual envelope; clone from `master` for stable releases:

    $ git clone -b <branchname> https://github.com/par2/lamana
    $ pip install -r requirements.txt
    $ pip install -e .

*NOTE: this option installs a source distribution using "pinned" dependencies, which may upgrade/downgrade existing packages in your local environment.*

### Details

This installation method assumes three primary dependencies are setup properly in your python environment: `numpy>=1.9.2`, `matplotlib>=1.4.3` and `pandas==0.16.2`.  

Many dependencies were updated to newer versions compatible with the Python 3.5 release.  In particular the newer `pandas` broke this package, and this result led to pinning dependencies.  While Linux builds passed on Travis-CI, manually compiling these dependencies and sub-dependencies proved difficult both on linux and windows environments.  

This release therefore represents the final stable version for local (pre-PyPI) builds using python 2.7, 3.3, 3.4 and 3.5.  

### Drawbacks

Despite stability, setting up this version may prove challenging due to the setup demands of the dependencies.  Some installation drawbacks are list below:  

- intermediate computing skills (or patient determination) may be required when [compiling `numpy`](https://stackoverflow.com/questions/26473681/pip-install-numpy-throws-an-error-ascii-codec-cant-decode-byte-0xe2) on your system.
- `numpy` takes very long to compile
- `pandas` and `matplotlib` depend on `numpy`, which adds to installation time.  
- `pip install -r requirements.txt` thus often failed to install major pinned dependencies
- installing from wheels also failed

Most of these drawbacks will be alleviated simply by using `conda` instead, the  tested protocol of which is marked for a near-future release.

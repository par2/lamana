
.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: {}'.format(st))


.. parsed-literal::

    Last Run: 2016-01-09 19:57:08
    

Installation
============

These introductions explain how to install LamAna. We recommend
installing `Anaconda (Python 2.7.6+ or Python
3.3+) <https://www.continuum.io/downloads>`__.

How to install LamAna
---------------------

There are two simple options for installing LamAna. Open a terminal and
run one of the following options:

::

    $ pip install lamana                       # source (Default)

    $ pip install lamana --use-wheel           # binary

.. note::

    The first option is most succint and builds a LamAna installation from source. The second option builds more quickly from a binary that uses pre-compiled libraries.  Both options install the most current dependencies.

If either of the latter commands work fine, **you can skip the rest of
this section**. See the remaining instructions for more detailed
information.

Experienced Python users
------------------------

Installing reproducible environments from "pinned" dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes a dependency can be updated and break an upstream package. For
example, sub-dependencies may require non-pythonic extensions to build
correctly such as C/C++ compiliers. Thus, a list of frozen version
numbers or "pinned dependencies" are included in a special
requirements.txt file, which can be invoked at installation to mimic the
original release environment.

::

    $ pip install lamana -r requirements.txt   # source (Recommended)

The latter option generates an installation using pinned dependencies
that have been tested and are known to work correctly at the time of
release. This approach is considered "hands-on" because installing
pinned dependencies may downgrade or upgrade some local packages (see
affected dependencies in requirements.txt). This precaution is made to
protect your native environment from unintended changes. However,
consider installing with requirements.txt if the default installation
commands fail or bugs are detected.

.. note::

    By default, pinned dependencies were not included in LamAna's `setup.py`. Thus the first installation methods serve as a minimally invasive, "hands-off" approaches.  

.. seealso::

    See the requirement.txt file for a list of pinned dependencies possibly influnced by the latter command.

Installing from wheels (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ideally we would prefer to offer a reproducible binary option as well,
but there is currently no straightforward way of installing requirements
of a binary from PyPI, as all data is meta and encased in the ``.whl``
file. Unlike a source distribution, which may contain the
``requirements.txt`` file, wheels do not appear to include the necessary
root directory files. Should you desire a reproducible binary
installation, the workaround for this technicality is to download/clone
the corresponding release package from github and point the ``-r`` flag
to the location of the downloaded ``requirements.txt`` file.

::

    $ pip install lamana --use-wheel -r /path/to/requirements.txt  # binary  

Installing dependencies from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**In the absence of Anaconda**, installing the three major
dependendencies from source can be tedious and arduous, specifically
``numpy``, ``pandas`` and ``matplotlib``. Here are some reasons and tips
`1 <https://stackoverflow.com/questions/26473681/pip-install-numpy-throws-an-error-ascii-codec-cant-decode-byte-0xe2>`__,
`2 <https://stackoverflow.com/questions/25674612/ubuntu-14-04-pip-cannot-upgrade-matplotllib>`__
for installing dependencies if they are not setup on your system.

On Debian-based systems, install the following pre-requisites.

::

    $ apt-get install build-essential python3-dev

On Windows systems, be certain to install the `appropriate Visual Studio
C-compilers <https://matthew-brett.github.io/pydagogue/python_msvc.html>`__.

.. note::

    Installing dependencies on windows can be troublesomes.  See the `installation guide for matplotlib <http://matplotlib.org/users/installing.html>`_. Try `this <https://github.com/matplotlib/matplotlib/issues/3029/>`_ or `this <http://newcoder.io/dataviz/part-0/>`_ for issues installing matplotlib.   Future developments will work towards OS agnostiscism with continuous Integration on Linux, OS and Windows using Travis and Appveyor. 

Creating a developer environment with ``conda``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minimal LamAna development requires testing code in a reproducible
enviroment. Anaconda is the most consistent option for test environments
of dependencies and sub-dependencies. `Here is a supporting
rationale <https://gist.github.com/dan-blanchard/7045057>`__ for using
``conda`` in travis. The following creates a fresh conda environment
with critical dependencies that trigger installation of sub-dependencies
required for LamAna.

.. code:: bash

    $ git clone -b <branch name> https://github.com/par2/lamana
    $ conda create -n <testenv name> pip nose numpy matplotlib pandas
    $ source activate <testenv name>       # exclude source for Windows 
    $ pip install -r requirements.txt
    $ pip install .                        # within lamana directory

The first command downloads the repo from a spefic branch using
```git`` <https://git-scm.com/downloads>`__. The second command creates
a reproducbile virtual environment using ``conda`` where therein,
isolated versions of pip and nose are installed. Specific dependencies
of the latest versions are downloaded within this environment which
contain a necessary backend of sub-dependencies that are difficult to
install manually. The environment is activated in the next command. Once
the conda build is setup, ``pip`` will downgrade the existing versions
to the pinned versions found in the requirments.txt file. Afterwards,
the package is finally installed mimicking the original release
environment.

The latter installation method should work fine. To check, the following
command should be able to run without errors:

::

    $ nosetests

Now, you should be able to run include jupyter notebook Demos.

.. important::

    If issues still arise, ensure the following requisites are satisfied:
    
    - the conda environment is properly set up with dependencies and compiled sub-dependencies e.g. C-extensions (see above)
    - the appropriate `compiler libraries <https://github.com/pydata/pandas/issues/1880>`_ are installed `on your specific OS <https://matthew-brett.github.io/pydagogue/python_msvc.html>`_, i.e. gcc for Linux, Visual Studio for Windows.  With conda, this should not be necessary.
    - `sufficient memory <http://ze.phyr.us/pandas-memory-crash/>`__ is available to compile C-extensions, e.g. 0.5-1 GB minimum
    - the appropriate LamAna version, compatible python version and dependency versions are installed according to requirements.txt (see the :ref:`Dependencies chart <dependencies-chart>`)

.. _dependencies-chart:

Dependencies
~~~~~~~~~~~~

The following table shows a chart of tested build build compatible with
LamAna:

+----------+---------------------------------------+-------------------------------------------------------------------+--------------------+
| lamana   | python                                | dependency                                                        | OS                 |
+==========+=======================================+===================================================================+====================+
| 0.4.8    | 2.7, 3.3, 3.4                         | numpy==1.9.2, pandas==0.16.2, matplotlib==1.4.3                   | linux, not win10   |
+----------+---------------------------------------+-------------------------------------------------------------------+--------------------+
| 0.4.8    | 2.7, 3.3, 3.4, 3.5, 3.5.1             | numpy==1.10.1, pandas==0.16.2, matplotlib==1.4.3                  | linux              |
+----------+---------------------------------------+-------------------------------------------------------------------+--------------------+
| 0.4.8    | 2.7.6, 2.7.10, 3.3, 3.4, 3.5, 3.5.1   | numpy==1.10.1, pandas==0.16.2, matplotlib==1.5.0                  | linux, local win   |
+----------+---------------------------------------+-------------------------------------------------------------------+--------------------+
| 0.4.9    | 2.7, 3.3, 3.4, 3.5, 3.5.1             | conda==3.19.0, numpy==1.10.1, pandas==0.16.2, matplotlib==1.4.3   | linux, win         |
+----------+---------------------------------------+-------------------------------------------------------------------+--------------------+


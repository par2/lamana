
.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: ', st)


.. parsed-literal::

    Last Run:  2016-01-12 02:07:27
    

Resources
=========

If you are new to developing, here are some resources to get started on
this project.

-  `git <https://git-scm.com/downloads>`__: default version control
-  `gitflow-avh <https://github.com/petervanderdoes/gitflow-avh>`__: a
   git extension used to ease development workflow
-  `atom <https://atom.io/>`__: an great text editor

The following packages are available in ``conda`` or ``pip``:

-  `virtualenv <https://github.com/pypa/virtualenv>`__: create
   reproducible, isolated virtual enviroments
-  `vituralenvwrapper <https://bitbucket.org/dhellmann/virtualenvwrapper>`__:
   simplify virtualenv creation; see also
   `virtualenvwrapper-win <https://pypi.python.org/pypi/virtualenvwrapper-win>`__
   for Windows
-  `nose <https://nose.readthedocs.org/en/latest/>`__: test code; see
   also ``pytest`` alternative.

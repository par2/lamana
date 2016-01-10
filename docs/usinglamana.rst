
.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: {}'.format(st))


.. parsed-literal::

    Last Run: 2016-01-08 16:27:52
    

Using LamAna with Jupyter
=========================

LamAna can work in commandline, but was developed to work best with the
IPython/Jupter Notebook (v3.2.0+/4.0+). As of ``lamana 0.4.9``,
``notebook`` is only a dependency frozen in the requirements.txt file;
by default it must be installed separately. It is typically package with
conda (`see documentation for
installation <https://jupyter.readthedocs.org/en/latest/install.html>`__)\`.
See examples of notebooks in the github repository.

Plotting does not work well in commandline. Plots work best in Jupyter
with some backend initiated using idiomatic IPython magics e.g.
``%matplotlib inline``



.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: ', st)


.. parsed-literal::

    Last Run:  2016-01-12 03:59:50
    

Testing
=======

Testing code with ``nose``
--------------------------

The current testing suite is ``nose``. From the root directory, you can
test all files prepended with "test\_" by running:

::

    $ nosetests

There are three types of tests in source ``lamana`` directory:

1. module tests: normal test files located in the "./tests" directory
2. model tests: test files specific for custom models, located in
   "./models/tests"
3. controls: .csv files located "./tests/controls\_LT"

Models tests are separated to support an extensibile design for author
contributions. Therefore, authors can create models and tests together
without a separate pull requests to the standard module directory.

.. note::

    The locations for tests may change in future releases.

Control files
-------------

LamAna maintains .csv files with expected data for different lamanate
configurations. These files are tested with the ``test_controls``
module. This mdule reads each control file and parses information such
as layer numbers, number of points per layer and geometry. Control files
are named by these variables.

Controls files can be created manually, but it may be simpler to make,
then edit a starter file. This process can be expedited for multiple
files by passing LaminateModels into the ``utils.tools.write_csv()``
function. This function will create a csv file for every LaminateModel,
which can be altered as desired and tested by copying into the
"lamana/tests/controls\_LT" folder.


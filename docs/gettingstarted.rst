
.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: {}'.format(st))


.. parsed-literal::

    Last Run: 2016-01-08 16:27:52
    

Getting Started
===============

Using LamAna with Jupyter
-------------------------

LamAna can work in commandline, but was developed to work best with the
IPython/Jupter Notebook (v3.2.0+/4.0+). As of ``lamana 0.4.9``,
``notebook`` is only a dependency frozen in the requirements.txt file;
by default it must be installed separately. It is typically package with
conda (`see documentation for
installation <https://jupyter.readthedocs.org/en/latest/install.html>`__)\`.
See examples of notebooks in the github repository.

Plotting does not work well in commandline. Plots work best in Jupyter
with some backend initiated using idiomatic IPython magics e.g.
``%matplotlib inline``.

The user starts by importing the desired Feature module, e.g.
``distributions`` for plots of stress or strain distributions. By using
a Feature module, they indirectly access the ``input_`` module through
by calling the ``apply()`` method.

.. note ::

    Indirect access to `input` was decided because importing `input_` to then access a Feature seemed cumbersome and awkward.  To reduce user boilerpoint, the specific Feature module became the frontend while the input transactions merged with the backend.

We will now explore how the user can **input data** and **generate
plots** using the ``distributions`` module.

User Setup
----------

First we must input loading parameters and material pproperties.
Secondly, we must invoke a selected laminate theory. The former requires
knowlege of the specimen dimensions, the materials properties and
loading configuration. For illustration, an example schematic of
laminate loading parameters is provided below.

.. figure:: ./_images/Schematic%20-%20Loading%20Parameters%206.png
   :alt: Loading Parameters

   Loading Parameters
A table is provided defining the illustrated parameters. These loading
parameters are coded in a dictionary called ``load_params`` (see
Tutorial).

+-------------+--------------+------------------------------------------------+
| Parameter   | Units (SI)   | Definition                                     |
+=============+==============+================================================+
| *P*         | N            | applied load                                   |
+-------------+--------------+------------------------------------------------+
| *R*         | m            | specimen radius                                |
+-------------+--------------+------------------------------------------------+
| *a*         | m            | support radius                                 |
+-------------+--------------+------------------------------------------------+
| *b*         | m            | piston radius                                  |
+-------------+--------------+------------------------------------------------+
| *r*         | m            | radial distance from central loading           |
+-------------+--------------+------------------------------------------------+
| *p*         | -            | graphical points or DataFrame rows per layer   |
+-------------+--------------+------------------------------------------------+

User Defined Parameters
~~~~~~~~~~~~~~~~~~~~~~~

Sample code is provided for setting up geometric dimensions, loading
parameters and material properties.

.. code:: python

    # SETUP -----------------------------------------------------------------------

    import lamana as la

    # Build two dicts of loading and material parameters
    load_params = {
        'P_a': 1,                                              # applied load 
        'R': 12e-3,                                            # specimen radius
        'a': 7.5e-3,                                           # support radius 
        'p': 4,                                                # points/layer
        'r': 2e-4,                                             # radial distance from center loading
    }

    # Using Quick Form (See Standard Form)
    mat_props = {
        'HA': [5.2e10, 0.25],                                  # modulus, Poissions
        'PSu': [2.7e9, 0.33],            
    }

    # Build a list of geometry strings to test.  Accepted conventions shown below:
    # 'outer - [{inner...-...}_i] - middle'

    geos1 = ['400-400-400', '400-200-800', '400-350-500']      # = total thickness
    geos2 = ['400-[400]-400', '400-[200,100]-800']             # = outer thickness 
    #------------------------------------------------------------------------------

Generate Data in 3 Lines
------------------------

With the **loading and material** information, we can make stress
distribution plots using Python to define (reusable) test **cases** by
implementing 3 simple steps.

1. Instantiate a Feature object with loading and material parameters
   (generates makes a user Case object)
2. ``apply()`` a model to a test with desired geometries (assumes
   mirrored at the neutral axis)
3. ``plot()`` the case object based on the chosen feature

Once the parameters geometries are set, in three lines of code, you can
build a case and simultaneiously plot stress distributions for an
indefinite number of laminates varying in compostion and dimension
within seconds. Conveniently, the outputs are common Python data
structures, specifically ``pandas`` DataFrames and ``matplotlib``
graphical plots ready for data munging and analysis.

.. code:: python

    case1 = la.distributions(load_params, mat_props)           # instantiate
    case1.apply(geos1, model='Classic_LT')                     # apply 
    case1.plot()                                               # plot 

A case stores all of the laminate data for a particular set of
parameters in two forms: a dict and a DataFrame (see tutorial for
details). Once a case is built, there serveral covenient builtin
attributes for accessing this data for further analysis.

.. code:: python

    '''Add mini api docs'''

.. code:: python

    # Case Attributes
    case.geometries                                            # geometry object
    case.total                                                 # total laminate thickness (all)                
    case.inner                                                 # layer thickness (all)    
    case.total_inner                                           # total layer type (all) 
    case.total_inner[0]                                        # slicing
    case.total_inner_i                                         # total inner layers
    case1.snapshot                                             # list of all geometry stacks (unique layers)
    case1.frames                                               # list all DataFrames (all layers)

We can perform sepearate analyses by building different cases and apply
different models (default model: "Wilson\_LT" for circular disks in
biaxial flexure).

Extensibilty
~~~~~~~~~~~~

Is Classical Laminate Theory incompatible with for your analysis?
Fortunately, **LamAna is extensible**. Users can define modified
laminate theory models and apply these to cases (see theories section
for details).

.. code:: python

    # Classical Laminate Theory
    case2 = la.distributions(load_params, mat_props)           # instantiate 
    case2.apply(geos2, model='Classical_LT')                   # apply model
    case2.plot()

    # Custom Biaxial Flexure Model
    case3 = la.distributions(load_params, mat_props)           # instantiate 
    case3.apply(geos2, model='Wilson_LT')                      # custom model
    case3.plot()



.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: {}'.format(st))


.. parsed-literal::

    Last Run: 2016-01-14 01:27:50
    

LPEP
====

LamAna Python Enhancement Proposals (LPEP) and Micro PEPs.

.. seealso ::

    The LPEP `types <https://www.python.org/dev/peps/pep-0001/#pep-types>`_, `submission <https://www.python.org/dev/peps/pep-0001/#id29>`_ and `content <https://www.python.org/dev/peps/pep-0001/#id32>`_  guidelines closely follows PEP 0001.  
    
.. note ::

    Most Active LPEPs include a Next Action Section.

LPEP 001: Standards
-------------------

-  **Status: Active**
-  **Type: Process**
-  **Date: Epoch**
-  **Current Version: 0.1**

This LPEP preserves best practices, standards or customs for develpopers
that maintain code consistency. Tne following micro-PEPs are numerically
assigned. New micro-PEPs will be added over time or modified with
caution.

1.  A *General Convention* will be standardized for internal code, such
    that the inner layer(s) is/are consistently returned as a list of
    floats i.e. ``400-[200]-800`` and ``400-[100-100]-800``. This format
    is used to maintain type checking consistency within the code.
    External use by the user input is not bound by this restriction
    however; shorthand notation is fine too, e.g. ``400-200-800``. Such
    notation will be internally converted to the General Convention.
2.  Except for user values such as layer thicknesses and total
    calculations (microns, um), all other internal, dimensional
    variables will assume SI units (i.e. meters, m). These values will
    be converted for convenience for the user in the DataFrames, (e.g.
    millimeters, mm). This PEP is adopted to limit excessive unit
    conversions within code.
3.  Per PEP 8, semi-private variables are marked with a single preceding
    underscore, i.e. ``_check_layer_order()``. This style is used to
    visually indicate internal methods/attributes, not particularly
    important for the user. Double underscores will only be used
    (sparingly) to prevent name collisions. Internal hook methods with
    use both trailing and leading underscores, e.g. ``_use_model_``.
4.  The true lamina thickness value (``t_``) will remain constant in the
    DataFrame and not vary with height (``d_``).
5.  In general, use convenient naming conventions that indicate modules
    where the objects originates, e.g. ``FeatureInput`` object. However,
    whenever possible, aim to use descriptive names that reduce
    confusion over convienient names, e.g. ``LaminateModel`` object
    instead of ``ConstructsTheories`` object.
6.  For compatibilty checks, run nose 2.x and nose 3.x before commits to
    target Py3to2 errors in tests, (e.g. ``dict.values()``).
7.  Materials parameters are handled internally as a dict formatted in
    *Standard Form* (compatible with pandas DataFrames) , but it is
    displayed as a DataFrame when the materials attribute is called by
    the user. The Standard form comprises a dict of materials property
    dicts. By contrast, a *Quick Form* is allowed as input by the user,
    but interally converted to the Standard Form.

    -  Quick Form: ``{Material: [Modulus value, Poissons value], ...}``
    -  Standard Form:
       ``{'Modulus': {'Mat1': value,...},'Poissons': {'Mat1': value, ...}``

8.  Internally, middle layers from ``Geometry`` return the full
    thickness, not the symmetric thickness.
9.  Thicknesses will be handled this way.

    -  :math:`t` is the total laminate thickness
    -  :math:`t_k` is the thickess at lamina ``k``
    -  ``t_`` is the internal variable that refers to true lamina
       thicknesses.
    -  The DataFrame column label :math:`t(um)` will refer to lamina
       thicknesses.
    -  ``h_`` is also a lamina thickness, relative to the neutral axis;
       therefore middle layers (and ``h_``) are symmeric about the
       neutral axis :math:`t_{middle} = 2h_{middle}`

10. p=2 give the most critical points to calculate - interfacial minima
    and maxima per layer. Maxima correlate with the 'interface'
    ``label_`` and minima correspond to the 'discont.' ``label_``.
    However, at minimun it is importannt to test with p>=5 to calculate
    all point types (interfacial, internals and neutural axes)
    perferably for odd plies.
11. in geometry strings, the dash character ``-`` separates layer types
    outer-inner-middle. The comma ``,`` separates other things, such as
    similar layer types, such as inner\_i -[200,100,300]-. The following
    is an invalid geomtry string ``'400-[200-100-300]-800'``.
12. Two main branches will be maintained: "master" and "stable".
    "master" will reflect development versions, always ahead of stable
    releases. "stable" will remain relatively unchanged except for minor
    point releases to fix bugs.
13. This package will adopt `semantic versioning <http://semver.org/>`__
    format (MAJOR.MINOR.PATCH). >- MAJOR version when you make
    incompatible API changes, >- MINOR version when you add
    functionality in a backwards-compatible manner, and >- PATCH version
    when you make backwards-compatible bug fixes.
14. Package releases pin dependencies to prevent breakage due to
    dependency patches/updates. This approach assumes the development
    versions will actively address patches to latest denpendency updates
    prior to release. User must be aware that installing older versions
    may downgradetheir current installs.

Copyright
^^^^^^^^^

This document has been placed in the public domain.

LPEP 002: Extending ``Cases`` with Patterns
-------------------------------------------

-  **Status: Draft**
-  **Type: Process**
-  **Date: October 01, 2015**
-  **Current Version: 0.4.4b**

Motivation
^^^^^^^^^^

As of 0.4.4b, a ``Cases`` object supports a group of cases distinguished
by different ps where each case is a set of LaminateModels with some
pattern that relates them. For example, an interesting plot might show
multiple geometries of:

-  Pattern A: constant total thickness
-  Pattern B: constant midddle thickness

In this example, two cases are represented, each comprising
LaminateModels with geometries satisfying a specific pattern. Currently
``Cases`` does not support groups of cases distinguished by pattern, but
refactoring it thusly should be simple and will be discussed here. Our
goal is to extend the ``Cases`` class to generate cases that differ by
parameters other than ``p``.

Desired Ouptut
^^^^^^^^^^^^^^

To plot both patterns together, we need to feed each case seperately to
plotting functons. We need to think of what may differ between cases:

-  p
-  loading parameters
-  material properties
-  different geometries, similar plies
-  number plies (complex to plot simulataneously)
-  orientation (not implemented yet)
-  ...

Given the present conditions, the most simple pattern is determined by
geometry. Here are examples of cases to plot with particular patterns of
interest.

.. code:: python

    # Pattern A: Constant Total Thickness
    case1.LMs = [<LamAna LaminateModel object (400-200-800) p=5>,
                 <LamAna LaminateModel object (350-400-500) p=5>,
                 <LamAna LaminateModel object (200-100-1400) p=5>,
                ]

    # Pattern B: Constant Middle and Total Thickness
    case2.LMs = [<LamAna LaminateModel object (400-200-800) p=5>,
                 <LamAna LaminateModel object (300-300-800) p=5>,
                 <LamAna LaminateModel object (200-400-800) p=5>,
                ]

Specification
^^^^^^^^^^^^^

To encapsulate these patterns, we can manually create a dict of keys and
case values. Here the keys label each case by the pattern name, which
aids in tracking what the cases do. The ``Cases`` dict should emulate
this modification to support labeling.

.. code:: python

    cases = {'t_total': case1,
             'mid&t_total': case2,}

``Cases`` would first have to support building different cases given
groups of different geometry strings. Perhaps given a dict of geometry
strings, the latter object gets automatically created. For example,

.. code:: python

    patterns = {
        't_total': ['400-200-800', '350-400-500', '200-100-1400'],
        'mid&t_total': ['400-200-800', '300-300-800', '200-400-800'],
    }

The question then would be, how to label different ps or combine
patterns i.e., t\_total and ps. Advanced ``Cases`` creation is a project
for another time. Meanwhile, this idea of plotting by dicts of this
manner will be beta tested.

Next Actions
^^^^^^^^^^^^

-  Objective: organize patterns of interest and plot them easily with
   ``Case`` and ``Cases`` plot methods.

   -  Refactor Case and Cases to handle dicts in for the first arg.
   -  Parse keys to serve as label names (priority).
   -  Iterate the dict items to detect groups by the comma and generate
      a caselets for cases, which get plotted as subplots using an
      instanace of \`output\_.PanelPlot'

See Also
^^^^^^^^

-  LPEP 003

Copyright
^^^^^^^^^

This document has been placed in the public domain.

LPEP 003: A humble case for ``caselets``
----------------------------------------

-  **Status: Accepted**
-  **Type: Process**
-  **Date: October 05, 2015**
-  **Current Version: 0.4.4b**

Motivation
^^^^^^^^^^

By the final implementation of 0.4.4b, each case will generate a plot
based on laminate data given loading, material and geometric
information. Single plots are created, but subplots are desired also,
where data can be compared from different cases in a single figure. This
proposal suggests methods for achieving such plots by defining a new
case-related term - a ``caselet`` - and its application to a figure
object comprising subplots, termed ``PanelPlot``.

Definitions
^^^^^^^^^^^

-  **LaminateModel** (LM): an object that combines physical laminate
   dimensions and laminate theory data, currently in the form of
   DataFrames.
-  **case**: a group of LMs; an analytical unit typically sharing
   similar loading, material and geometric parameters. The final outcome
   is commonly represented by a matplotlib axes.
-  **cases**: a group of cases each differentiated by some "pattern" of
   interest, e.g. p, geometries, etc. (see LPEP 002).
-  **caselet**: (new) a sub-unit of a case or cases object. Forms are
   either a single geometry string, list of geometry strings or list of
   cases. The final outcome is commonly represented as a matplotlib
   axes, or subplot component (not an instance or class).

Containing Caselets
^^^^^^^^^^^^^^^^^^^

The generation of caselets as matplotlib subplots requires us to pass
objects into ``Case`` or ``Cases``. To pass in caselets, a container
must be used (e.g. list or dict) to encapsulate the objects. Here this
type of caselet could be a string, list or case. If a list is used,
there are at least three options for containing caselets:

1. A list of geometry strings: ``type(caselet) == str``
2. A nested list of geometry strings: ``type(caselet) == list``
3. A list of cases:
   ``type(caselet) == <LamAna.distributions.Case object>``

If a dict is used to contain caselets, the latter options can substitute
as dict values. The keys can be either integers or explict labels.
*NOTE: a List of caselets will be implemented in 0.4.5. Dict of caselets
may or may not be implemented in future versions.*

The following will not be implemented in v0.4.5.

Dict of Caselets
''''''''''''''''

*Key-value pairs as labeled cases.*

(NotImplemented) What if we want to compare different cases in a single
figure? We can arrange data for each case per subplot. We can abstract
the code of such plots into a new class ``PanelPlot``, which handles
displaying subplots. Let's extend ``Cases`` to make a ``PanelPlot`` by
supplying a dict of cases.

::

    >>> dict_patterns = {'HA/PSu': case1,
    ...                  'mat_X/Y': case2,}
    >>> cases = la.distributions.Cases(dict_patterns)

    Figure of two subplots with three differnt patterns for two laminates with different materials. 

    .. plot::
            :context: close-figs

            >>> cases.plot()

*Key-value pairs as labeled lists*

(NotImplemented) We could explicitly try applying a dict of patterns
instead of a list. This inital labeling by keys can help order patterns
as well as feed matplotlib for rough plotting titles. Let's say we have
a new case of different materials.

::

    >>> dict_patterns = {
    ...    't_tot': ['400-200-800', '350-400-500', '200-100-1400'],
    ...    't&mid': ['400-200-800', '300-300-800', '200-400-800'],
    ...    't&out': ['400-200-800', '400-100-1000', '400-300-600']
    ... }
    >>> new_matls = {'mat_X': [6e9, 0.30],
    ...              'mat_Y': [20e9, 0.45]}
    >>> cases = la.distributions.Cases(
    ...     dict_patterns, dft.load_params, new_matls
    ... )

    Figure of three subplots with constant total thickness, middle and outer for different materials. 

    .. plot::
            :context: close-figs

            >>> cases.plot()

*Key-value pairs as numbered lists*

(NotImplemented) We can make a caselets in dict form where each key
enumerates a list of geometry strings. This idiom is probably the most
generic. [STRIKEOUT:This idiom is currently accepted in
``Cases.plot()``.] Other idioms may be developed and implemented in
future versions.

::

    >>> dict_caselets = {0: ['350-400-500',  '400-200-800', '200-200-1200',
    ...                      '200-100-1400', '100-100-1600', '100-200-1400',]
    ...                  1: ['400-550-100', '400-500-200', '400-450-300',
    ...                      '400-400-400', '400-350-500', '400-300-600'],
    ...                  2: ['400-400-400', '350-400-500', '300-400-600',
    ...                      '200-400-700', '200-400-800', '150-400-990'],
    ...                  3: ['100-700-400', '150-650-400', '200-600-400',
    ...                      '250-550-400', '300-400-500', '350-450-400'], 
    ...                 }
    >>> #dict_patterns == dict_caselets
    >>> cases = la.distributions.Cases(dict_caselets)

    Figure of four subplots with different caselets.  Here each caselet represents a different case (not always the situation). 

    .. plot::
            :context: close-figs

            >>> cases.plot()

Next Actions
^^^^^^^^^^^^

-  Objective: Make abstract ``PanelPlot`` class that accepts dicts of
   LMs for cases to output figures of caselets or cases.

   -  build ``PanelPlot`` which wraps matplotlib subplots method.
   -  inherit from ``PanelPlot`` in ``Case.plot()`` or ``Cases.plot()``
   -  implement in ``output_``
   -  make plots comparing different conditions in the same ``Case``
      (caselets)
   -  [STRIKEOUT:make plots comparing different cases using ``Cases``]

-  Abstract idiom for building caselets accepted in ``Cases.plot()``.

Copyright
^^^^^^^^^

This document has been placed in the public domain.

LPEP 004: Refactoring ::class:: ``Stack``
-----------------------------------------

-  **Status: Draft**
-  **Type: Process**
-  **Date: October 20, 2015**
-  **Current Version: 0.4.4b1**

Motivation
^^^^^^^^^^

Inspired to adhere to classic data structures, we attempt to refactor
some classes. The present ``constructs.Stack`` class is not a true
stack. Athough built in a LIFO style, there are no methods for reversing
the stack. It may be beneficial to the user to add or delete layers on
the fly. Stacks, queues and other data structures have methods for such
manipulations. Here are some ideas that entertain this train of thought.

-  Insert and remove any layers
-  Access geometry positions in an index way

Examples
^^^^^^^^

.. code:: python

    >>> LM = la.distributions.Cases('400-200-800').LMs
    >>> LM.insert('-[-,100]-')
    >>> print(LM.geometry, LM.nplies)
    <Geometry object (400-[200,100]-800)>, 7

    >>> LM.remove('outer')
    >>> print(LM.geometry, LM.nplies)
    <Geometry object (0-[200,100]-800)>, 5

    >>>LM.insert((1, 1), 50)
    >>>LM.remove(0)
    >>> print(LM.geometry, LM.nplies)
    <Geometry object (0-[200,50,100]-0)>, 6
    >>>LM.remove('inner_i')
    >>> print(LM.geometry, LM.nplies)
    <Geometry object (0-[0]-0)>, 0

Next Actions
^^^^^^^^^^^^

-  Complete LPEP 004

Copyright
^^^^^^^^^

This document has been placed in the public domain.


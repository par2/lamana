
.. LamAna documentation master file, created by
   sphinx-quickstart on Tue Jan 05 14:44:04 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
LamAna Documentation
====================

.. TODO: Not sure why the pdf renders this section incorrectly on RTD.

The LamAna project is an extensible Python library for interactive laminate
analysis and visualization.

.. sidebar:: What's New in LamAna

   - appveyor builds (support on Windows)

LamAna enables users to **calculate**/**export**/**analyze** and
**author** custom models based on laminate theory.  *Feature modules*  can be
used to plot stress distributions, analyze thickessness effects and
predict failure trends.

User Benefits
-------------

The primary benefits to users is an scientific package that:

-  **Simplicity**: given a model and parameters, analysis begins with
   three lines of code
-  **Visualization**: plotting and physical representations
-  **Analysis**: fast computational analysis using a Pandas backend
-  **Extensibility**: anyone with a little Python knowledge can
   implement custom laminate models
-  **Speed**: data computed, plotting and exported for dozens of
   configurations within seconds

Community Benefits
------------------

Long-term goals for the laminate community are:

-  **Standardization**: general abstractions for laminate theory
   analysis
-  **Common Library**: R-like acceptance of model contributions for
   everyone to use


.. _gallery-docs:

.. toctree::
   :maxdepth: 1
   :caption: Gallery

   showcase

.. _user-docs:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   installation
   gettingstarted
   api
   support

.. _author-docs:

.. toctree::
   :maxdepth: 2
   :caption: Author Documentation

   writecustom

.. _dev-docs:

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   package
   components
   installation2
   contributions
   testing
   docs
   demo
   lpep
   versions


Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

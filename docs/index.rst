
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

   - Developer Release Cycle Workflow
   - Shippable (CI for unpinned builds)

LamAna enables users to **calculate**/**export**/**analyze** data and
**author** custom models based on laminate theory.  *Feature modules*  are used to plot stress distributions, analyze thickessness effects and
predict failure trends.

User Benefits
-------------

The primary benefits to users is an scientific package with these characteristics:

-  **Simplicity**: given a model and parameters, analysis can start with
   three simple lines of code
-  **Visualization**: plotting distributions and physical representations
-  **Analysis**: fast computational analyses using a Pandas backend
-  **Extensibility**: anyone with a little Python knowledge can
   implement custom laminate models; otherwise, it is easy to learn
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
   :hidden:
   :maxdepth: 1
   :caption: Gallery

   showcase

.. _user-docs:

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: User Documentation

   installation
   gettingstarted
   api
   support

.. _author-docs:

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Author Documentation

   writecustom

.. _dev-docs:

.. toctree::
   :hidden:
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

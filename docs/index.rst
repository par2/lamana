
.. LamAna documentation master file, created by
   sphinx-quickstart on Tue Jan 05 14:44:04 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
LamAna Documentation
====================

The LamAna project is an extensible Python library for interactive laminate analysis and visualization.

.. sidebar:: What's New in LamAna

   - Official documentation hosted on readthedocs
   - Docs support Jupyter notebooks (see `nbsphinx <https://nbsphinx.readthedocs.org/en/latest/>`_)
   - Docs support Sphinx extensions: autodocs, autosummary, numpydoc/napolean, viewcode
   
Using the LamAna project, you can **calculate**/**export**/**analyze** data and
**author** custom models based on laminate theory.  Featured components can be used to plot stress distributions, analyze thickessness effects and predict failure trends.

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

The documentation for LamAna is organized into several sections by increasing complexity:

  :ref:`User Documentation<user-docs>` |
  :ref:`Author Documentation<author-docs>` |
  :ref:`Developer Documentation<dev-docs>`

Detailed information on ancillary topics can be found in the :ref:`Appendix<appendix-docs>`.

.. _gallery-docs:

.. toctree::
   :maxdepth: 1
   :caption: Gallery
   :name: gallerydoc
   
   showcase

.. _user-docs:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation
   :name: usertoc
   
   installation
   gettingstarted
   api
   support


.. _author-docs:

.. toctree::
   :maxdepth: 2
   :caption: Author Documentation
   :name: authortoc

   writecustom


.. _dev-docs:

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation
   :name: devtoc
   
   package
   contributions
   testing
   docs
   demo
   lpep


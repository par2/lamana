
.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: {}'.format(st))


.. parsed-literal::

    Last Run: 2016-01-09 23:58:54
    

Writing Custom Models
=====================

A powerful, extensible option of the ``LamAna`` package is user
implementation of their own laminate theory models. A library of these
custom models (as well as the defaults) are kept in the ``models``
directory (sub-package). This is possbile since the ``theories`` module
handshakes between the ``constructs`` module and the selected model from
the ``models`` sub-package. All models related exceptions and global
model code is housed in ``theories`` and merges the model calculations
to generate data variables in the ``LaminateModel`` object.

Authoring Custom Models
-----------------------

Custom models are simple .py files that can be placed by the user into
the models directory. The API allows for calling these selected files in
the ``apply()`` method of the distributions module. In order for these
process to work smoothly, the following essentials are need to talk to
``theories`` module.

1. Implement a ``_use_model_()`` hook that returns (at minimum) an
   updated DataFrame.
2. If using class-style, implement ``_use_model_()`` hook within a class
   named "Model" (must have this name) that inherits from
   ``theories.BaseModel``.

Exceptions for model specific variables or variables defined in
load\_params are maintained by the model's author.

.. code:: python

    '''Fix link below'''




.. parsed-literal::

    'Fix link below'



.. see also:
    
    The latter guidelines are used for authoring custom models on your local machine.  If you would like to share your more, see the `Contributions: As an Author <contribution>_` section for more details.


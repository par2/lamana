
.. code:: python

    # TimeStamp
    import time, datetime
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Run: {}'.format(st))


.. parsed-literal::

    Last Run: 2016-01-13 22:47:18
    

Contributions
=============

First, thank you for your interests in potentially improving LamAna.

At the moment, you can contribute to the LamAna community as an Author
or Developer in several ways.

As an Author
------------

to the Models Library
~~~~~~~~~~~~~~~~~~~~~

You have worked on your custom model and you would like to share it with
others. You can sumbit your custom model as an extension to the current
models library as a pull request on GitHub. As an extension, other users
can access your model with ease. With further review and community
acceptance, the most favorable models will be accepted into the core
LamAna models library. Please do the following:

1. create Python files subclassed from ``theories.Model``
2. write tests
3. document your code
4. cite academic references
5. include supporting validation or FEA data (preferred)

The LamAna Project welcomes open contributions to the offical ``models``
library. It is envisioned that a stable source of reliable laminate
anaylsis models will be useful to other users, similar to the way R
package libraries are maintained.

As a Developer
--------------

to LPEPs
~~~~~~~~

If you are not interested in writing code, but would like to propose an
idea for enchancing LamAna, you can submit an LPEP for review.

1. Please draft your proposals in a similar format to existing LPEPs as
   jupyter notebooks
2. You can submit a pull request on GitHub.

The LPEP `submission <https://www.python.org/dev/peps/pep-0001/#id29>`__
and content
`guidelines <https://www.python.org/dev/peps/pep-0001/#id32>`__ closely
follow PEP 0001.

to Package Code
~~~~~~~~~~~~~~~

If you would like to improve the latest version, please do the
following:

1. ``git clone`` the ``develop`` branch
2. write tests for your enhancement
3. modify the code with appropriate comments
4. successfully run tests
5. write documentation in a jupyter notebook
6. submit your test, code and documentation as a pull requests on
   GitHub.

The latter steps pertain to adding or enchancing Feature modules and
improving core modules. Thanks for your contributions. You are helping
to improve the LamAna community!


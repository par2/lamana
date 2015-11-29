try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='lamana',
    version='0.4.7',                                  ### edit
    description='An extensible Python package for Laminate Analysis.',
    author='P. Robinson II',
    author_email='par2.get@gmail.com',
    url='https://github.com/par2/lamana',             # use the URL to the github repo
    download_url='https://github.com/par2/lamana/tarball/0.4.7',
    packages=['lamana', 'lamana.models', 'lamana.utils', 'lamana.tests',
              'lamana.tests.controls_LT', 'lamana.models.tests'],
    keywords=['laminate analysis', 'visualization'],
    #install_requires=['matplotlib', 'pandas', 'numpy'],
    classifiers=[
        'Framework :: IPython',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
)


# References
# ----- ---------                           -------------
# (001) PyPI Tutorial                       http://peterdowns.com/posts/first-time-with-pypi.html
# (002) Git tagging                         https://git-scm.com/book/en/v2/Git-Basics-Tagging
# (003) Remove remote tag                   https://nathanhoad.net/how-to-delete-a-remote-git-tag
# (004) Create package                      http://zetcode.com/articles/packageinpython/
# (005) Detailed package guide              https://python-packaging-user-guide.readthedocs.org/en/latest/
# (006) Updated guide: twine, pip, wheel    http://joebergantine.com/blog/2015/jul/17/releasing-package-pypi/
# (007) packages                            Python Cookbook, 3rd ed, p. 435
# (008) install_requires                    https://python-packaging-user-guide.readthedocs.org/en/latest/requirements/
# (009) distutils vs. setuptools            http://stackoverflow.com/questions/25337706/setuptools-vs-distutils-why-is-distutils-still-a-thing
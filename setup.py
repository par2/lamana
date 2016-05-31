# -----------------------------------------------------------------------------
# Copyright (c) P. Robinson II.
# Distributed under the terms of the Modified BSD License.
import os
import re
import codecs

# NOTE: Apparently setuptools "ruins the universe"; be cautious with continued use

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


# Utility Code ----------------------------------------------------------------
'''Add to utils'''
here = os.path.abspath(os.path.dirname(__file__))          # REF 024


def read(*parts):
    '''Read the files (REF 024)'''
    # Intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    '''Extract version string (REF 024)'''
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# -----------------------------------------------------------------------------
NAME = 'lamana'
VERSION = find_version(NAME, '__init__.py')
URL = 'https://github.com/par2/lamana'

setup(
    name=NAME,
    version=VERSION,
    description='An extensible Python package for laminate analysis',
    author='P. Robinson II',
    author_email='par2.get@gmail.com',
    url=URL,
    download_url='/'.join([URL, 'tarball', VERSION]),
    ##download_url='https://github.com/par2/lamana/tarball/0.4.9-dev',
    # Search all sub directories; specifics commented below
    packages=find_packages(),
    #packages=['lamana', 'lamana.models', 'lamana.utils', 'lamana.tests',
    #          'lamana.tests.controls_LT', 'lamana.models.tests'],
    # Include everything in source control or MANIFEST.in
    # MANIFEST.in is required to add files to source distributions
    include_package_data=True,
    # Required to add files to wheels
    package_data={
        # Include root level items
        # (Uncertain how this is added to wheels...)
        '': ['LICENSE', 'requirements.txt'],
        # Include test *.py files and *.csv files in 'controls_LT' directory
        'lamana': ['tests/*.py', 'tests/controls_LT/*.csv'],
    },
    # Install latest dependencies; "hands-off" approach
    # Invoke `-r requirements.txt` to install pinned dependencies; "hands-on" approach
    install_requires=[
        'matplotlib',
        'pandas',
        'numpy'
    ],
    keywords=['laminate analysis', 'visualization'],
    license='BSD',
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
# (010) Pinning Dependencies                http://nvie.com/posts/pin-your-packages/
# (011) Improved Package Management         http://nvie.com/posts/better-package-management/
# (012) Modified BSD License                https://opensource.org/licenses/BSD-3-Clause
# (013) On package_data                     https://pythonhosted.org/setuptools/setuptools.html#including-data-files
# (014) find_version code                   https://github.com/pypa/pip/blob/develop/setup.py
# (015) Use pkg_resources to find version   https://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package

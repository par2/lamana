# -----------------------------------------------------------------------------
'''The main init file that stores the package version number.'''
# __version__ is used by find_version() in setup.py

from . import input_
from . import distributions

# Possible import of other modules required

from .models import *

#from . import ratios
#from . import predictions
#from . import gamuts


__title__ = 'lamana'
__version__ = '0.4.13-dev'                                # PEP 440 style
__author__ = 'P. Robinson II'
__license__ = 'BSD'
__copyright__ = 'Copyright 2015, P. Robinson II'

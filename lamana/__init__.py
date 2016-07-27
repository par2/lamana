# -----------------------------------------------------------------------------
'''The main init file that stores the package version number.'''
# __version__ is used by find_version() in setup.py

# import lamana.input_
# import lamana.distributions
# import lamana.constructs
# import lamana.theories
# import lamana.output_

from . import input_
from . import distributions
from . import constructs
from . import theories
from . import output_
#from .utils import *

#from lamana.models import *
#import lamana.ratios
#import lamana.predictions
#import lamana.gamuts


__title__ = 'lamana'
__version__ = '0.4.13-dev'                                # PEP 440 style
__author__ = 'P. Robinson II'
__license__ = 'BSD'
__copyright__ = 'Copyright 2015, P. Robinson II'

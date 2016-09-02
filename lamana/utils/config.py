#------------------------------------------------------------------------------
'''Module for system-wide constants'''

import os

from lamana import __file__ as __root__

# Name for hook function/method; used in `theories.handshake()` with models
HOOKNAME = '_use_model_'

# Default export directory path; used in `utils.get_path()`
# sourcepath = os.path.abspath(os.path.dirname(la.__file__))
SOURCEPATH = os.path.abspath(os.path.dirname(__root__))
PACKAGEPATH = os.path.dirname(SOURCEPATH)
DEFAULTPATH = os.path.join(PACKAGEPATH, 'export')

# Supported export extensions
EXTENSIONS = ('.csv', '.xlsx')

# Random characters
RANDOMCHARS = 'xZ(1-)[]'

# Number of plies obove which iteration is efficient of computing internals.
# An auxillary algorithm is then used.  DEV: See Performance.ipynb for details.
EFFICIENCY_THRESHOLD = 7

# Default layer colors
# colorblind palette from seaborn; grayscale is web-safe
LAMANA_PALETTES = dict(
    #bold=['#FC0D00','#FC7700','#018C99','#00C318','#6A07A9','#009797','#CF0069'],
    bold=['#EB0C00', '#FC7700', '#018C99', '#00C318', '#6A07A9', '#009797', '#CF0069'],
    colorblind=['#0072B2', '#009E73', '#D55E00', '#CC79A7', '#F0E442', '#56B4E9'],
    grayscale=['#FFFFFF', '#999999', '#666666', '#333333', '#000000'],
    HAPSu=['#E7940E', '#F5A9A9', '#FCEB00', '#0B4EA5'],
)

# Store pacage regexes; see reference.py for links
REGEXES = {
    # Last Run: 2016-07-28 09:12:14
    'custom timestamp': '\w+ \w+: \d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}',
    # <matplotlib.figure.Figure at 0x84773c8>
    'addressed output': '<[a-zA-z.]+\b at \b0[xX][0-9a-fA-F]+>',
    # {...}
    'dict/set': '{[\w\W]*}',
    # ....xlsx' or ....csv'
    'last file extensions': ".*.((\bcsv\b)|(\bxlsx\b))'",
    # ....xlsx, ....xlsx or ....csv, ....csv
    'all file extensions': ".*.((\bcsv\b)|(\bxlsx\b))'",
}

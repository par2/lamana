import glob
import logging
from os.path import dirname, basename, isfile

# REF 055
#__all__ = ['Wilson_LT']
modules = glob.glob(dirname(__file__) + '/*.py')
filenames = [basename(f)[:-3] for f in modules if isfile(f)]
__all__ = filenames                                        # Ex. __all__ = ['Wilson_LT']
logging.debug('List of Models files: {}'.format(filenames))

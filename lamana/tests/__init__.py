import numpy as np
from matplotlib.pyplot import close


class PlotTestCase(object):
    '''Adatped from seaborn.'''
    def setUp(self):
        np.random.seed(33)

    def tearDown(self):
        close('all')

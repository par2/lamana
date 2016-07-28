
import matplotlib as mpl
mpl.use('Agg')                                             # required to prevent DISPLAY error; must be before pyplot (REF 050)
import matplotlib.pyplot as plt
import numpy as np


class PlotTestCase(object):
    '''Adatped from seaborn.'''
    def setUp(self):
        np.random.seed(33)

    def tearDown(self):
        plt.close('all')

import numpy as np
import matplotlib.pyplot as plt


class PlotTestCase(object):
    '''Adatped from seaborn.'''
    def setUp(self):
        np.random.seed(33)

    def tearDown(self):
        plt.close('all')

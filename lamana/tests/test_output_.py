#------------------------------------------------------------------------------
'''Confirm output of general models.'''

import logging

import matplotlib.pyplot as plt
import nose.tools as nt

import lamana as la
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt

# Setup -----------------------------------------------------------------------
dft = wlt.Defaults()

load_params = {
    'R': 12e-3,                                            # specimen radius
    'a': 7.5e-3,                                           # support ring radius
    'r': 2e-4,                                             # radial distance from center loading
    'P_a': 1,                                              # applied load
    'p': 2,                                                # points/layer
}

# Quick Form: a dict of lists
mat_props = {
    'HA': [5.2e10, 0.25],
    'PSu': [2.7e9, 0.33],
}


# TESTS -----------------------------------------------------------------------
# These tests are primitive.  They check that plots are made without errors.
# Details of the plotting fidelity must be checked by other means.


def test_plot_nobreak():
    '''Check that basic plotting API works without errors.'''
    # Build dicts of loading parameters and and material properties
    # Select geometries
    single_geo = ['400-200-800']

    case = la.distributions.Case(load_params, mat_props)   # instantiate a User Input Case Object through distributions
    case.apply(single_geo)
    ##actual = case.plot
    ##actual = case.plot()
    # plt.close()                                          # hangs

    # TODO: need to add kw in distrplot to turn off plot window
    # Shut down plt.show()

    #nt.assertTrue(isinstance(actual, mpl.axes))
    pass


# TODO: Cover tests for _multiplot and _cycle_depth


# TODO: Consider sublclassing from PlotTestCase to close plots
class TestPlotDimensions():
    '''Check plots dimensions of rectangle patches correctly.

    Notes
    -----
    - Required creating new axes to prevent plot clobbering
    - Some methods use class level plots; some use internal plots.  Internals that make axes need closing.

    '''
    # Set up cases
    case1 = ut.laminator(['400-200-800'])[0]
    case2 = ut.laminator(dft.geos_standard)
    case3 = ut.laminator(dft.geo_inputs['7-ply'])

    # Sample plots
    plot1 = la.output_._distribplot(case1.LMs, normalized=True)
    fig2, ax2 = plt.subplots()                          # make new, separate axes; prevent inifinite loop of plt.gca()
    plot2 = la.output_._distribplot(case1.LMs, normalized=False, ax=ax2)

    def test_distribplot_normalized_patches_dimensions1(self):
        '''Check position and dimensions of normalized patches, statically.'''

        # Static implies the plot is supplied with fixed, pre-determined values
        for i, rec in enumerate(self.plot1.artists):

            y_i = float(i + 1)                          # fixed y positions
            h_i = 1.0                                   # fixed heights

            # Rectangle Dimensions
            x = rec.get_x()
            y = rec.get_y()
            width = rec.get_width()
            height = rec.get_height()
            logging.debug('x: {}, y: {}, w: {}, h: {}'.format(x, y, width, height))

            # Rectangle Attributes
            #fcolor = rec.get_facecolor()

            # For normalized plots, we expect fixed x positions, widths and heights
            # Only y positions change
            actual = (x, y, width, height)
            expected = (-0.378730662983, y_i, 0.757461325966, h_i)
            logging.debug('y_i: {}, h_i: {}'.format(y_i, h_i))

            nt.assert_almost_equal(actual[0], expected[0])
            nt.assert_almost_equal(actual[1], expected[1])
            nt.assert_almost_equal(actual[2], expected[2])
            nt.assert_almost_equal(actual[3], expected[3])

    # TODO: add randomized cases
    # NOTE: can accept random cases of equivalent plies, e.g.
    # case = ut.laminator(dft.geo_inputs['5-ply'])
    # case = ut.laminator(dft.geo_inputs['4-ply'])
    # case = ut.laminator(dft.geo_inputs['7-ply'])
    def test_distribplot_normalized_patches_dimensions2(self):
        '''Check position and dimensions of normalized patches, dynamically.

        Notes
        -----
        Iterating cases, artists and LaminateModels.  The LMs must have the a same nplies.

        '''
        for case_ in self.case3.values():
            fig, ax = plt.subplots()
            plot = la.output_._distribplot(case_.LMs, normalized=True)

            # Calculations on all LMs in a case
            x_max = max(LM.max_stress.max() for LM in case_.LMs)
            x_min = min(LM.max_stress.min() for LM in case_.LMs)
            w_i = abs(x_max - x_min)

            # Dynamic implies the dimensional values are unknown and thus not fixed
            # Zip the artist and LaminateModel lists together, then iterate both
            # to match the artist with
            for i, rec in enumerate(plot.artists):

                # Rectangle Dimensions
                x = rec.get_x()
                y = rec.get_y()
                width = rec.get_width()
                height = rec.get_height()
                logging.debug('x: {}, y: {}, w: {}, h: {}'.format(x, y, width, height))

                # Rectangle Attributes
                #fcolor = rec.get_facecolor()

                y_i = float(i + 1)
                h_i = 1.0                               # heights equal for normalized; actually k
                logging.debug('x_i: {}, y_i: {}, w_i: {}, h_i: {}'.format(x_min, y_i, w_i, h_i))

                # x postions and widths are fixed; y positions and height change.
                actual = (x, y, width, height)
                expected = (x_min, y_i, w_i, h_i)

                nt.assert_almost_equal(actual[0], expected[0])
                nt.assert_almost_equal(actual[1], expected[1])
                nt.assert_almost_equal(actual[2], expected[2])
                nt.assert_almost_equal(actual[3], expected[3])

            plt.close()

    def test_distribplot_unnormalized_patches_dimensions1(self):
        '''Check position and dimensions of unnormalized patches, statically.'''
        # Static implies the plot is supplied with fixed, pre-determined values
        #case = ut.laminator(['400-200-800'])[0]
        #plot = la.output_._distribplot(LM, normalized=False)

        ys = {
            0: 0.0,
            1: 0.0004,
            2: 0.0006,
            3: 0.0014,
            4: 0.0016,
        }

        hs = {
            0: 0.0004,
            1: 0.0002,
            2: 0.0008,
            3: 0.0002,
            4: 0.0004,
        }

        for i, rec in enumerate(self.plot2.artists):

            # Rectangle Dimensions
            x = rec.get_x()
            y = rec.get_y()
            width = rec.get_width()
            height = rec.get_height()
            logging.debug('x: {}, y: {}, w: {}, h: {}'.format(x, y, width, height))

            # Rectangle Attributes
            #fcolor = rec.get_facecolor()

            # x postions and widths are fixed; y positions and height change.
            actual = (x, y, width, height)
            expected = (-0.378730662983, ys[i], 0.757461325966, hs[i])

            nt.assert_almost_equal(actual[0], expected[0])
            nt.assert_almost_equal(actual[1], expected[1])
            nt.assert_almost_equal(actual[2], expected[2])
            nt.assert_almost_equal(actual[3], expected[3])

    def test_distribplot_unnormalized_patches_dimensions2(self):
        '''Check position and dimensions of unnormalized patches, dynamically.

        Notes
        -----
        Iterating cases, artists and LaminateModels.  Can only handle single geometries.

        '''
        for case_ in self.case2.values():
            fig, ax = plt.subplots()
            plot = la.output_._distribplot(case_.LMs, normalized=False, ax=ax)

            # Calculations on all LMs in a case
            x_max = max(LM.max_stress.max() for LM in case_.LMs)
            x_min = min(LM.max_stress.min() for LM in case_.LMs)
            w_i = abs(x_max - x_min)

            # Dynamic implies the dimensional values are unknown and thus not fixed
            # Zip the artist and LaminateModel lists together, then iterate both
            # to match the artist with
            for i, rec in enumerate(plot.artists):

                # Rectangle Dimensions
                x = rec.get_x()
                y = rec.get_y()
                width = rec.get_width()
                height = rec.get_height()
                logging.debug('x: {}, y: {}, w: {}, h: {}'.format(x, y, width, height))

                # Rectangle Attributes
                #fcolor = rec.get_facecolor()

                # Extract from DataFrames (assume normalized have equal patch dimensions)
                df = case_.LMs[0].LMFrame
                y_i = df[df['label'] == 'interface']['d(m)'].reset_index(drop=True)[i]
                h_i = case_.snapshots[0]['t(um)'][i] / 1e6
                logging.debug('x_i: {}, y_i: {}, w_i: {}, h_i: {}'.format(x_min, y_i, w_i, h_i))

                # x postions and widths are fixed; y positions and height change.
                actual = (x, y, width, height)
                expected = (x_min, y_i, w_i, h_i)

                nt.assert_almost_equal(actual[0], expected[0])
                nt.assert_almost_equal(actual[1], expected[1])
                nt.assert_almost_equal(actual[2], expected[2])
                nt.assert_almost_equal(actual[3], expected[3])

            plt.close()

        # TODO: add line detection tests here

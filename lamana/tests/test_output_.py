#------------------------------------------------------------------------------
'''Confirm output of general models.'''

import logging

import matplotlib as mpl
mpl.use('Agg')                                             # required to prevent DISPLAY error; must be before pyplot (REF 050)
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
    plot1 = la.output_._distribplot(case1.LMs, normalized=True, extrema=True)
    fig2, ax2 = plt.subplots()                          # make new, separate axes; prevent inifinite loop of plt.gca()
    plot2 = la.output_._distribplot(case1.LMs, normalized=False, extrema=True, ax=ax2)

    def test_distribplot_patches_normalized_dimensions1(self):
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
    def test_distribplot_patches_normalized_dimensions2(self):
        '''Check position and dimensions of normalized patches, dynamically.

        Notes
        -----
        Iterating cases, artists and LaminateModels.  The LMs must have the a same nplies.
        Extrema forced True.

        '''
        for case_ in self.case3.values():
            fig, ax = plt.subplots()
            plot = la.output_._distribplot(case_.LMs, normalized=True, extrema=True)

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

    def test_distribplot_unpatches_unnormalized_dimensions1(self):
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

    def test_distribplot_patches_unnormalized_dimensions2(self):
        '''Check position and dimensions of unnormalized patches, dynamically.

        Notes
        -----
        Iterating cases, artists and LaminateModels.  Can only handle single geometries.
        Extrema are forced True.

        '''
        for case_ in self.case2.values():
            fig, ax = plt.subplots()
            plot = la.output_._distribplot(
                case_.LMs, normalized=False, extrema=True, ax=ax
            )

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
                ##h_i = case_.snapshots[0]['t(um)'][i]/1e6
                h_i = case_.LMs[0].stack_order[i + 1][1] / 1e6 # access stack layer thickness
                logging.debug('x_i: {}, y_i: {}, w_i: {}, h_i: {}'.format(x_min, y_i, w_i, h_i))

                # x postions and widths are fixed; y positions and height change.
                actual = (x, y, width, height)
                expected = (x_min, y_i, w_i, h_i)

                nt.assert_almost_equal(actual[0], expected[0])
                nt.assert_almost_equal(actual[1], expected[1])
                nt.assert_almost_equal(actual[2], expected[2])
                nt.assert_almost_equal(actual[3], expected[3])

            plt.close()


# TODO: case randomizer here
# TODO: since similar methods, consider abstracting plot_df_data_extractor into plottools
class TestPlotLines():
    '''Check accuracy of plot lines.'''

    # Various cases
    #case1 = ut.laminator(['400-200-800',], ps=[3,])
    #case2 = ut.laminator(['400-200-800',], ps=[3, 3])
    #case2 = ut.laminator(['400-200-800',], ps=[4, 4])
    case2 = ut.laminator(['400-200-800'], ps=[3, 4])
    case3 = ut.laminator(['400-200-800', '400-400-400', '100-100-100'], ps=[3, 4])

    def test_distribplot_lines_normalized_data1(self):
        '''Check plot data agrees with LaminateModel data; normalized=True.

        Compares lists of zipped (x,y) datapoints.

        Notes
        -----
        - Supports normalize triggering; normalized=True|False
        - Supports non-fixed extrema, i.e p>=2; extrema=False.
        - Supports multiple ps, cases, geo_strings

        '''
        # DEV: change parameters
        normalized = True
        extrema = False
        #case = self.case1
        #case = self.case2
        case = self.case3

        for i, case_ in enumerate(case.values()):
            fig, ax = plt.subplots()
            plot = la.output_._distribplot(case_.LMs, normalized=normalized, extrema=extrema, ax=ax)
            #print(plot)

            # Extract plot data from lines; contain lines per case
            line_cases = []
            for line in plot.lines:
                xs, ys = line.get_data()
                line_cases.append(zip(xs.tolist(), ys.tolist()))
            logging.debug('Case: {}, Plot points per line | xs, ys: {}'.format(i, line_cases))

            # Extract data from LaminateModel; only
            df_cases = []
            for LM in case_.LMs:
                df = LM.LMFrame
                condition = (df['label'] == 'interface') | (df['label'] == 'discont.')
                df_xs = df[condition].ix[:, -1]
                if not extrema: df_xs = df.ix[:, -1]
                if normalized:
                    df_ys = df[condition]['k']
                    if not extrema: df_ys = df['k']
                elif not normalized:
                    df_ys = df[condition]['d(m)']
                    if not extrema: df_ys = df['d(m)']
                df_cases.append(zip(df_xs.tolist(), df_ys.tolist()))
            logging.debug('Case {}, LaminateModel data | df_xs, df_ys: {}'.format(i, df_cases))

        # Compare plot data with LaminateModel data
        #actual = zip(xs.tolist(), ys.tolist())
        actual = line_cases
        expected = df_cases                             # as lists
        nt.assert_equal(actual, expected)

        plt.close()                                     # in jupyter, cuts out last plot

    def test_distribplot_lines_unnormalized_data1(self):
        '''Check plot data agrees with LaminateModel data; normalized=False.

        Compares lists of zipped (x,y) datapoints.

        Notes
        -----
        - Supports normalize triggering; normalized=True|False
        - Supports non-fixed extrema, i.e p>=2; extrema=False.
        - Supports multiple ps, cases; does NOT support mutliple geo_strings

        '''
        # DEV: change parameters
        normalized = False
        extrema = False
        #case = self.case1
        case = self.case2

        for i, case_ in enumerate(case.values()):
            fig, ax = plt.subplots()
            plot = la.output_._distribplot(case_.LMs, normalized=normalized, extrema=extrema, ax=ax)
            #print(plot)

            # Extract plot data from lines; contain lines per case
            line_cases = []
            for line in plot.lines:
                xs, ys = line.get_data()
                line_cases.append(zip(xs.tolist(), ys.tolist()))
            logging.debug('Case: {}, Plot points per line | xs, ys: {}'.format(i, line_cases))

            # Extract data from LaminateModel; only
            df_cases = []
            for LM in case_.LMs:
                df = LM.LMFrame
                condition = (df['label'] == 'interface') | (df['label'] == 'discont.')
                df_xs = df[condition].ix[:, -1]
                if not extrema: df_xs = df.ix[:, -1]
                if normalized:
                    df_ys = df[condition]['k']
                    if not extrema: df_ys = df['k']
                elif not normalized:
                    df_ys = df[condition]['d(m)']
                    if not extrema: df_ys = df['d(m)']
                df_cases.append(zip(df_xs.tolist(), df_ys.tolist()))
            logging.debug('Case {}, LaminateModel data | df_xs, df_ys: {}'.format(i, df_cases))

        # Compare plot data with LaminateModel data
        #actual = zip(xs.tolist(), ys.tolist())
        actual = line_cases
        expected = df_cases                             # as lists
        nt.assert_equal(actual, expected)

        plt.close()                                     # in jupyter, cuts out last plot

#------------------------------------------------------------------------------
'''Confirm output of general models.'''

import logging
import itertools as it

import matplotlib as mpl
mpl.use('Agg')                                             # required to prevent DISPLAY error; must be before pyplot (REF 050)
import matplotlib.pyplot as plt
import nose.tools as nt

from lamana import distributions
from lamana import output_
from lamana.utils import tools as ut
from lamana.lt_exceptions import PlottingError
from lamana.utils import plottools as upt
from lamana.models import Wilson_LT as wlt


dft = wlt.Defaults()


# TESTS -----------------------------------------------------------------------
# TODO:  _cycle_depth
def test_cycler_depth1():
    '''Check cycler repeats for a given depth.

    Notes
    -----
    Testing an infinite generator is not straight-forward.  It must be consumed.
    We will use itertools.islice() to consume up to an arbitrary index, e.g. 10.

    '''
    # Depth:  1    2    3    4    5    6
    iter_ = ['A', 'B', 'C', 'D', 'E', 'F']
    cycler1 = output_._cycle_depth(iter_, depth=None)
    cycler2 = output_._cycle_depth(iter_, depth=2)
    cycler3 = output_._cycle_depth(iter_, depth=3)

    # Consume the infinite generator with islice.
    actual1 = list(it.islice(cycler1, 10))
    actual2 = list(it.islice(cycler2, 10))
    actual3 = list(it.islice(cycler3, 10))

    expected1 = ['A', 'B', 'C', 'D', 'E', 'F', 'A', 'B', 'C', 'D']
    expected2 = ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
    expected3 = ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A']

    nt.assert_almost_equals(actual1, expected1)
    nt.assert_almost_equals(actual2, expected2)
    nt.assert_almost_equals(actual3, expected3)


# Single Plots ----------------------------------------------------------------
# TODO: need to add kw in distribplot to turn off plot window; shut down plt.show()
@nt.raises(PlottingError)
def test_distribplot_unnormalized_error1():
    '''Check raises PlottingError if geometry > 1 for unnormalized plot.'''
    case = distributions.laminator(['400-200-800', '400-400-400'])[0]
    plot = output_._distribplot(case.LMs, normalized=False)

    plt.close()


# TODO: release after moking mock model with no stress columns; needed for LM
#@nt.raises(InputError)
#def test_distribplot_input_error1():
#    '''Check raises InputError if x override does not have 'stress' in the name.'''
#    x_col = 'sterss'
#    case = distributions.laminator(['400-200-800', '400-400-400'])[0]
#    plot = output_._distribplot(case.LMs, x=x_col)
#
#    plt.close()


def test_distribplot_input_error2():
    '''Check still looks for stress column, even if bad x column name given.'''
    x_col = 'bad_column_name'
    case = distributions.laminator(['400-200-800'])[0]
    plot = output_._distribplot(case.LMs, x=x_col)
    nt.assert_is_instance(plot, mpl.axes.Axes)

    plt.close()


def test_distribplot_instance1():
    '''Check distribplot returns an axes.'''
    case = distributions.laminator(['400-200-800'])[0]
    plot = output_._distribplot(case.LMs, normalized=True, extrema=True)

    nt.assert_is_instance(plot, mpl.axes.Axes)

    plt.close()


def test_distribplot_annotate1():
    '''Check iif text exists on the plot when annotate=True.'''
    case = distributions.laminator(['400-200-800'])[0]
    plot = output_._distribplot(case.LMs, annotate=True)

    actual = upt.has_annotations(plot.texts)
    nt.assert_true(actual)

    plt.close()


def test_distribplot_annotate2():
    '''Check ift text exists; return False when annotate=False'''
    case = distributions.laminator(['400-200-800'])[0]
    plot = output_._distribplot(case.LMs, annotate=False)

    actual = upt.has_annotations(plot.texts)
    nt.assert_false(actual)

    plt.close()


# TODO: Consider sublclassing from PlotTestCase to close plots
class TestDistribplotDimensions():
    '''Check plots dimensions of rectangle patches correctly.

    `_distribplot` is the source of distribution plots; backbone to `distributions`.

    Notes
    -----
    - Required creating new axes to prevent plot clobbering
    - Some methods use class level plots; some use internal plots.
      Internals that make axes need closing.

    '''
    # Set up cases
    case1 = distributions.laminator(['400-200-800'])[0]
    case2 = distributions.laminator(dft.geos_standard)
    case3 = distributions.laminator(dft.geo_inputs['7-ply'])

    # Sample plots
    plot1 = output_._distribplot(case1.LMs, normalized=True, extrema=True)
    fig2, ax2 = plt.subplots()                             # make new, separate axes; prevent inifinite loop of plt.gca()
    plot2 = output_._distribplot(case1.LMs, normalized=False, extrema=True, ax=ax2)

    # TODO: randomize cases for this test
    def test_distribplot_patches_count1(self):
        '''Check number of rectangle patches equals number of plies.'''
        case = self.case1
        LM = case.LMs[0]

        npatches = len(self.plot1.artists)
        nplies = LM.nplies

        actual = npatches
        expected = nplies

        nt.assert_equal(actual, expected)

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
    # case = distributions.laminator(dft.geo_inputs['5-ply'])
    # case = distributions.laminator(dft.geo_inputs['4-ply'])
    # case = distributions.laminator(dft.geo_inputs['7-ply'])
    def test_distribplot_patches_normalized_dimensions2(self):
        '''Check position and dimensions of normalized patches, dynamically.

        Notes
        -----
        Iterating cases, artists and LaminateModels.  The LMs must have the a same nplies.
        Extrema forced True.

        '''
        for case_ in self.case3.values():
            fig, ax = plt.subplots()
            plot = output_._distribplot(case_.LMs, normalized=True, extrema=True)

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

    def test_distribplot_patches_unnormalized_dimensions1(self):
        '''Check position and dimensions of unnormalized patches, statically.'''
        # Static implies the plot is supplied with fixed, pre-determined values
        #case = distributions.laminator(['400-200-800'])[0]
        #plot = output_._distribplot(LM, normalized=False)

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
            plot = output_._distribplot(
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
class TestDistribplotLines():
    '''Check accuracy of plot lines.'''

    # Various cases
    #case1 = distributions.laminator(['400-200-800',], ps=[3,])
    #cases2 = distributions.laminator(['400-200-800',], ps=[3, 3])
    #cases2 = distributions.laminator(['400-200-800',], ps=[4, 4])
    cases2 = distributions.laminator(['400-200-800'], ps=[3, 4])
    cases3 = distributions.laminator(['400-200-800', '400-400-400', '100-100-100'], ps=[3, 4])

    def test_distribplot_lines_count1(self):
        '''Check number of lines equals number of case size (# geo_strings).'''
        cases = self.cases3

        for case_ in cases.values():
            fig, ax = plt.subplots()
            plot = output_._distribplot(case_.LMs, ax=ax)

            nlines = len(plot.lines)
            ngeo_strings = len(case_.LMs)
            ncases = case_.size

            actual1 = nlines
            expected1 = ngeo_strings
            expected2 = ncases

            nt.assert_equal(actual1, expected1)
            nt.assert_equal(actual1, expected2)

            plt.close()

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
        #cases_ = self.case1
        #cases_ = self.cases2
        cases_ = self.cases3

        # Compare plot data with LaminateModel data
        line_df_case = upt.extract_plot_LM_xy(cases_, normalized=True, extrema=False)
        line_data, df_data = line_df_case

        actual = line_data
        expected = df_data
        nt.assert_equal(actual, expected)

        plt.close()                                     # in jupyter, cuts out last plot

    def test_distribplot_lines_unnormalized_data1(self):
        '''Check plot data agrees with LaminateModel data; normalized=False.

        Compares lists of (x, y) datapoints.

        Notes
        -----
        - Supports normalize triggering; normalized=True|False
        - Supports non-fixed extrema, i.e p>=2; extrema=False.
        - Supports multiple ps, cases; does NOT support mutliple geo_strings

        '''
        #cases_ = self.case1
        cases_ = self.cases2

        # Compare plot data with LaminateModel data
        line_df_case = upt.extract_plot_LM_xy(cases_, normalized=False, extrema=False)
        line_data, df_data = line_df_case

        actual = line_data
        expected = df_data
        nt.assert_equal(actual, expected)

        plt.close()                                     # in jupyter, cuts out last plot


# Multiple Plots --------------------------------------------------------------
# DEV: a series of bugs were discovered during testing; refactoring is required.
# TODO: Look into close plots by encasing following functions with a class
def test_multiplot_plot_instance1():
    '''Check distribplot returns a figure.'''
    str_caselets = ['350-400-500', '400-200-800']
    cases = distributions.Cases(str_caselets, ps=[2, 3])
    plot = output_._multiplot(cases)
    nt.assert_is_instance(plot, mpl.figure.Figure)

    plt.close()


def test_multiplot_axes_count1():
    '''Check total axes equals number of cases.'''
    str_caselets = ['400-200-800', '400-400-400']
    ps = [2, 3, 4, 5]

    cases = distributions.Cases(str_caselets, ps=ps)
    plot = output_._multiplot(cases)

    naxes = len(plot.axes)
    ncases1 = len(str_caselets) * len(ps)
    ncases2 = len(cases)

    actual = naxes
    expected1 = ncases1
    expected2 = ncases2

    nt.assert_equal(actual, expected1)
    nt.assert_equal(actual, expected2)

    plt.close()


# TODO: release after fix; need to plot beyond default rows
# def test_multiplot_axes_count2():
#     '''Check total axes in figure for random number of ps equals number of cases.'''
#     random_choice = random.randint(2,10)
#     population = range(2, 12)
#     # Generate list of random integers, e.g [2, 5, 4, 7] or [5, 3]
#     random_ps = random.sample(population, random_choice)
#     assert len(random_ps) < population

#     cases = distributions.Cases(['400-200-800', '400-400-400'], ps=random_ps)
#     plot = output_._multiplot(cases)

#     naxes = len(plot.axes)
#     ncases = len(cases)
#     actual = naxes
#     expected = ncases

#     logging.debug('# axes: {}, # cases: {}, # ps: {} --> ps: {}'.format(
#             naxes, ncases, random_choice, random_ps)
#     )
#     nt.assert_equal(actual, expected)

#     plt.close()


# TODO: Test multiplot caselet types

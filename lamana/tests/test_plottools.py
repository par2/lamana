#------------------------------------------------------------------------------
import nose.tools as nt

from lamana.lt_exceptions import InputError
from lamana.utils import tools as ut
from lamana.utils import plottools as upt


# Analyze Geometries ----------------------------------------------------------
@nt.raises(InputError)
def test_get_duples_error1():
    '''Check raise error if full geometry given.'''
    upt._get_duples('(400,100)-[100,(200.0,200),300]-800')


@nt.raises(InputError)
def test_get_nonduples_error1():
    '''Check raise error if full geometry given.'''
    upt._get_non_duples('(400,100)-[100,(200.0,200),300]-800')


def test_get_duples1():
    '''Check returns list of duples given outer or inner tokens.'''
    outer = '(300.0,100.0)'                                # token
    inner_i1 = '[100.0, (200.0, 200.0), 300.0]'
    inner_i2 = '[100.0, (200.0, 200.0), 300.0, (100,300.0)]'
    inner_i3 = '[100.0, (200.0, 200.0), 300, (100.0,300),(100,300.0)]'
    invalid = '800.0'                                    # invalid arg
    actual1 = upt._get_duples(outer)
    actual2 = upt._get_duples(inner_i1)
    actual3 = upt._get_duples(inner_i2)
    actual4 = upt._get_duples(inner_i3)
    actual5 = upt._get_duples(invalid)
    expected1 = [(0, (300.0, 100.0))]
    expected2 = [(8, (200.0, 200.0))]
    expected3 = [(8, (200.0, 200.0)), (31, (100.0, 300.0))]
    expected4 = [(8, (200.0, 200.0)), (29, (100.0, 300.0)), (41, (100.0, 300.0))]
    expected5 = []

    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)
    nt.assert_equal(actual4, expected4)
    nt.assert_equal(actual5, expected5)


def test_get_non_duples1():
    '''Check returns list of non-duples given outer or inner tokens.'''
    outer = '300.0'                                        # token
    inner_i1 = '[100.0, (200.0, 200.0), 300.0]'
    inner_i2 = '[100.0, (200.0, 200.0), 300.0, (100,300.0)]'
    inner_i3 = '[100.0, (200.0, 200.0), 300, (100.0,300),(100,300.0)]'
    invalid = '(300.0, 100.0)'                             # invalid arg
    actual1 = upt._get_non_duples(outer)
    actual2 = upt._get_non_duples(inner_i1)
    actual3 = upt._get_non_duples(inner_i2)
    actual4 = upt._get_non_duples(inner_i3)
    actual5 = upt._get_non_duples(invalid)
    expected1 = [(0, 300.0)]
    expected2 = [(1, 100.0), (24, 300.0)]
    expected3 = [(1, 100.0,), (24, 300.0)]
    expected3 = [(1, 100.0,), (24, 300.0)]
    expected4 = [(1, 100.0,), (24, 300.0)]
    expected5 = []

    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)
    nt.assert_equal(actual4, expected4)
    nt.assert_equal(actual5, expected5)


def test_get_outer1():
    '''Check get a float or tuples.'''
    actual1 = upt._get_outer('400')
    actual2 = upt._get_outer('400.0')
    actual3 = upt._get_outer('(300,100)')
    expected1 = 400.0
    expected2 = 400.0
    expected3 = (300.0, 100.0)
    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)


def test_get_inner_i1():
    '''Check a list of inner_i components is returned.'''
    inner_i1 = '[100,(200.0,200),300]'
    expected = [100.0, (200.0, 200.0), 300.0]
    actual = upt._get_inner_i(inner_i1)
    nt.assert_equal(actual, expected)


def test_get_middle1():
    '''Check get a float regardless of symmetric 'S'.'''
    actual1 = upt._get_middle('800')
    actual2 = upt._get_middle('800.0')
    actual3 = upt._get_middle('400S')
    expected = 800.0

    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)
    nt.assert_equal(actual3, expected)


def test_unfold_geometry1():
    '''Check returns list of ordered stack sequence.'''
    expected = [400.0, 100.0, 200.0, 300.0, 800.0, 300.0, 200.0, 100.0, 400.0]
    outer = 400.0
    inner_i = [100.0, (200.0, 200.0), 300.0]
    middle = 800.0
    actual = upt._unfold_geometry(outer, inner_i, middle)
    nt.assert_equal(actual, expected)


def test_unfold_geometry2():
    '''Check returns list of ordered stack sequence; using outer duples.'''
    expected = [300.0, 100.0, 200.0, 300.0, 800.0, 300.0, 200.0, 100.0, 100.0]
    outer = (300.0, 100.0)
    inner_i = [100.0, (200.0, 200.0), 300.0]
    middle = 800.0
    actual = upt._unfold_geometry(outer, inner_i, middle)
    nt.assert_equal(actual, expected)


def test_analyze_geostring1():
    '''Check nplies, thickness and order given a geo_string.'''
    geostrings = {
        # Unconventional
        '400-200-800': (
            5, 2.0, [400.0, 200.0, 800.0, 200.0, 400.0]
        ),
        # Gen. Conventional
        '400-[200]-800': (
            5, 2.0, [400.0, 200.0, 800.0, 200.0, 400.0]
        ),
        # n inner_i
        '400-[100,100]-800': (
            7, 2.0, [400.0, 100.0, 100.0, 800.0, 100.0, 100.0, 400.0]
        ),
        # n inner_i
        '400-[100,75,25]-800': (
            9, 2.0, [400.0, 100.0, 75.0, 25.0, 800.0, 25.0, 75.0, 100.0, 400.0]
        ),
        # Symmetric
        '400-[200]-400S': (
            5, 2.0, [400.0, 200.0, 800.0, 200.0, 400.0]
        ),
        # TODO: Release post refactor of _to_gen_convention.
        # Duple
        #'(300,100)-[100,(50,150)]-800': (7, 1.6,
        #    [300.0, 100.0, 50.0, 800.0, 150.0, 100.0, 100.0]),
    }

    for g, e in geostrings.items():
        actual = upt.analyze_geostring(g)
        expected = e
        nt.assert_equal(actual, expected)


# Extract xy Data -------------------------------------------------------------
def test_extract_equivalence1():
    '''Given a case, line plot data agrees with the DataFrame data.'''

    case = ut.laminator(['400-[200]-800', '400-[400]-400'])
    line_df_case = upt.extract_plot_LM_xy(case)
    line_data, df_data = line_df_case

    actual = line_data
    expected = df_data
    nt.assert_equal(actual, expected)


def test_extract_equivalence2():
    '''Given a case, line plot data agrees with the DataFrame data; extrema=True.'''

    case = ut.laminator(['400-[200]-800', '400-[400]-400'])
    line_df_case = upt.extract_plot_LM_xy(case, extrema=True)
    line_data, df_data = line_df_case

    actual = line_data
    expected = df_data
    nt.assert_equal(actual, expected)


def test_extract_equivalence3():
    '''Given a case, line plot data agrees with the DataFrame data; normalized=False.'''

    case = ut.laminator(['400-[200]-800'])                 # unnormalized multiplot requires only one geoemetry
    line_df_case = upt.extract_plot_LM_xy(case, normalized=False)
    line_data, df_data = line_df_case

    actual = line_data
    expected = df_data
    nt.assert_equal(actual, expected)


def test_extract_equivalence4():
    '''Given a case, line plot data agrees with the DataFrame data; {extrema,normalized}=False.'''

    case = ut.laminator(['400-[200]-800'])                 # unnormalized multiplot requires only one geoemetry
    line_df_case = upt.extract_plot_LM_xy(case, extrema=False, normalized=False)
    line_data, df_data = line_df_case

    actual = line_data
    expected = df_data
    nt.assert_equal(actual, expected)

# TODO: Add tests for colors

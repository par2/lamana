#------------------------------------------------------------------------------
'''Test for consistency of utils.'''

import nose.tools as nt
import pandas as pd

import lamana as la
##from lamana.input_ import BaseDefaults
#from lamana.utils.tools import BaseDefaults
from lamana.models import Wilson_LT as wlt
from lamana.utils import tools as ut

##bdft = BaseDefaults()                                      # from base class
dft = wlt.Defaults()                                       # from inherited class in models; user


# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {
    'R': 12e-3,                                            # specimen radius
    'a': 7.5e-3,                                           # support ring radius
    'p': 5,                                                # points/layer
    'P_a': 1,                                              # applied load
    'r': 2e-4,                                             # radial distance from center loading
}

mat_props = {
    'HA': [5.2e10, 0.25],
    'PSu': [2.7e9, 0.33],
}

# TESTS -----------------------------------------------------------------------

# =============================================================================
# TOOLS -----------------------------------------------------------------------
# =============================================================================


# Laminator -------------------------------------------------------------------
def test_laminator_consistency1():
    '''Check laminator yields same LMFrame as classic case building.'''
    case = ut.laminator(geos=dft.geos_all, ps=[5])
    for case_ in case.values():
        case1 = case_
    case2 = la.distributions.Case(load_params, mat_props)
    case2.apply(dft.geos_all)
    #print(case1)
    #print(case2)
    ##for actual, expected in zip(case1, case2.LMs):
    for actual, expected in zip(case1.LMs, case2.LMs):
        #print(actual)
        #print(expected)
        ut.assertFrameEqual(actual.LMFrame, expected.LMFrame)


# Sort DataFrame Columns ------------------------------------------------------
def test_set_columns_seq1():
    '''Check reorders columns to existing sequence.'''
    # Pandas orders DataFrame columns alphabetically
    data = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    df = pd.DataFrame(data, index=['amount'])
    # apple  banana  blueberry  orange

    # We can resequence the columns
    seq = ['apple', 'orange', 'banana', 'blueberry']
    actual = ut.set_column_sequence(df, seq)
    expected = pd.DataFrame(data, index=['amount'], columns=seq)
    ut.assertFrameEqual(actual, expected)


def test_set_columns_seq2():
    '''Check reorders columns and adds columns not in sequence to the end.'''
    data = {'apple': 4, 'strawberry': 3, 'orange': 3, 'banana': 2}
    df = pd.DataFrame(data, index=['amount'])

    # Excluded names are appended to the end of the DataFrame
    seq = ['apple', 'strawberry']
    # apple  strawberry banana  orange
    actual = ut.set_column_sequence(df, seq)
    expected = pd.DataFrame(data, index=['amount'],
                            columns=['apple', 'strawberry', 'banana', 'orange'])
    ut.assertFrameEqual(actual, expected)


# Natural Sort ----------------------------------------------------------------
def test_natural_sort1():
    '''Check natural sorting of keys in a dict; keys are passed in from the dict.'''
    dict_ = {'3-ply': None, '1-ply': None, '10-ply': None, '2-ply': None}
    # actual = [k for k, v in sorted(dict_(), key=natural_sort)]    # equivalent
    actual = [k for k in sorted(dict_.keys(), key=ut.natural_sort)]
    expected = ['1-ply', '2-ply', '3-ply', '10-ply']
    nt.assert_equal(actual, expected)


def test_natural_sort2():
    '''Check natural sorting of keys from tuples; key-value pairs are passed in from the dict.'''
    dict_ = {'3-ply': None, '1-ply': None, '10-ply': None, '2-ply': None}
    actual = [k for k in sorted(dict_.items(), key=ut.natural_sort)]
    expected = [('1-ply', None), ('2-ply', None), ('3-ply', None), ('10-ply', None)]
    nt.assert_equal(actual, expected)


def test_natural_sort3():
    '''Check if non-digits are in keys.'''
    dict_ = {'3-ply': None, 'foo-ply': None, '10-ply': None, '2-ply': None}
    # actual = [k for k, v in sorted(dict_(), key=natural_sort)]    # equivalent
    actual = [k for k in sorted(dict_.keys(), key=ut.natural_sort)]
    expected = ['2-ply', '3-ply', '10-ply', 'foo-ply']
    nt.assert_equal(actual, expected)

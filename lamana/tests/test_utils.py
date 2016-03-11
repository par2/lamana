#------------------------------------------------------------------------------
'''Test for consistency of utils.'''

import nose.tools as nt
import pandas as pd

import lamana as la
from lamana.models import Wilson_LT as wlt
from lamana.utils import tools as ut

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


#def test_laminator_gencon1():
#    '''Check returns a geometry string in General Convention; converts 'S'.'''
#    case = ut.laminator(['400-0-400S'])
#    for case_ in case.values():
#        for LM in case_.LMs:
#            actual = ut.get_special_geometry(LM.LMFrame)
#            expected = '400.0-[0.0]-800.0'
#            nt.assert_equal(actual, expected)


# Get Specials ----------------------------------------------------------------
def test_getspecialgeo1():
    '''Check strings are extracted from a special laminate Frame, nplies <= 4.'''
    case = ut.laminator(['400-200-0'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)
            expected = '400-[200]-0'
            nt.assert_equal(actual, expected)


@nt.raises(Exception)
def test_getspecialgeo2():
    '''Check error is raised if not special, nplies > 4.'''
    case = ut.laminator(['400-200-800'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)


# Sets ------------------------------------------------------------------------
def test_compare_subset():
    '''Check the comparison of subsets.'''
    # Subset: [1,2] < [1,2,3] -> True; [1,2] <= [1,2] -> True
    it = [[1, 2], [1, 2], [1, 2]]
    others = [[1, 2, 3], [1, 2], [3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union', test='issubset')
        actual.append(result)
    expected = [True, True, False]
    nt.assert_equal(actual, expected)


def test_compare_superset():
    '''Check the comparison of supersets.'''
    # Superset: [1,2,3] > [1,2] -> True; [1,2,3] >= [1,2,3] -> True
    it = [[1, 2, 3], [1, 2, 3], [1, 2]]
    others = [[1, 2], [1, 2, 3], [3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union', test='issuperset')
        actual.append(result)
    expected = [True, True, False]
    nt.assert_equal(actual, expected)


def test_compare_disjoint():
    '''Check the comparison of dijoints.'''
    # Superset: [1,2,3] > [1,2] -> True; [1,2,3] >= [1,2,3] -> True
    it = [[1, 2]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union', test='isdisjoint')
        actual.append(result)
    expected = [True]
    nt.assert_equal(actual, expected)


def test_compare_union():
    '''Check set union.'''
    # Union: [1,2] | [3,4] -> {1,2,3,4}
    it = [[1, 2]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union')
        actual.append(result)
    expected = [{1, 2, 3, 4}]
    nt.assert_equal(actual, expected)


def test_compare_intersection():
    '''Check set intersection.'''
    # Intersection: [1] & [1,2] -> {1}
    it = [[1]]
    others = [[1, 2]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='intersection')
        actual.append(result)
    expected = [{1}]
    nt.assert_equal(actual, expected)


def test_compare_difference():
    '''Check set difference.'''
    # Difference: [1,2,3] - [3,4] -> {1,2}
    it = [[1, 2, 3]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='difference')
        actual.append(result)
    expected = [{1, 2}]
    nt.assert_equal(actual, expected)


def test_compare_symmetric():
    '''Check set symmetric difference.'''
    # Symmetric Difference: [1,2,3] ^ [3,4] -> {1,2,4}
    it = [[1, 2, 3]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='symmetric difference')
        actual.append(result)
    expected = [{1, 2, 4}]
    nt.assert_equal(actual, expected)


def test_compare_iterables():
    '''Check set comparision works if given non-iterables e.g. int.'''
    # Symmetric Difference: [1,2,3] ^ [3,4] -> {1,2,4}
    actual1 = ut.compare_set(1, [2, 3], how='union')       # it is int
    actual2 = ut.compare_set([1, 2], 3, how='union')       # other is int
    expected = {1, 2, 3}
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


# Matching Brackets -----------------------------------------------------------
def test_ismatched1():
    '''Check matching pair of brackets or parentheses returns True.'''
    s1 = 'Here the [brackets] are matched.'
    s2 = 'Here the (parentheses) are matched.'
    actual1 = ut.is_matched(s1)
    actual2 = ut.is_matched(s2)
    expected = True
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


def test_ismatched2():
    '''Check non-matching pair of brackets brackets or parentheses returns False.'''
    s1 = 'Here the [brackets][ are NOT matched.'
    s2 = 'Here the ((parentheses) are NOT matched.'
    actual1 = ut.is_matched(s1)
    actual2 = ut.is_matched(s2)
    expected = False
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


def test_ismatched3():
    '''Check non-matching pair of brackets brackets or parentheses returns False.'''
    s1 = 'Only accept [letters] in brackets that are [CAPITALIZED[.'
    s2 = 'Only accept (letters) in parentheses that are ((CAPITALIZED(.'
    p = '\W[A-Z]+\W'                                       # regex for all only capital letters and non-alphannumerics
    actual1 = ut.is_matched(s1, p)
    actual2 = ut.is_matched(s2, p)
    expected = False
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


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

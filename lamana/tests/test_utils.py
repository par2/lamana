#------------------------------------------------------------------------------
'''Test for consistency of utils.'''
# CAUTION: This module writes and removes temporary files in the "export" dir


import os
import collections as ct

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


@nt.raises(Exception)
def test_lamainator_type1():
    '''Check raises Exception if geos is not a list.'''
    actual = ut.laminator(geos={'400-200-800'})


def test_laminator_type2():
    '''Check defaults to 400-200-800 nothing is passed in.'''
    case1 = ut.laminator(geos=['400-200-800'])
    LM = case1[0]
    actual = LM.frames[0]
    case2 = la.distributions.Case(dft.load_params, dft.mat_props)
    case2.apply(['400-200-800'])
    expected = case2.frames[0]
    ut.assertFrameEqual(actual, expected)


def test_laminator_type3():
    '''Check defaults triggerd if nothing is passed in.'''
    case1 = ut.laminator()
    LM = case1[0]
    actual = LM.frames[0]
    case2 = la.distributions.Case(dft.load_params, dft.mat_props)
    case2.apply(['400-200-800'])
    expected = case2.frames[0]
    ut.assertFrameEqual(actual, expected)


def test_laminator_gencon1():
    '''Check returns a geometry string in General Convention; converts 'S'.'''
    case = ut.laminator(['400-0-400S'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)
            ##expected = '400-[0]-800'                       # pre to_gen_convention()
            expected = '400.0-[0.0]-800.0'
            nt.assert_equal(actual, expected)


# Write CSV -------------------------------------------------------------------
def test_tools_write1():
    '''Check DataFrame is written of csv and read DataFrame is the same.

    Notes
    -----
    Builds case(s), pulls the DataFrame, write a temporary csv in the default
    "export" directory (overwrites if the temporary file exists to keep clean).
    Then use pandas to read the csv back as a DataFrame.  Finally compare
    equality between DataFrames, then removes the file.

    DEV: File is removed even if fails to keep the export dir clean.  Comment
    if debugging required.

    See also
    --------
    - test_write2(): overwrite=False; may give unexpected results in tandem

    '''
    try:
        case = ut.laminator(['400-200-800'])
        # Write files to default output dir
        for case_ in case.values():
            for LM in case_.LMs:
                expected = LM.LMFrame
                filepath = ut.write_csv(LM, overwrite=True, prefix='temp')

                # Read a file
                actual = pd.read_csv(filepath, index_col=0)
                ut.assertFrameEqual(actual, expected)
    finally:
        # Remove temporary file
        os.remove(filepath)
        #pass


def test_tools_write2():
    '''Check if overwrite=False retains files.

    Notes
    -----
    Make two files of the same name.  Force write_csv to increment files.
    Check the filepath names exist.  Finally remove all files.

    DEV: Files are removed even if fails to keep the export dir clean.  Comment
    if debugging required.

    '''
    try:
        case = ut.laminator(['400-200-800', '400-200-800'])
        # Write files to default output dir
        filepaths = []
        for case_ in case.values():
            for LM in case_.LMs:
                #filepath = ut.write_csv(LM, overwrite=False, verbose=True, prefix='temp')
                filepath = ut.write_csv(LM, overwrite=False, prefix='temp')
                filepaths.append(filepath)

        for file_ in filepaths:
            actual = os.path.isfile(file_)
            nt.assert_true(actual)

    finally:
        # Remove temporary file
        for file_ in filepaths:
            os.remove(file_)


# Read CSV --------------------------------------------------------------------
# TODO: add modified write file
def test_read1():
    try:
        case = ut.laminator(['400-200-800', '400-[100,100]-800'])

        # Expected: Write LaminateModels
        # Make files in a default export dir, and catch expected dfs
        list_l = []
        for case_ in case.values():
            for LM in case_.LMs:
                df_l = LM.LMFrame
                filepath_l = ut.write_csv(LM, overwrite=False, prefix='temp')
                list_l.append((df_l, filepath_l))

        # Actual: Read Files
        # Get dirpath from last filepath_l; assumes default path structure from write_csv
        dirpath = os.path.dirname(filepath_l)
        gen_r = ut.read_csv_dir(dirpath)                   # yields (file, filepath)

        # Use a defaultdict to place same dfs with matching paths
        # {'...\filename': [df_l, df_r]}
        d = ct.defaultdict(list)
        for df_l, filepath_l in list_l:
            d[filepath_l].append(df_l)

        for df_r, filepath_r in gen_r:
            d[filepath_r].append(df_r)

        # If files are already present in export dir, the # write files < # read files
        # Need to filter the dict entries that don't have both read and write (left-right) values
        # Only need to iterate over keys for the written files i.e. filepath_l
        written_filepaths = [path for df, path in list_l]

        # Verify Equivalence
        # Compare DataFrames sharing the same pathname (ensure correct file for left and right)
        for k, v in d.items():
            filename = k
            if filename in written_filepaths:
                expected, actual = v
                #print(filename)
                #print(expected.info)
                ut.assertFrameEqual(actual, expected)

    # Cleanup
    # Only remove the written temporary files
    finally:
        for file_ in d:
            if file_ in written_filepaths:
                print('Cleaning up temporary files ...')
                os.remove(file_)


# Extract geo_strings ---------------------------------------------------------
def test_getmultigeo1():
    '''Check strings are extracted from a "multi" laminate Frame, nplies >= 5.'''
    case = ut.laminator(['400-200-800'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_multi_geometry(LM.LMFrame)
            #expected = '400-[200]-800'                       # pre to_gen_convention()
            expected = '400.0-[200.0]-800.0'
            nt.assert_equal(actual, expected)


@nt.raises(Exception)
def test_getmultigeo2():
    '''Check error is raised if not "multi", rather a special, nplies < 4.'''
    case = ut.laminator(['400-200-0'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_multi_geometry(LM.LMFrame)


def test_getspecialgeo1():
    '''Check strings are extracted from a special laminate Frame, nplies <= 4.'''
    case = ut.laminator(['400-200-0'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)
            ##expected = '400-[200]-0'                       # pre to_gen_convention()
            expected = '400.0-[200.0]-0.0'
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


# Pandas Object Comparisons ---------------------------------------------------
class TestPandasComparisions():
    '''Check basic assertions for helper functions comparings Series and DataFrames.'''
    # Build DataFrames
    df_data1 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    df_data2 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    df_data3 = {'apple': 4, 'strawberry': 3, 'orange': 3, 'banana': 2}

    df1 = pd.DataFrame(df_data1, index=['amount'])
    df2 = pd.DataFrame(df_data2, index=['amount'])
    df3 = pd.DataFrame(df_data3, index=['amount'])

    # Build Series
    s_data1 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    s_data2 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    s_data3 = {'apple': 4, 'strawberry': 3, 'orange': 3, 'banana': 2}

    s1 = pd.Series(s_data1)
    s2 = pd.Series(s_data2)
    s3 = pd.Series(s_data3)

    # Test assertFrameEqual
    def test_assertframeeq1(self):
        '''Check helper function compares DataFrames, None.'''
        # See https://github.com/pydata/pandas/blob/master/pandas/util/testing.py
        actual = ut.assertFrameEqual(self.df1, self.df2)
        expected = None
        nt.assert_equal(actual, expected)

    @nt.raises(AssertionError)
    def test_assertframeeq2(self):
        '''Check helper function compares DataFrames, raises error is not equal.'''
        actual = ut.assertFrameEqual(self.df1, self.df3)

    # Test assertSeriesEqual
    def test_assertserieseq1(self):
        '''Check helper function compares Series, None.'''
        # See https://github.com/pydata/pandas/blob/master/pandas/util/testing.py
        actual = ut.assertSeriesEqual(self.s1, self.s2)
        expected = None
        nt.assert_equal(actual, expected)

    @nt.raises(AssertionError)
    def test_assertserieseq2(self):
        '''Check helper function compares Series, raises error is not equal.'''
        actual = ut.assertSeriesEqual(self.s1, self.s3)

    # Test ndframe_equal
    def test_ndframeeq_DataFrame1(self):
        '''Check helper function compares DataFrames, True.'''
        actual = ut.ndframe_equal(self.df1, self.df2)
        expected = True
        nt.assert_equal(actual, expected)

    def test_ndframeeq_DataFrame2(self):
        '''Check helper function compares DataFrames, False.'''
        actual = ut.ndframe_equal(self.df1, self.df3)
        expected = False
        nt.assert_equal(actual, expected)

    def test_ndframeeq_Series1(self):
        '''Check helper function compares Series, True.'''
        actual = ut.ndframe_equal(self.s1, self.s2)
        expected = True
        nt.assert_equal(actual, expected)

    def test_ndframeeq_Series2(self):
        '''Check helper function compares Series, False.'''
        actual = ut.ndframe_equal(self.s1, self.s3)
        expected = False
        nt.assert_equal(actual, expected)


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


# TODO: How to access the counting branches in ismatched()?
#def test_ismatched_count1():
#    '''Check parens and brakets are counted.'''
#    s1 = '[[][]]]'
#    s2 = '()))()))'
#    actual1 = ut.is_matched(s1)
#    actual2 = ut.ismatched(s2)
#    actual3 = ut.ismatched(''.join(s1, s2))
#    # (bra, ket, par, ren)
#    expected1 = (3, 4, 0, 0)
#    expected1 = (0, 0, 2, 6)
#    expected3 = (3, 4, 2, 6)
#    nt.assert_equal(actual1, expected1)
#    nt.assert_equal(actual2, expected2)
#    nt.assert_equal(actual3, expected3)


# Sort DataFrame Columns ------------------------------------------------------
# TODO: Make a test class to combine DataFrame builds; see TestPandasComparisions
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

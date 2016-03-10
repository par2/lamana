#------------------------------------------------------------------------------
'''Handy tools for global use.'''
# flake8 utils/tools.py --ignore=E265,E501,F841,N802,N803

import os
import re

import pandas as pd
import pandas.util.testing as pdt

import lamana as la


def laminator(geos=None, load_params=None, mat_props=None, ps=[5], verbose=False):
    '''Return a dict of Cases; quickly build and encase a suite of Case objects.

    This is useful for tests requiring laminates with different thicknesses,
    ps and geometries.

    .. note:: DEPRECATE LamAna 0.4.10
            `lamanator` will be removed in LamAna 0.5 and replaced by
            `lamana.distributions.Cases` because the latter is more efficient.

    Parameters
    ----------
    geos : list; default `None`
        Contains tuples of geometry strings.
    load_params : dict; default `None`
        Passed-in geometric parameters if specified; else default is used.
    mat_props : dict; default `None`
        Passed-in materials parameters if specified; else default is used.
    ps : list of int, optional; default 5
        p values to be looped over; this sets the number of rows per DataFrame.
    verbose : bool; default `False`
        If True, print a list of Geometries.

    See Also
    --------
    test_sanity#() : set of test functions that run sanity checks
    utils.tools.get_frames() : utility function to parse DataFrames

    Notes
    -----
    The preferred use for this function is the following:

    >>> for case in cases:
    ...    print(case.LMs)
    [<lamana LaminateModel object (400-200-400S)>,
     <lamana LaminateModel object (400-200-800)>],
    [<lamana LaminateModel object (400-200-400S)>,
     <lamana LaminateModel object (400-200-800)>]

    >>> (LM for case in cases for LM in case.LMs)
    <generator object>

    Examples
    --------
    >>> from lamana.utils import tools as ut
    >>> g = ('400-200-400S')
    >>> case = ut.laminator(geos=g, ps=[2])
    >>> LM = case[0]
    >>> LM
    <lamana LaminateModel object (400-200-400S)>

    >>> g = ['400-200-400S', '400-200-800']
    >>> cases = ut.laminator(geos=g, p=[2,3])
    >>> cases
    {0: <lamana.distributions.Case p=2>,
     1: <lamana.distributions.Case p=3>,}                  # keys by p

    >>> for i, case in cases.items():                      # process cases
    ...     for LM in case.LMs:
    ...         print(LM.Geometry)

    >>> (LM for i, LMs in cases.items() for LM in LMs)     # generator processing

    '''
    # Default
    if (geos is None) and (load_params is None) and (mat_props is None):
        print('CAUTION: No Geometry or parameters provided to case builder.  Using defaults...')
    if geos is None:
        geos = [('400-200-800')]
    if isinstance(geos, str):
        geos = [geos]
    elif (geos is not None) and not (isinstance(geos, list)):
        raise Exception('geos must be a list of tupled strings')

    if load_params is None:
        ''' UPDATE: pull from Defaults()'''
        load_params = {
            'R': 12e-3,                                    # specimen radius
            'a': 7.5e-3,                                   # support ring radius
            'p': 5,                                        # points/layer
            'P_a': 1,                                      # applied load
            'r': 2e-4,                                     # radial distance from center loading
        }
    if mat_props is None:
        mat_props = {
            'HA': [5.2e10, 0.25],
            'PSu': [2.7e9, 0.33],
        }

    # Laminates of different ps
    '''Fix to output repr; may do this with an iterator class.'''
    def cases_by_p():
        for i, p in enumerate(ps):
            '''raise exception if p is not int.'''
            load_params['p'] = p
            case = la.distributions.Case(load_params, mat_props)
            case.apply(geos)
            # Verbose printing
            if verbose:
                print('A new case was created. '
                      '# of LaminateModels: {}, p: {}'.format(len(geos), p))
                #print('A new case was created. # LaminateModels: %s, ps: %s' % (len(geos), p))
            #yield p, case
            yield i, case
    return dict((i, case) for i, case in cases_by_p())


# Helpers
def get_multi_geometry(laminate):
    '''Return geometry string parsed from a multi-plied laminate DataFrame.

    Uses pandas GroupBy to extract indices with unique values
    in middle and outer.  Splits the inner_i list by p.  Used in controls.py.
    Refactored for even multi-plies in 0.4.3d4.
    '''
    def chunks(lst, n):
        '''Split up a list into n-sized smaller lists; (REF 018)'''
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def convert_lists(lst):
        '''Convert numeric contents of lists to int then str'''
        return [str(int(i)) for i in lst]

    #print(laminate)
    group = laminate.groupby('type')
    nplies = len(laminate['layer'].unique())
    if nplies < 5:
        raise Exception('Number of plies < 5.  Use get_special_geometry() instead.')
    p = laminate.groupby('layer').size().iloc[0]           # should be same for each group

    # Identify laminae types by creating lists of indices
    # These lists must consider the the inner lists as well
    # Final lists appear to contain strings.

    # Access types by indices
    if nplies % 2 != 0:
        middle_group = group.get_group('middle')
    inner_group = group.get_group('inner').groupby('side')
    outer_group = group.get_group('outer')

    # Convert to list of indices for each group
    if nplies % 2 != 0:
        mid_idx = middle_group.index.tolist()
    in_idx = inner_group.groups['Tens.']                   # need to split in chunks
    out_idx = outer_group.index.tolist()

    # Make lists of inner_i indices for a single stress side_
    # TODO: Would like to make this inner_i splitting more robust
    # TODO: better for it to auto differentiate subsets within inner_i
    in_lst = []
    for inner_i_idx in chunks(in_idx, p):
        #print(inner_i_idx)
        t = laminate.ix[inner_i_idx, 't(um)'].dropna().unique().tolist()
        in_lst.append(t)

    if nplies % 2 != 0:
        mid_lst = laminate.ix[mid_idx, 't(um)'].dropna().unique().tolist()
    in_lst = sum(in_lst, [])                               # flatten list
    out_lst = laminate.ix[out_idx, 't(um)'].dropna().unique().tolist()
    #print(out_lst, in_lst, mid_lst)

    # Convert list thicknesses to strings
    if nplies % 2 != 0:
        mid_con = convert_lists(mid_lst)
    else:
        mid_con = ['0']                                   # for even plies
    out_con = convert_lists(out_lst)

    # Make geometry string
    geo = []
    geo.extend(out_con)
    geo.append(str(in_lst))
    geo.extend(mid_con)
    geometry = '-'.join(geo)
    return geometry


def get_special_geometry(laminate):
    '''Return geometry string parsed from a special-plied (<5) laminate DataFrame.
    Used in controls.py.

    '''
    nplies = len(laminate['layer'].unique())
    geo = [
        str(int(thickness)) for thickness               # gets unique values
        in laminate.groupby('type', sort=False)['t(um)'].first()
    ]
    #print(geo)

    # Amend list by plies by inserting 0 for missing layer type thicknesses; list required for .join
    if nplies == 1:
        #ply = 'Monolith'
        geo.insert(0, '0')                                 # outer
        geo.insert(1, '0')                                 # inner
    elif nplies == 2:
        #ply = 'Bilayer'
        geo.append('0')                                    # middle
        geo.append('0')
    elif nplies == 3:
        #ply = 'Trilayer'
        geo.insert(1, '0')
    elif nplies == 4:
        #ply = '4ply'
        geo.append('0')
        # TODO: use join
        geo[1] = '[' + geo[1] + ']'                        # redo inner in General Convention notation
    else:
        raise Exception('Number of plies > 4.  Use get_multi_geometry() instead.')

    #print('nplies:', nplies)
    #print(geo)
    geometry = '-'.join(geo)
    return geometry


# TODO: Change to `select_frames`
def get_frames(cases, name=None, nplies=None, ps=None):
    '''Yield and print a subset of case DataFrames given a keyword.
    Else, print all DataFrames for all cases.

    Parameters
    ----------
    cases : list of DataFrames
        Contains case objects.
    name : str
        Common name.
    nplies : int
        Number of plies.
    ps : int
        Number of points per layer.

    Examples
    --------
    >>> cases_selected = ut.get_frames(cases, name='Trilayer', ps=[])
    >>> LMs_list = list(cases)                              # capture generator contents
    >>> LMs_list = [LM for LM in cases_selected]            # capture and exhaust generator
    >>> for LMs in cases_selected:                          # exhaust generator; see contents
    ...    print(LMs)

    See Also
    --------
    lamana.distributions.Cases.select() : canonical way to select df subsets.

    Yields
    ------
    DataFrame
        Extracted data from a sequence of case objects.

    '''
    # TODO: Add a verbose mode

    # Default
    if ps is None:
        ps = []

    try:
        for i, case in enumerate(cases.values()):          # Python 3
            print('case', i + 1)
            for LM in case.LMs:
                #print(LM.Geometry)
                #print(name, nplies, ps)
                # Select based on what is not None
                if not not ps:                             # if list not empty
                    for p in ps:
                        #print('p', p)
                        if ((LM.name == name) | (LM.nplies == nplies)) & (LM.p == p):
                            #print(LM.LMFrame)
                            print(LM.Geometry)
                            yield LM.LMFrame
                # All ps in the case suite
                elif ((LM.name == name) | (LM.nplies == nplies)):
                    #print(LM.LMFrame)
                    print(LM.Geometry)
                    yield LM.LMFrame
                # No subset --> print all
                if (name is None) & (nplies is None) & (ps == []):
                    #print(LM.LMFrame)
                    print(LM.Geometry)
                    yield LM.LMFrame
    finally:
        print('\n')
        print('Finished getting DataFrames.')


def write_csv(LM, path=None, verbose=True, overwrite=False):
    '''Convert DataFrame to csv files and write them to a specified directory.

    Parameters
    ----------
    LM : DataFrame
        LaminateModel containing data calculations.
    path : str, optional; default `./lamana/output` directory
        Directory path to store resulting csv files.
    verbose : bool; default True
        Print additional information during the writing process.
    overwrite : bool; default False
        Save over files with the same name.  Prevents file incrementation
        and excess files after cyclic calls.

    Returns
    -------
    csv
        Writes csv file of data contained in LM (a DataFrame) to a path.


    '''
    # Parse Laminate Properties
    nplies = LM.nplies
    p = LM.p
    t_total = LM.total * 1e3                               # (in mm)
    geometry = LM.Geometry.string
    df = LM.LMFrame

    # Default csv to output directory
    if path is None:
        # TODO: write file paths pythonically; use abspath()
        path = os.getcwd()                                 # use for the test in the correct path
        ##path = path + r'\lamana\tests\controls_LT'         # for Main Script. Comment out in tests
        path = ''.join([path, r'\lamana\output'])

    # Prepend files with 'w' for "written" by the package
    template = '\w_laminate_{}ply_p{}_t{:.1f}_'.format(nplies, p, t_total)
    suffix = '.csv'
    fullpath = ''.join([path, template, geometry, suffix])
    #print(path)

    # Read for duplicates; overwrite protection
    if not overwrite:
        #Read dir if file exists.  Then append counter to path name
        counter = 1
        while os.path.isfile(fullpath):
            print('Overwrite protection: File exists.  Writing new file...')
            fullpath = ''.join([path, template, geometry, '_', str(counter), suffix])
            counter += 1
    df.to_csv(fullpath)

    # Write files
    if verbose:
        print('Writing DataFrame to csv in:', fullpath)


def compare_set(it, others, how='union', test=None):
    '''Return a specific set of unique values based on `how` it is evaluated.

    Wraps set operators from the standard library.  Used to check values in demo.

    Parameters
    ----------
    it, others : iterable
        A container of unique or non-unique values.
    how : {'union', 'intersection', 'difference', 'symmetric_difference'}; default 'union'
        Determine which type of set to use.  Applies set theory.
    test : {'issubset', 'issuperset', 'isdisjoint'}; default `None`
        Test the type of subset.

    '''
    # Defaults
    if isinstance(it, int):
        it = [it]
    if isinstance(others, int):
        others = [others]
    if test is None:
        test = ''

    # Tests
    # Subset: [1,2] < [1,2,3] -> True; [1,2] <= [1,2] -> True
    if test.startswith('issub'):
        return set(it).issubset(others)
    # Subset: [1,2,3] > [1,2] -> True; [1,2,3] >= [1,2,3] -> True
    if test.startswith('issuper'):
        return set(it).issuperset(others)
    # Disjoint: [1,2] , [3,4] -> True
    if test.startswith('isdis'):
        return set(it).isdisjoint(others)

    # Set Theory
    # Union: [1,2] | [3,4] -> {1,2,3,4}
    if how.startswith('uni'):
        return set(it).union(others)
    # Intersection: [1] & [1,2] -> {1}
    elif how.startswith('int'):
        return set(it).intersection(others)
    # Difference: [1,2,3] - [3,4] -> {1,2}
    elif how.startswith('diff'):
        return set(it).difference(others)
    # Symmetric Difference: [1,2,3] ^ [3,4] -> {1,2,4}
    elif how.startswith('symm'):
        return set(it).symmetric_difference(others)


def ndframe_equal(ndf1, ndf2):
    '''Return True if DataFrames (or Series) are equal; else False.

    Parameters
    ----------
    ndf1, ndf2 : Series or DataFrame
        Two groups of data in pandas data structures.

    '''
    try:
        if isinstance(ndf1, pd.DataFrame) and isinstance(ndf2, pd.DataFrame):
            pdt.assert_frame_equal(ndf1, ndf2)
            #print('DataFrame check:', type(ndf1), type(ndf2))
        elif isinstance(ndf1, pd.Series) and isinstance(ndf2, pd.Series):
            pdt.assert_series_equal(ndf1, ndf2)
            #print('Series check:', type(ndf1), type(ndf2))
        return True
    except (ValueError, AssertionError, AttributeError):
        return False


def is_matched(pattern, string):
    '''Return True if container brackets or parentheses have equal count; matched.

    Parameters
    ----------
    pattern : str
        Regular expression pattern.
    string : str
        String to which the pattern in search.

    Examples
    --------
    >>> s = 'Here the [brackets] are matched.'
    >>> p = '.'                                            # regular expression pattern for all
    >>> is_matched(p, s)
    True

    >>> s = 'Here the [brackets][ are NOT matched.'
    >>> p = '.'                                           # regular expression pattern
    >>> is_matched(p, s)
    False

    '''
    # TODO: all default pattern for 'all' (.) if none supplied; make pattern optional
    search = re.findall(pattern, string)                   # quick, non-iterative extraction
    if '[' or ']' in search:
        bra = search.count('[')
        ket = search.count(']')
    if '(' or ')' in search:
        par = search.count('(')
        ren = search.count(')')
    #print(bra, ket, par, ren)
    return bra == ket and par == ren

# =============================================================================
# CITED CODE ------------------------------------------------------------------
# =============================================================================
# Code is modified from existing examples and cited in reference.py


def set_column_sequence(df, seq):
    '''Return a DataFrame with columns sorted by a given sequence (REF 007).

    Parameters
    ----------
    df : DataFrame
        One with unsorted columns.
    seq : list-like
        List of column names in desired order.

    Notes
    -----
    If DataFrame columns are not found in the given sequence, they are appended
    of the end of the DataFrame.

    Examples
    --------
    >>> # Pandas orders DataFrame columns alphabetically
    >>> data = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    >>> df = pd.DataFrame(data, index=['amount'])
    >>> df
            apple  banana  blueberry  orange
    amount      4       2          3       3

    >>> # We can resequence the columns
    >>> seq = ['apple', 'orange', 'banana', 'blueberry']
    >>> set_column_sequence(df, seq)
            apple  banana  orange  blueberry
    amount      4       2       3          3

    >>> # Excluded names are appended to the end of the DataFrame
    >>> seq = ['apple', 'orange']
    >>> set_column_sequence(df, seq)
            apple  banana  orange  blueberry
    amount      4       2       3          3

    '''
    cols = seq[:]                                          # copy so we don't mutate seq
    for x in df.columns:
        if x not in cols:
            cols.append(x)
    return df[cols]


def assertSeriesEqual(s1, s2, **kwds):
    '''Return True if two Series are equal.

    Parameters
    ----------
    {s1, s2} : DataFrame
        Compare two objects using pandas testing tools.
    **kwds : dict-like
        Keywords for `pandas.util.testing.assert_series_equal()`.

    '''
    from pandas.util.testing import assert_series_equal
    return assert_series_equal(s1, s2, **kwds)


# TODO: Determine what `check_less_precise` needs.  Post-theories tests use this.
def assertFrameEqual(df1, df2, **kwds):
    '''Return True if two DataFrames are equal, ignoring order of columns (REF 014).

    Parameters
    ----------
    {df1, df2} : DataFrame
        Compare two objects using pandas testing tools.
    **kwds : dict-like
        Keywords for `pandas.util.testing.assert_frame_equal()`.

    '''
    from pandas.util.testing import assert_frame_equal
    # `sort` is deprecated; works in pandas 0.16.2; last worked in lamana 0.4.9
    # replaced `sort` with `sort_index` for pandas 0.17.1; backwards compatible
    return assert_frame_equal(df1.sort_index(axis=1), df2.sort_index(axis=1),
                              check_names=True, **kwds)
    ##return assert_frame_equal(df1.sort(axis=1), df2.sort(axis=1),
    ##                          check_names=True, **kwds)


# TODO: Remove unused "my_file" and test
def read_csv_dir(path, *args, **kwargs):
    '''Yield all csv files in a directory (REF 013).'''
    # Read all files in path
    for dir_entry in os.listdir(path):
        dir_entry_path = os.path.join(path, dir_entry)
        # TODO: How to test this if branch?
        if os.path.isfile(dir_entry_path):
            # TODO: clean up and remove my_file; test affects
            with open(dir_entry_path, 'r') as my_file:
                # Assumes first column are indices
                file = pd.read_csv(dir_entry_path, *args, index_col=0, **kwargs)
                yield file


# TODO: Rename to int extractor.  sorting happen else where with an iterator and sorted().
# TODO: Refine explanation, especially the return.  Why is it a 3-item list.
# TODO: call data data_keys
def natural_sort(data):
    '''Return a list naturally sorted by numeric strings, as read by humans (REF 027).

    Parameters
    ----------
    data : string-like
        Assumes a key (str), or key-value pair (tuple) containing a string,
        e.g. '14-ply', ('1-ply', None).  Numeric strings are used to sort.

    Notes
    -----
    This function extracts string information from `data` w/reguar expressions
    and parses numbers, if found.  These numeric strings are converted to
    integers.  The result for each `string_` is a three part list of str and int
    such as ['', 1, '-ply'].  The `sorted()` function is smart enough to sort by
    numerical order.  Use this function in an iterator.

    This helper function is used as a "key=" parameter with the `sorted()` function,
    so it's design is a bit different than typical functions.  Some preparation
    is required to pass the appropriate data-type in.

    Examples
    --------
    >>> # Dicts are not normally sorted; we could therefore invoke `sorted()`
    >>> # However, `sorted()`` does not order numeric strings like humans, e.g.
    >>> dict_ = {'3-ply': None, '1-ply': None, '10-ply': None, '2-ply': None}
    >>> data_sorted = sorted(dict_)
    >>> data_sorted
    ['1-ply', '10-ply', '2-ply', '3-ply']                  # not naturally sorted; NOTE only keys returned

    >>> # Therefore, we use `natural_sort()` in combination with `sorted()`.
    >>> # Now we can naturally sort the keys of the dict.
    >>> [k for k in sorted(dict_, key=natural_sort)]
    ['1-ply', '2-ply', '3-ply', '10-ply']

    >>> # Notice, `sorted()` automatically sorts dicts by keys; the following is equivalent
    >>> [k for k in sorted(dict_.keys(), key=natural_sort)]
    ['1-ply', '2-ply', '3-ply', '10-ply']

    >>> # `natural_sort()` can also handle data as key-value tuples
    >>> [k for k in sorted(dict_.items(), key=natural_sort)]
    [('1-ply', None), ('2-ply', None), ('3-ply', None), ('10-ply', None)]

    '''
    #print(data, type(data))
    # Extract string from a key in a sorted dict; if data.keys() used
    if isinstance(data, str):
        string_ = data                                     # only key

    # Extract string from a key-value tuple in a sorted dict; if data.items() used
    elif isinstance(data, tuple):
        #string_ = data[0]
        string_, list_ = data                             # key, value pair
    #print(string_)

    #TODO: Need to complete; doesn't really do any sorting, just sets up the iterator.  Redo.
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

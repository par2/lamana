#------------------------------------------------------------------------------
# Handy tools for global use
# flake8 utils/tools.py --ignore=E265,E501,F841,N802,N803

import os
import re

import pandas as pd
import pandas.util.testing as pdt

import lamana as la


## DEPRECATE
def laminator(geos=None, load_params=None, mat_props=None, ps=[5], verbose=False):
    '''Return a dict of Cases; quickly build and encase a suite of Case objects.

    This is useful for tests requiring laminates with different thicknesses,
    ps and geometries.

    Variables
    =========
    geos : list; Default: None
        Contains tuples of geometry strings
    load_params : dict; Default: None
        Passed-in geometric parameters if specified; else default is used.
    mat_props : dict; Default: None
        Passed-in materials parameters if specified; else default is used.
    ps : list; ints
        p values to be looped over; this sets the number of rows per DataFrame.
    verbose : bool; False
        If True, print a list of Geometries.

    Example
    =======
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
         1: <lamana.distributions.Case p=3>,}              # keys by p

    >>> for i, case in cases.items():                      # process cases
    ...     for LM in case.LMs:
    ...         print(LM.Geometry)

    >>> (LM for i, LMs in cases.items() for LM in LMs)     # generator processing

    Preferred
    =========
    >>> for case in cases:
    ...    print(case.LMs)
        [<lamana LaminateModel object (400-200-400S)>,
         <lamana LaminateModel object (400-200-800)>],
        [<lamana LaminateModel object (400-200-400S)>,
         <lamana LaminateModel object (400-200-800)>]

    >>> (LM for case in cases for LM in case.LMs)
        <generator object>

    See Also
    ========
    test_...sanity#() and utils.tools.get_frames()

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
###DEPRECATE
def get_multi_geometry(laminate):
    '''Return geometry string parsed from a multi-plied laminate DataFrame.

    Uses pandas GroupBy to extract indices with unique values
    in middle and outer.  Splits the inner_i list by p.  Used in controls.py.

    UPDATE: refactor for even multi-plies 0.4.3d4
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
    '''Would like to make this inner_i splitting more robust'''
    '''Better for it to auto differentiate subsets within inner_i'''
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


###DEPRECATE
def get_special_geometry(laminate):
    '''Return geometry string parsed from a special-plied (<5) laminate DataFrame.
    Used in controls.py.'''
    nplies = len(laminate['layer'].unique())
    geo = [str(int(thickness)) for thickness               # gets unique values
        in laminate.groupby('type', sort=False)['t(um)'].first()]
    #print(geo)

    # Amend list by plies by inserting 0 for missing layer type thicknesses; list required for .join
    if nplies == 1:
        ply = 'Monolith'
        geo.insert(0, '0')                                 # outer
        geo.insert(1, '0')                                 # inner
    elif nplies == 2:
        ply = 'Bilayer'
        geo.append('0')                                    # middle
        geo.append('0')
    elif nplies == 3:
        ply = 'Trilayer'
        geo.insert(1, '0')
    elif nplies == 4:
        ply = '4ply'
        geo.append('0')
        '''There is some pythonic way to do this by Raymond Hettinger; but same thing.'''
        geo[1] = '[' + geo[1] + ']'                        # redo inner in General Convention notation
    else:
        raise Exception('Number of plies > 4.  Use get_multi_geometry() instead.')

    #print('nplies:', nplies)
    #print(geo)
    geometry = '-'.join(geo)
    return geometry

'''Change to select_frames()...'''


###DEPRECATE
def get_frames(cases, name=None, nplies=None, ps=None):
    '''Yield and print a subset of case DataFrames given a keyword.
    Else, prints all DataFrames for all cases.

    Examples
    ========
    >>>cases_selected = ut.get_frames(cases, name='Trilayer', ps=[])
    >>>LMs_list = list(cases)                              # capture generator contents
    >>>LMs_list = [LM for LM in cases_selected]            # capture and exhaust generator
    >>>for LMs in cases_selected:                          # exhaust generator; see contents
    ...    print(LMs)
    '''
    '''Add a verbose mode'''
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
    '''Convert DataFrames to csv files and write them to a specified
    directory.'''
    # Parse Laminate Properties
    nplies = LM.nplies
    p = LM.p
    t_total = LM.total * 1e3                               # (in mm)
    geometry = LM.Geometry.string
    df = LM.LMFrame

    # Default csv to output directory
    if path is None:
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
    '''Compile set operators from the standard library.'''
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
    '''Returns True if DataFrames (or Series) are equal; else False.'''
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
    '''Return True if container ends have equal count; matched.'''
    search = re.findall(pattern, string)                   # quick, non-iterative extraction
    if '[' or ']' in search:
        bra = search.count('[')
        ket = search.count(']')
    if '(' or ')' in search:
        par = search.count('(')
        ren = search.count(')')
    #print(bra, ket, par, ren)
    return bra == ket and par == ren


# Cited Code ------------------------------------------------------------------
def set_column_sequence(df, seq):
    '''Takes a DataFrame and a subsequence of its columns, then returns
    a DataFrame with columns sorted by seq. (REF 007).'''
    cols = seq[:]                                          # copy so we don't mutate seq
    for x in df.columns:
        if x not in cols:
            cols.append(x)
    return df[cols]


def assertFrameEqual(df1, df2, **kwds):
    '''Assert two DataFrames are equal, ignoring column order; (REF 014).'''
    from pandas.util.testing import assert_frame_equal
    # `sort` is deprecated; works in pandas 0.16.2; last worked in lamana 0.4.9
    # replaced `sort` with `sort_index` for pandas 0.17.1; backwards compatible
    return assert_frame_equal(df1.sort_index(axis=1), df2.sort_index(axis=1),
                              check_names=True, **kwds)
    ##return assert_frame_equal(df1.sort(axis=1), df2.sort(axis=1),
    ##                          check_names=True, **kwds)

'''Determine what check_less_precise requires.  Some post_theories test use this.'''


def assertSeriesEqual(s1, s2, **kwds):
    '''Assert two Series are equal.'''
    from pandas.util.testing import assert_series_equal
    return assert_series_equal(s1, s2, **kwds)


def read_csv_dir(path, *args, **kwargs):
    '''Return all csv files in a directory; (REF 013).'''
    # Read all files in path
    for dir_entry in os.listdir(path):
        dir_entry_path = os.path.join(path, dir_entry)
        if os.path.isfile(dir_entry_path):
            with open(dir_entry_path, 'r') as my_file:
                # Assumes first column are indices
                file = pd.read_csv(dir_entry_path, *args, index_col=0, **kwargs)
                yield file


def natural_sort(data):
    '''Sort numbers natural as humans would read them (REF 027); assumes sorting a dict.'''
    if isinstance(data, str):
        string_ = data
    # Extract string from tuple of a sorted dict
    elif isinstance(data, tuple):
        string_ = data[0]
    #print(string_)
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

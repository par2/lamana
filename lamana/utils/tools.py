#------------------------------------------------------------------------------
'''Handy tools for global use.

- build cases quickly
- read geo_strings from DataFrames
- write/read csv files to DataFrames
- compare sets
- resequence columns in DataFrame
- determine if brackets/parentheses match in a string
- assert pandas Series/DataFrames
- natural sort strings

'''
# flake8 utils/tools.py --ignore=E265,E501,F841,N802,N803


import os
import re
import logging
import tempfile
import inspect
import warnings
import collections as ct

import pandas as pd
import pandas.util.testing as pdt


from .. import input_
from .. import distributions
from .. import theories
from .utils import config


# import lamana as la
# from lamana.utils import config


# TODO: Add deprecation warning
def laminator(geos=None, load_params=None, mat_props=None, ps=[5], verbose=False):
    '''Return a dict of Cases; quickly build and encase a suite of Case objects.

    This is useful for tests requiring laminates with different thicknesses,
    ps and geometries.

    .. note:: Deprecate warning LamAna 0.4.10
            `lamanator` will be removed in LamAna 0.5 and replaced by
            `lamana.distributions.Cases` because the latter is more efficient.

    Parameters
    ----------
    geos : list; default `None`
        Contains (optionally tuples of) geometry strings.
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
    utils.tools.select_frames() : utility function to parse DataFrames

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
        # TODO: use custom Exception
        raise Exception('geos must be a list of strings')

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
            case = distributions.Case(load_params, mat_props)
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
def get_multi_geometry(Frame):
    '''Return geometry string parsed from a multi-plied laminate DataFrame.

    Uses pandas GroupBy to extract indices with unique values
    in middle and outer.  Splits the inner_i list by p.  Used in controls.py.
    Refactored for even multi-plies in 0.4.3d4.

    Parameters
    ----------
    Frame : DataFrame
        A laminate DataFrame, typically extracted from a file.  Therefore,
        it is ambigouous whether Frame is an LFrame or LMFrame.

    Notes
    -----
    Used in controls.py, extract_dataframe() to parse data from files.

    See Also
    --------
    - get_special_geometry: for getting geo_strings of laminates w/nplies<=4.

    '''
    # TODO: Move to separate function in utils
    def chunks(lst, n):
        '''Split up a list into n-sized smaller lists; (REF 018)'''
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    # TODO: why convert to int?; consider conversion to str
    def convert_lists(lst):
        '''Convert numeric contents of lists to int then str'''
        return [str(int(i)) for i in lst]

    #print(Frame)
    group = Frame.groupby('type')
    nplies = len(Frame['layer'].unique())
    if nplies < 5:
        raise Exception('Number of plies < 5.  Use get_special_geometry() instead.')
    p = Frame.groupby('layer').size().iloc[0]              # should be same for each group

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
    # NOTE: inner values are converting to floats somewhere, i.e. 400-200-800 --> 400-[200.0]-800
    # Might be fixed with _gen_convention, but take note o the inconsistency.
    # Looks like out_lst, in_lst, mid_lst are all floats.  Out and mid convert to ints.
    in_lst = []
    for inner_i_idx in chunks(in_idx, p):
        #print(inner_i_idx)
        t = Frame.ix[inner_i_idx, 't(um)'].dropna().unique().tolist()
        in_lst.append(t)

    if nplies % 2 != 0:
        mid_lst = Frame.ix[mid_idx, 't(um)'].dropna().unique().tolist()
    in_lst = sum(in_lst, [])                               # flatten list
    out_lst = Frame.ix[out_idx, 't(um)'].dropna().unique().tolist()
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
    geo_string = '-'.join(geo)
    # TODO: format geo_strings to General Convention
    # NOTE: geo_string comes in int-[float]-int format; _to_gen_convention should patch
    geo_string = input_.Geometry._to_gen_convention(geo_string)
    return geo_string


def get_special_geometry(Frame):
    '''Return geometry string parsed from a special-plied (<5) laminate DataFrame.

    Parameters
    ----------
    Frame : DataFrame
        A laminate DataFrame, typically extracted from a file.  Therefore,
        it is ambigouous whether Frame is an LFrame or LMFrame.

    Notes
    -----
    Used in controls.py, extract_dataframe() to parse data from files.

    See Also
    --------
    - get_multi_geometry: for getting geo_strings of laminates w/nplies>=5.

    '''
    #nplies = len(laminate['layer'].unique())
    #geo = [
    #    str(int(thickness)) for thickness               # gets unique values
    #    in laminate.groupby('type', sort=False)['t(um)'].first()
    #]
    nplies = len(Frame['layer'].unique())
    geo = [
        str(int(thickness)) for thickness               # gets unique values
        in Frame.groupby('type', sort=False)['t(um)'].first()
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
        #ply = '4-ply'
        geo.append('0')
        # TODO: use join
        geo[1] = '[' + geo[1] + ']'                        # redo inner in General Convention notation
    else:
        # TODO: use custom Exception
        raise Exception('Number of plies > 4.  Use get_multi_geometry() instead.')

    #print('nplies:', nplies)
    #print(geo)
    geo_string = '-'.join(geo)
    # TODO: format geo_strings to General Convention
    geo_string = input_.Geometry._to_gen_convention(geo_string)
    return geo_string


# TODO: Add extract_dataframe and fix_discontinuities here from controls.py; make tests.

# DEPRECATE: remove and replace with Cases() (0.4.11.dev0)
# Does not print cases accurately
# Did not fail test although alias given for name
#def get_frames(cases, name=None, nplies=None, ps=None):
# def select_frames(cases, name=None, nplies=None, ps=None):
#     '''Yield and print a subset of case DataFrames given cases.

#     Else, print all DataFrames for all cases.

#    .. note:: DEPRECATE LamAna 0.4.11.dev0
#            `lamanator` will be removed in LamAna 0.5 and replaced by
#            `lamana.distributions.Cases` because the latter is more efficient.
#
#     Parameters
#     ----------
#     cases : list of DataFrames
#         Contains case objects.
#     name : str
#         Common name.
#     nplies : int
#         Number of plies.
#     ps : int
#         Number of points per layer.

#     Examples
#     --------
#     >>> cases_selected = ut.select_frames(cases, name='Trilayer', ps=[])
#     >>> LMs_list = list(cases)                              # capture generator contents
#     >>> LMs_list = [LM for LM in cases_selected]            # capture and exhaust generator
#     >>> for LMs in cases_selected:                          # exhaust generator; see contents
#     ...    print(LMs)

#     Notes
#     -----
#     This function is a predecessor to the modern Cases.select() method.  It is
#     no longer maintained (0.4.11.dev0), though possibly useful for extracting
#     selected DataFrames from existing cases.  Formerly `get_frames()`.

#     See Also
#     --------
#     lamana.distributions.Cases.select() : canonical way to select df subsets.

#     Yields
#     ------
#     DataFrame
#         Extracted data from a sequence of case objects.

#     '''
#     # Default
#     if ps is None:
#         ps = []

#     try:
#         for i, case in enumerate(cases.values()):          # Python 3
#             print('case', i + 1)
#             for LM in case.LMs:
#                 #print(LM.Geometry)
#                 #print(name, nplies, ps)
#                 # Select based on what is not None
#                 if not not ps:                             # if list not empty
#                     for p in ps:
#                         #print('p', p)
#                         if ((LM.name == name) | (LM.nplies == nplies)) & (LM.p == p):
#                             #print(LM.LMFrame)
#                             print(LM.Geometry)
#                             yield LM.LMFrame
#                 # All ps in the case suite
#                 elif ((LM.name == name) | (LM.nplies == nplies)):
#                     #print(LM.LMFrame)
#                     print(LM.Geometry)
#                     yield LM.LMFrame
#                 # No subset --> print all
#                 if (name is None) & (nplies is None) & (ps == []):
#                     #print(LM.LMFrame)
#                     print(LM.Geometry)
#                     yield LM.LMFrame
#     finally:
#         print('\n')
#         print('Finished getting DataFrames.')


def compare_set(it, others, how='union', test=None):
    '''Return a specific set of unique values based on `how` it is evaluated.

    Wraps set operators from the standard library.  Used to check values in demo.

    Parameters
    ----------
    it, others : iterable
        A container of unique or non-unique values.
    how : {'union', 'intersection', 'difference', 'symmetric_difference'}; default 'union'.
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
    # Superset: [1,2,3] > [1,2] -> True; [1,2,3] >= [1,2,3] -> True
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


# Refactor to favor string as first arg (0.4.11.dev0)
def is_matched(string, pattern=None):
    '''Return True if container brackets or parentheses have equal count; matched.

    Parameters
    ----------
    string : str
        String to which the pattern in search.
    pattern : str; Default None
        Regular expression pattern.  If None, defaults to test all characters i.e. '.'.

    Notes
    -----
    This function was made to help validate parsed input strings.

    Examples
    --------
    >>> s = 'Here the [brackets] are matched.'
    >>> is_matched(s)
    True

    >>> s = 'Here the [brackets][ are NOT matched.'
    >>> is_matched(s)
    False

    >>> s = 'Only accept [letters] in brackets that are [CAPITALIZED[.'
    >>> p = '\W[A-Z]+\W'                                   # regex for all only capital letters and non-alphannumerics
    >>> is_matched(s, p)
    False

    '''
    if pattern is None:
        pattern = '.+'                                     # default for all characters together (greedily)
    bra, ket, par, ren = 0, 0, 0, 0

    search = re.findall(pattern, string)                   # quick, non-iterative extraction
    for item in search:
        if ('[' in item) or (']' in item):
            bra, ket = item.count('['), item.count(']')
        if ('(' in item) or (')' in item):
            par, ren = item.count('('), item.count(')')
    #print(search, len(search))
    #print('l_bracket: {0}, r_bracket: {1}, '
    #      'l_paren {2}, r_paren: {3}'.format(bra, ket, par, ren))
    return bra == ket and par == ren


# IO --------------------------------------------------------------------------
# IO-related functions
# DEPRECATE: verbose; use logging instead
def rename_tempfile(filepath, filename):
    '''Return new file path; renames an extant file in-place.'''
    dirpath = os.path.dirname(filepath)
    new_filepath = os.path.join(dirpath, filename)
    new_filepath = get_path(validate=new_filepath)
    os.rename(filepath, new_filepath)
    return new_filepath


# TODO: Add write functions from controls.py here
def convert_featureinput(FI):
    '''Return FeaureInput dict with converted values to Dataframes.

    Can accept almost any dict.  Converts to DataFrames depending on type.

    Returns
    -------
    defaultdict
        Values are DataFrames.

    '''
    logging.info('Converting FeatureInput values to DataFrames: {}...'.format(
        FI.get('Geometry')))

    dd = ct.defaultdict(list)
    for k, v in FI.items():
        if isinstance(v, dict):
            try:
                # if dict of dicts
                dd[k] = pd.DataFrame(v).T
            except(ValueError):
                # if regular dict, put in a list
                dd[k] = pd.DataFrame([v], index=[k]).T
            finally:
                logging.debug('{0} {1} -> df'.format(k, type(v)))
        elif isinstance(v, list):
            dd[k] = pd.DataFrame(v, columns=[k])
            logging.debug('{0} {1} -> df'.format(k, type(v)))
        elif isinstance(v, str):
            dd[k] = pd.DataFrame({'': {k: v}})
            logging.debug('{0} {1} -> df'.format(k, type(v)))
        elif isinstance(v, input_.Geometry):
            v = v.string                                       # get geo_string
            dd[k] = pd.DataFrame({'': {k: v}})
            logging.debug('{0} {1} -> df'.format(k, type(v)))
        elif isinstance(v, pd.DataFrame):                      # sometimes materials is df
            dd[k] = v
            logging.debug('{0} {1} -> df'.format(k, type(v)))
        elif not v:                                            # empty container
            dd[k] = pd.DataFrame()
            logging.debug('{0} {1} -> empty df'.format(k, v))
        else:
            logging.debug('{0} -> Skipped'.format(type(v)))    # pragma: no cover

    return dd


def reorder_featureinput(d, keys=None):
    '''Return an OrderedDict given a list of keys.

    Parameters
    ----------
    d : dict
        Any dict; expects a FeatureInput.
    keys : list of strings, default None
        Order of keys of a FeatureInput.

    Examples
    --------
    >>> case = ut.laminator(dft.geos_standard)[0]
    >>> LM = case.LMs[0]
    >>> FI = LM.FeatureInput

    >>> # Default order
    >>> fi = reorder_featureinput(FI)
    >>> list(fi.keys())
    ['Geometry',  'Model', 'Materials', 'Parameters', 'Globals', 'Properties']

    >>> # Manage key order
    >>> rev_keys = reversed(['Geometry',  'Model', 'Materials',
    ... 'Parameters', 'Globals', 'Properties'])
    >>> fi = reorder_featureinput(FI, keys=rev_keys)
    >>> list(fi.keys())
    ['Properties', 'Globals', 'Parameters', 'Materials', 'Model', 'Geometry']

    >>> # Add missing keys (in random order)
    >>> fi = reorder_featureinput(FI, [Model', 'Geometry'])
    >>> list(fi.keys())
    ['Model', 'Geometry', 'Materials', 'Parameters', 'Globals', 'Properties']

    Notes
    -----
    - Keys are optional; assumes a typical FeatureInput with default keys.
    - If passed keys are shorter the FI keys, ignores empty entries.
    - Groups single string entries (i.e. Geometry, Model) upfront for dashboard.
    - Properties are last as the materials expand expand column-wise.

    '''
    # Default keys for standard FeatureInput
    if keys is None:
        keys = ['Geometry', 'Model', 'Materials', 'Parameters',
                'Globals', 'Properties']

    od = ct.OrderedDict()
    for key in keys:
        if key in d:                                       # skip Globals in Laminate.FeaturInput
            od[key] = d[key]

    # If keys is shorter than FI.keys(), tag on the missing keys
    for k in d.keys():
        if k not in od:
            od[k] = d[k]

    return od


def get_path(filename=None, prefix=None, suffix=None, overwrite=True,
             dashboard=False, validate=None,):
    '''Return the default export path or a file path if given a filename.

    Verifies existing paths, else returns an new path.

    Parameters
    ----------
    filename : str, default None
        File name.
    prefix : str, default None
        File name prefix.
    suffix : |'.csv'|'.xlsx'|, default None
        File name extension.
    overwrite : bool, default True
        Toggle of overwrite protection. If False, increments filename.
    dashboard : bool, default False
        Auto-append 'dash_' to filename.  Flag a dashboard is being made;
        only .csv files supportted.
    validate : str, default None, optional
        Verifies if full file path exists; if so, return incremented file path.

    Notes
    -----
    Need to return different types of paths depending on output file.  Here is
    what this function can do:
    - OK  Standardize the default "\export" directory
    - OK  Give path for csv data file
    - OK  Give path for csv dashboard file; prepend "dash_"
    - OK  Give path for xlsx file only (no dashboard)
    - OK  Support overwrite protection of pre-existing files
    - OK  Reprocess paths for temporary files
    - X   Join path components and return a safe path
    - X   Accept directory paths arg to override the default path; security issue

    Key Terms:
    * currpath = current working directory
    * dirpath = full path - base name
    * filepath = full path (includes suffix)
    * basename = prefix + filename + suffix
    * filename = base name - suffix - prefix

    Raises
    ------
    OSError : verify working directory starts at the package root prior writing.

    Returns
    -------
    str
        Default export directory path, unless given other information

    '''

    # Helpers -----------------------------------------------------------------
    def protect_overwrite(filepath):
        '''Return a new filepath by looping existing files and incrementing.

        Notes
        -----
        - Check for duplicates before writing; overwrite protection
        - Read dir if file exists.  Append counter to path name if exists.

        '''
        basename = os.path.basename(filepath)
        dirpath = os.path.dirname(filepath)
        counter = 1
        # Edit basename

        while os.path.isfile(filepath):
            ##suffix = [ext for ext in EXTENSIONS if basename.endswith(ext)][0]
            ##filename = basename.replace(suffix, '')
            filename, suffix = os.path.splitext(basename)
            logging.debug('filename: {}, suffix: {}'.format(filename, suffix))

            increment = ''.join(['(', str(counter), ')'])
            filename = ''.join([filename, increment])
            logging.info("Overwrite protection: filename exists."
                         " Incrementing name to '{}' ...".format(filename))
            # Pretend the default directory path with a simple recursive call
            ##filepath = get_path(filename=filename, suffix=suffix, overwrite=True)  # or inifinite loop
            filepath = os.path.join(dirpath, ''.join([filename, suffix]))
            counter += 1
        return filepath

    # Reset Defaults ----------------------------------------------------------
    if filename is None:
        filename = ''
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = ''
    elif suffix.endswith('csv'):
        suffix = config.EXTENSIONS[0]
    elif suffix.endswith('xlsx'):
        suffix = config.EXTENSIONS[1]

    # Set Root/Source/Default Paths -------------------------------------------
    # The export folder is relative to the root (package) path
    # sourcepath = os.path.abspath(os.path.dirname(la.__file__))
    # packagepath = os.path.dirname(sourcepath)
    # if not os.path.isfile(os.path.join(packagepath, 'setup.py')):
    if not os.path.isfile(os.path.join(config.PACKAGEPATH, 'setup.py')):
        raise OSError(
            'Package root path location is not correct: {}'
            ' Verify working directory is ./lamana.'.format(packagepath)
        )
    # defaultpath = os.path.join(config.PACKAGEPATH, 'export')
    #
    # dirpath = defaultpath

    dirpath = config.DEFAULTPATH


    logging.debug('Root path: {}'.format(config.PACKAGEPATH))
    if not filename and (suffix or dashboard):
        logging.warn("Missing 'filename' arg.  Using default export directory ...")

    # File Path ---------------------------------------------------------------
    if validate:
        # Just check if exists.  Give new filepath is so.
        return protect_overwrite(validate)

    if filename:
        prefix = 'dash_'if dashboard and suffix.endswith('csv') else ''
        if dashboard and not suffix.endswith('csv'):
            logging.info('Only .csv files support separate dashboards.'
                         ' Using default export directory...')
        if not suffix:
            logging.warn('Missing suffix.  No action taken.')
        basename = ''.join([prefix, filename, suffix])
        filepath = os.path.join(dirpath, basename)

        if not overwrite:
            return protect_overwrite(filepath)
        return filepath

    return dirpath


def export(L_, overwrite=False, prefix=None, suffix=None, order=None,
           offset=3, dirpath=None, temp=False, keepname=True, delete=False):
    '''Write LaminateModels and FeatureInput to files; return a tuple of paths.

    Supported formats:
    - .csv: two files; separate data and dashboard files
    - .xlsx: one file; data and dashboard sheets

    Parameters
    ----------
    L_ : Laminate-like object
        Laminate or subclass containing attributes and calculations.
    overwrite : bool; default False
        Save over files with the same name.  Prevents file incrementation
        and excess files after cyclic calls.
    prefix : str; default None
        Prepend a prefix to the filename.  Conventions are:
        - '' : legacy or new
        - 'w': written by the package
        - 't': temporary file; used when tempfile is renamed
        - 'r': redone; altered from legacy
        - 'dash': dashboard
    suffix : |'.csv'|'.xlsx'|
        Determines the file format by appending to filename; default '.xlsx'.
    order: list
        Keys of the FeatureInput.
    offset : int
        Blank columns between data in the dashboard.
    dirpath : str, optional; default "/export" directory
        Directory path to store resulting csv files; custom path NotImplemented.
    temp : bool, default False
        Make temporary files in the OS Temp directory instead.
    keepname : bool, True
        Toggle renaming temporary files; temp must be True.
    delete : bool, default False
        Force file removal after created; mainly used for temporary files.

    Returns
    -------
    tuple
        Full file paths (str) of the created files LM and dashboard data.

    See Also
    --------
    - get_path(): deals with munging paths and validations
    - convert_featureinput(): convert dict values to DataFrames
    - reorder_featureinput(): make and ordered list for the dashboard
    - make_tempfile(): review how Python 'mkstemp' makes temp; NotImplemented
    - rename_tempfile(): rename the file post closing file.

    Notes
    -----
    Contents are written into an "/export" directory. FeatureInput data a.k.a "dashboard".
    We use mkstemp (low-level), which leaves it open for to_excel to write.
    Here are technical characteristics:
    - OK  Outputs different file formats.
    - OK  Writes regular or temporary files (get auto-deleted by the OS; for tests)
    - OK  Calls helper functions to clean paths and datastructures.
    - OK  Allows prefixing for file indentification.
    - OK  Outputs data and dashboards.
    - OK  Works even when files exist in the directory.
    - OK  Auto creates "\export" directory if none exists.
    - OK  Renames temporary files by default.
    - OK  Support Laminate and LaminateModel objects
    - X   Supports custom directory paths.

    Examples
    --------
    >>> from lamana.utils import tools as ut
    >>> case = ut.laminator('400.0-[200.0]-800.0')[0]
    >>> LM = case.LMs[0]
    >>> export(LM)
    '~/lamana/export/laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.xlsx'

    >>> # Overwrite Protection
    >>> export(LM, overwrite=False)
    '~/lamana/export/laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0(1).xlsx'

    >>> # Optional .csv Format
    >>> export(LM, suffix='.csv')
    '~/lamana/export/dash_laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'
    '~/lamana/export/laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'

    >>> # Optional Temporary Files
    >>> export(LM, suffix='.csv', temp=True)
    'temp/t_dash_laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'
    'temp/t_laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'

    >>> # Supports Laminate objects too
    >>> from lamana.models import Wilson_LT as wlt
    >>> dft = wlt.Defaults()
    >>> L = la.constructs.Laminate(dft.FeatureInput)
    >>> export(L)
    '~/lamana/export/dash_laminate_5ply_p5_t2.0_400.0-[200.0]-800.0.xlsx'

    '''
    # Parse for Filename ------------------------------------------------------
    nplies = L_.nplies
    p = L_.p
    # TODO: Fix units
    t_total = L_.total * 1e3                               # (in mm)
    geo_string = L_.Geometry.string
    FI = L_.FeatureInput

    # Path Munge --------------------------------------------------------------
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = config.EXTENSIONS[1]                      # .xlsx

    if dirpath is None:
        ###
        # Prepend files with 'w' for "written" by the package
        # NOTE: removed default w_ prefix; check the control and other uses to maintain coding
        # TODO: rename legacy files with "l_"
        ###
        if hasattr(L_, 'LMFrame'):
            kind = 'laminatemodel'
        else:
            kind = 'laminate'
        filename = r'{}{}_{}ply_p{}_t{:.1f}_{}'.format(
            prefix, kind, nplies, p, t_total, geo_string)

        # Force-create export directory or path (REF 047)
        # Send file to export directory
        defaultpath = get_path()
        if not os.path.exists(defaultpath):
            # TODO: Make sure this log prints out
            logging.info(
                'No default export directory found.  Making directory {} ...'.format(defaultpath)
            )
            os.makedirs(defaultpath)
    else:
        raise NotImplementedError('Custom directory paths are not yet implemented.')

    # Prepare FeatureInput ----------------------------------------------------
    if order is None:
        order = ['Geometry', 'Model', 'Materials',
                 'Parameters', 'Globals', 'Properties']    # default
    converted_FI = convert_featureinput(FI)
    reordered_FI = reorder_featureinput(converted_FI, order)  # elevates strings
    dash_df = pd.concat(converted_FI)                       # combines all dfs into one
    data_df = L_._frame

    # Assemble ----------------------------------------------------------------
    # Build csv data and dashboard (as optional temporary file)
    if not suffix.endswith('xlsx'):
        try:
            # Tempfiles are used to obviate writing to package folders
            if temp:
                data_des, data_filepath = tempfile.mkstemp(suffix=suffix)
                dash_des, dash_filepath = tempfile.mkstemp(suffix=suffix)
            else:
                data_filepath = get_path(
                    filename, suffix=suffix, overwrite=overwrite
                )                                          # pragma: no cover
                dash_filepath = get_path(
                    filename, suffix=suffix, overwrite=overwrite, dashboard=True
                )                                          # pragma: no cover

            # Write File
            data_df.to_csv(data_filepath)
            dash_df.to_csv(dash_filepath)

            # Tempfile Options
            if temp:
                os.close(data_des)
                os.close(dash_des)

            if temp and keepname:
                data_filepath = rename_tempfile(
                    data_filepath, ''.join(['t_', filename, suffix]))
                dash_filepath = rename_tempfile(
                    dash_filepath, ''.join(['t_', 'dash_', filename, suffix]))

            logging.info('DataFrame written as {} file in: {}'.format(suffix, data_filepath))
            logging.info('Dashboard written as {} file in: {}'.format(suffix, dash_filepath))

        finally:
            if delete:
                os.remove(data_filepath)
                os.remove(dash_filepath)
                logging.info('File has been deleted: {}'.format(data_filepath))
                logging.info('File has been deleted: {}'.format(dash_filepath))
            pass
        return (data_filepath, dash_filepath)

    # For Excel Files Only
    elif suffix.endswith('xlsx'):
        try:
            # Tempfiles are used to obviate writing to package folders
            if temp:
                data_des, workbook_filepath = tempfile.mkstemp(suffix=suffix)
            else:
                workbook_filepath = get_path(
                    filename, suffix=suffix, overwrite=overwrite
                )                                          # pragma: no cover

            # Excel worksheet code block --------------------------------------
            writer = pd.ExcelWriter(workbook_filepath)

            # Data sheet
            sheetname = geo_string.replace('[', '|').replace(']', '|')
            data_sheetname = ' '.join(['Data', sheetname])
            data_df.to_excel(writer, data_sheetname)

            # Dashboard sheet
            dash_sheetname = ' '.join(['Dash', sheetname])

            for i, dict_df in enumerate(reordered_FI.values()):
                if dict_df.size == 1:                      # assumes string strs are ordered first
                    dict_df.to_excel(writer, dash_sheetname, startrow=4**i)
                else:
                    dict_df.to_excel(writer, dash_sheetname, startcol=(i-1)*offset)

            writer.save()

            if temp:
                os.close(data_des)

            if temp and keepname:
                workbook_filepath = rename_tempfile(
                    workbook_filepath, ''.join(['t_', filename, suffix]))

            logging.info('Data and dashboard written as {} file in: {}'.format(suffix, workbook_filepath))

        finally:
            if delete:
                os.remove(workbook_filepath)
                logging.info('File has been deleted: {}'.format(workbook_filepath))
            pass

        return (workbook_filepath,)


# Inspection Tools ------------------------------------------------------------
# These tools are used by `theories.handshake` to search for hook functions
def isparent(kls):
    '''Return True is class is a parent.'''
    return kls.__base__ is object


def find_classes(module):
    '''Return a list of class (name, object) tuples.'''
    clsmembers = inspect.getmembers(module, inspect.isclass)
    return clsmembers


def find_methods(kls):
    '''Return a list of method (name, object) tuples.'''
    # For unbound methods removed in Python 3
    mthdmembers = inspect.getmembers(
        kls, predicate=lambda obj: inspect.isfunction(obj) or inspect.ismethod(obj)

    )                                                      # REF 006
    return mthdmembers


def find_functions(module):
    funcmembers = inspect.getmembers(module, inspect.isfunction)
    return funcmembers


# Hook Utils ------------------------------------------------------------------
# These tools are used by `theories.handshake` to search for hook functions
def get_hook_function(module, hookname):
    '''Return the hook function given a module.

    Inspect all functions in a module for one a given a HOOKNAME.  Assumes
    only one hook per module.

    '''
    logging.debug("Given hookname: '{}'".format(hookname))
    functions = [(name, func) for name, func in find_functions(module)
            if name == hookname]
    if not len(functions):
        raise AttributeError('No hook function found.')
    elif len(functions) != 1:
        raise AttributeError('Found more than one hook_function in {}'
                             ' Expected only one per module.'.format(module))
    _, hook_function = functions[0]
    logging.debug('Hook function: {}'.format(hook_function))

    return hook_function


def get_hook_class(module, hookname):
    '''Return the class containing the hook method.

    Inspect all classes in a module for a method with a given HOOKNAME. Assumes
    only one hook per module.  Return the class so that it can be later
    instantiated for it's hook method.

    '''
    logging.debug("Given hookname: '{}'".format(hookname))
    methods = []
    all_methods = []
    for name, kls in find_classes(module):
        logging.debug('Found class: {}'.format(kls))
        # Need to make sure we not looking in the parent class BaseModel
        if issubclass(kls, theories.BaseModel) and not isparent(kls):
            logging.debug('Sub-classes of BaseModel: {}'.format(kls))
            methods = [(name, mthd) for name, mthd in find_methods(kls)
                if name == hookname]
            class_obj = kls
            all_methods.extend(methods)
    logging.debug("All hook methods ({}) found in module {}: '{}'".format(
        len(all_methods), module, all_methods))
    if not len(all_methods):
        raise AttributeError('No hook class found.')
    elif len(all_methods) != 1:
        raise AttributeError('Found more than one hook_method in {}'
                             ' Expected only one per module.'.format(module))

    return class_obj

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

    Returns
    -------
    None
        Uses tools.pandas.testing; raises exceptions if not equal.

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

    Returns
    -------
    None
        Uses tools.pandas.testing; raises exceptions if not equal.

    '''
    from pandas.util.testing import assert_frame_equal
    # `sort` is deprecated; works in pandas 0.16.2; last worked in lamana 0.4.9
    # replaced `sort` with `sort_index` for pandas 0.17.1; backwards compatible
    return assert_frame_equal(
        df1.sort_index(axis=1), df2.sort_index(axis=1), check_names=True, **kwds
    )
    ##return assert_frame_equal(df1.sort(axis=1), df2.sort(axis=1),
    ##                          check_names=True, **kwds)


# TODO: Remove unused "my_file" and test
def read_csv_dir(dirpath, *args, **kwargs):
    '''Yield all csv files in a directory (REF 013).

    Notes
    -----
    Makes a generator containing DataFrames for all csv files in a directory.

    '''
    # Read all files in path
    for itemname in os.listdir(dirpath):                  # list files, folders, etc in a dir
        dir_item_path = os.path.join(dirpath, itemname)
        # TODO: How to test this if branch?
        if os.path.isfile(dir_item_path):
            # TODO: clean up and remove my_file; test affects
            ##with open(dir_item_path, 'r') as my_file:
            with open(dir_item_path, 'r'):
                # Assumes first column are indices
                file = pd.read_csv(dir_item_path, *args, index_col=0, **kwargs)
                yield file, dir_item_path


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

    # TODO: Need to complete; doesn't really do any sorting, just sets up the iterator.  Redo.
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


# def with_metaclass(meta, *bases):
#     '''Create a base class with a metaclass (REF 054).
#
#     Examples
#     --------
#     >>> class MyClassA(object):
#     ...     ___metaclass__ = Meta                          # python 2
#     >>> class MyClassB(metaclass=Meta): pass               # python 3
#
#     >>> # Py 2/3 equivalent metaclasses
#     >>> class MyClassC(with_metaclass(Meta, object)): pass # python 2/3
#     >>> type(MyClassA) is type(MyClassC)                   # python 2
#     True
#     >>> type(MyClassA) is type(MyClassC)                   # python 3
#     True
#
#     '''
#     return meta('MetaBase', bases, {})

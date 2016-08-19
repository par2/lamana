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
import sys
import logging
import tempfile
import inspect
import warnings
import collections as ct

import pandas as pd
import pandas.util.testing as pdt

# Avoid importing core modules; act as an aux for common code
from lamana.utils.config import DEFAULTPATH, PACKAGEPATH, EXTENSIONS


# Helpers
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


def reorder_featureinput(d, keys=None):
    '''Return an OrderedDict given a list of keys.

    Parameters
    ----------
    d : dict
        Any dict; expects a FeatureInput.
    keys : list of strings, default None
        Order of keys of a FeatureInput.

    See Also
    --------
    - covert_featureinput: make a dict of DataFrame values

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
        suffix = EXTENSIONS[0]
    elif suffix.endswith('xlsx'):
        suffix = EXTENSIONS[1]

    # Set Root/Source/Default Paths -------------------------------------------
    # The export folder is relative to the root (package) path
    # sourcepath = os.path.abspath(os.path.dirname(la.__file__))
    # packagepath = os.path.dirname(sourcepath)
    # if not os.path.isfile(os.path.join(packagepath, 'setup.py')):
    if not os.path.isfile(os.path.join(PACKAGEPATH, 'setup.py')):
        raise OSError(
            'Package root path location is not correct: {}'
            ' Verify working directory is ./lamana.'.format(packagepath)
        )
    # defaultpath = os.path.join(config.PACKAGEPATH, 'export')
    #
    # dirpath = defaultpath

    dirpath = DEFAULTPATH


    logging.debug('Root path: {}'.format(PACKAGEPATH))
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


def get_indicies(prim_df):
    '''Return a namedtuple comprising a dict of indicies parsed by layer.

    Grabs indicies of layers based on categories.

    Parameters
    ----------
    prim_df : DataFrame
        Expects a primitivate DataFrame at minimum.

    Notes
    -----
    The following categories list pandas index objects comprising the `indicies` dict:

    - interfaces: outside-in, peri-superficial indicies of all layers
    - disconts: outside-in, final indicies of all layers
    - internals: all indicies between interfaces and disconts
    - surfaces: first and last indicies, i.e. the top and bottom of the laminate
    - middles: central row (or two rows if even plies) proximal to the neutral axis
    - neutralaxis: the row representing the middle of an odd-ply laminate
    - firsts: top-down first (smallest) index per layer
    - lasts: top-down last (largest) index per layer

    Since the laminate is mirrored, the indicies are built conditionally based
    on tensile or compressive side and merged by set operations.  All indicies
    per category are presented; booleane tests are left to the user.

    Returns
    -------
    namedtuple
        Dict of panada Index objects, dict of booleans

    '''
    df = prim_df
    df['idx'] = df.index                                   # temp. index column for idxmin & idxmax
    n_rows = df.index.size
    nplies = df['layer'].max()
    p = n_rows/nplies
    groupby_layer = df.groupby('layer')
    length = len(df.index)

    # Conditionals
    conditions = {
        'tensile': df['side'] == 'Tens.',
        'compressive': df['side'] == 'Comp.',
        'middle': df['type'] == 'middle',
    }

    tensile = conditions.get('tensile')
    compressive = conditions.get('compressive')
    middle = conditions.get('middle')

    # Pandas Index Objects
    # Groupby layer, apply mix/max to indicies, store as pandas Index
    interf_tens_idx = pd.Index(df[tensile].groupby('layer')['idx'].idxmin())
    discont_tens_idx = pd.Index(df[tensile &~ middle].groupby('layer')['idx'].idxmax())
    discont_comp_idx = pd.Index(df[compressive &~ middle].groupby('layer')['idx'].idxmin())
    interf_comp_idx = pd.Index(df[compressive].groupby('layer')['idx'].idxmax())
    if nplies != 1:
        pseudo_middle_idx = pd.Index([discont_tens_idx.values[-1], discont_comp_idx.values[0]], name='idx')
    else:
        pseudo_middle_idx = pd.Index({})
    middle_idx = pd.Index([len(df.index) // 2], name='idx')
    internals_idx = df.index.difference(interf_tens_idx | discont_tens_idx | discont_comp_idx | interf_comp_idx)
    if p % 2 != 0: internals_idx = internals_idx.difference(middle_idx)
    surfaces_idx = pd.Index([0, length - 1], name='idx')
    firsts_idx = pd.Index(groupby_layer.first()['idx'], name='idx')
    lasts_idx = pd.Index(groupby_layer.last()['idx'], name='idx')

    # DataFrame indicies
    indicies = {
        'interfaces': interf_tens_idx.union(interf_comp_idx).sort_values(),
        'disconts': discont_tens_idx.union(discont_comp_idx).sort_values(),
        'internals': internals_idx,
        'surfaces': surfaces_idx,
        'firsts': firsts_idx,
        'lasts': lasts_idx,
    }

    if nplies % 2 == 0 or p % 2 == 0:
        indicies['middles'] = pseudo_middle_idx
        indicies['neutralaxis'] = pd.Index({})
    else:
        indicies['middles'] = middle_idx
        indicies['neutralaxis'] = middle_idx

    logging.debug('Indices: {}'.format(indicies))

    # Setup a namedtuple
    Indexer = ct.namedtuple('Indexer', 'indicies conditions')

    return Indexer(indicies=indicies, conditions=conditions)

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


## =============================================================================
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
            apple  orange  banana  blueberry
    amount      4       3       2          3

    '''
    cols = seq[:]                                          # copy so we don't mutate seq
    for x in df.columns:
        if x not in cols:
            cols.append(x)
    return df[cols]

    # NOTE: Seems even returning the dataframes takes about 8 ms
    #remaining = [seq.append(col) for col in df.columns if col not in seq]
    #seq.extend(remaining)
    #return df[seq]

def assertSeriesEqual(s1, s2, **kwds):
    '''Return True if two Series are equal (REF 014)?.

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
    ##from pandas.util.testing import assert_series_equal
    return pdt.assert_series_equal(s1, s2, **kwds)


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
    ##from pandas.util.testing import assert_frame_equal
    # `sort` is deprecated; works in pandas 0.16.2; last worked in lamana 0.4.9
    # replaced `sort` with `sort_index` for pandas 0.17.1; backwards compatible
    return pdt.assert_frame_equal(
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
    for itemname in os.listdir(dirpath):                   # list files, folders, etc in a dir
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
        string_, list_ = data                              # key, value pair
    #print(string_)

    # TODO: Need to complete; doesn't really do any sorting, just sets up the iterator.  Redo.
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def inspect_callers(x):
    '''Print who is calling a function (REF 058).'''
    callingframe = sys._getframe(1)
    print('My caller is the %r function in a %r class' % (
        callingframe.f_code.co_name,
        callingframe.f_locals['self'].__class__.__name__))

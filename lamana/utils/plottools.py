#------------------------------------------------------------------------------
'''Tools to assist in testing plotting outputs.'''
# Separated from tools.py since specific to troubleshooting output_ tests.


import re
import logging

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import lamana as la
from lamana.lt_exceptions import InputError


# Analyze Geometries ----------------------------------------------------------
# Token processing
def _get_duples(token):
    '''Return list of tuples given an outer or inner_i; (position, duple).

    If none found, return empty list.

    Parameters
    ----------
    token: str
        A string representation of a geometry token (outer, inner_i or middle);
        this is NOT a full geometry string.

    Returns
    -------
    list of tuples
        The duple location and string representation of all duples are contained
        in a list.  [(string position, duple), ...]

    Examples
    --------
    >>> _get_duples('(300,100)')                            # outer token
    [(0, '(300.0, 100.0)']
    >>> _get_duples('[100,(200.0,200),300]')                # inner_i token
    [(5, '(200.0,200)')]
    >>> _get_non_duples('[100,300]')                        # if non-duple, empty list
    []

    Raises
    ------
    InputError
        If full geometry string is passed in e.g. '400.0-[100.0,100.0]-800.0'.

    Notes
    -----
    Assumes tokens are valid.

    '''
    # TODO: Replace with an is_valid_token() method to improve robostness
    if '-' in token:
        raise InputError(
            "'-' found.  Please input a geometry token only, e.g."
            "outer, inner_i or middle string."
        )

    pattern = r'(\( *\d+\.*\d*\, *\d+\.*\d* *\))'          # duple; includes whitespace

    list_of_duples = []
    for match in re.finditer(pattern, token):
        pos = match.start()
        end = match.end()
        #print(pos, end)
        duple = token[pos:end]

        # Convert to float
        duple = duple.strip('()')
        duple = tuple(float(inner) for inner in duple.split(','))
        #print(duple)

        list_of_duples.append((pos, duple))
        logging.debug('Using _get_duple. position: {},'
                      ' duple: {} for string {}'.format(pos, duple, token))
    return list_of_duples
    # TODO: should probably return None if list is empty, or none found


def _get_non_duples(token):
    '''Return list of pure inner numbers (non-duples) given an inner_i or outer geo_string.

    If none found, return empty list.

    Parameters
    ----------
    token: str
        A string representation of a geometry token (outer, inner_i or middle);
        this is NOT a full geometry string.

    Examples
    --------
    >>> _get_non_duples('400')                             # outer token
    [(0, '400.0')]
    >>> _get_non_duples('[100,(200.0,200),300]')           # inner_i token
    [(1, '100.0'), (17, '300.0')]
    >>> _get_non_duples('[(200.0,200)]')                   # if duple, empty list
    []

    Returns
    -------
    list of tuples
        The duple location and string representation of all duples are contained
        in a list.  [(string position, duple), ...]

    Raises
    ------
    InputError
        If full geometry string is passed in e.g. '400.0-[100.0,100.0]-800.0'.

    Notes
    -----
    Assumes tokens are valid.

    '''
    # TODO: Replace with an is_valid_token() method to improve robostness
    if '-' in token:
        raise InputError(
            "'-' found.  Please input a geometry token only, e.g."
            "outer, inner_i or middle string."
        )

    # NOTE: adding tests may require refining the regex pattern
    # Assume only duples and inners in the inner_i string
    pattern = r'(?<![(\d+])(\d+\.*\d+ *\,*?)(?![\d\.)])'   # inners only; exlude duples
    # Test string: '[100.0, (200.0, 200.0), 300, (100.0,300),(100,300.0)]'

    list_of_non_duples = []
    for match in re.finditer(pattern, token):
        pos = match.start()
        end = match.end()
        #print(pos, end)
        layer = float(token[pos:end])                     # convert to float
        list_of_non_duples.append((pos, layer))
        logging.debug('Using _get_nonduples. position: {},'
                      ' layer: {} for string {}'.format(pos, layer, token))
    return list_of_non_duples
    # TODO: should probably return None if list is empty, or none found


def _get_outer(token):
    '''Return a float or tuple of the outer.

    Parameters
    ----------
    token : str
        String representations of outer layer_ ints, floats and duples
        e.g '400', '400.0', '(300.0, 100)'

    Notes
    -----
    Parse the outer token; NOT a full geometry string.  Get either:
    1. a float (position, outer) or
    2. tuple (position, outer)

    Examples
    --------
    >>> _get_outer('400-[200]-800')
    400.0
    >>> _get_outer('(300,100)-[200]-800')
    (300.0, 100.0)

    Checks if duple. If not, is ignored.  Float conversions occur internally.

    '''
    duples = _get_duples(token)
    non_duples = _get_non_duples(token)
    #print(non_duples)
    try:
        # Assumes if isinstance(non_duples[0][1], float)
        return non_duples[0][1]
    except(IndexError):
        # Assumes if isinstance(duples[0][1], tuple)
        return duples[0][1]


def _get_inner_i(token):
    '''Return a list of converted inners including duples.

    Parameters
    ----------
    token : str
        String representation of inner_i layer_ ints, floats and duples
        e.g. '[100,(200.0,200),300]'

    Examples
    --------
    >>> _get_inner_i('[100,(200.0,200),300]')
    [100.0, (200.0, 200.0), 300.0]

    Notes
    -----
    Parse the inner_i.  Get two lists:
    1. float(s) (position, inner(s))
    2. tuple(s) (position, duple(s)). Then sort positions of coverted inner
    components into a single list.

    Float conversions occur internally.

    '''
    duples = _get_duples(token)
    non_duples = _get_non_duples(token)

    ordered_inner_i = sorted(duples + non_duples)
    inner_i = [inner for i, inner in ordered_inner_i]

    return inner_i


def _get_middle(token):
    '''Return float given a string possibly including 'S'.

    Parameters
    ----------
    token : str
        String representation of middle layer_ ints, floats symmetric
        e.g. '800', '800.0', '400S'

    Examples
    --------
    >>> _get_middle('800.0')
    800.0
    >>> _get_middle('400S')
    800.0

    Notes
    -----
    The symmetry flag 'S' indicates doubling the numeric value.

    '''
    if 'S' in token:
        return 2 * float(token[:-1])
    else:
        return float(token)


# TODO: Performance comparison of this function with Stack.decode_geometry().
# Stack assembly
def _unfold_geometry(outer, inner_i, middle):
    '''Return an list of unfolded, stacking sequence given converted geo_string tokens.

    Parameters
    ----------
    outer : str
        The outer token of a parsed geometry string, split by '-'.  May contain
        a string representation of an int, float or duple.
    inner_i : str
        The inner_i token of a parsed geometry string, split by '-'.  May contain
        string representations of an ints, floats and/or duples.
    middle: str
        The middle token of a parsed geometry string, split by '-'.  Must contain
        a string representation of an float.  Use _get_middle().

    Notes
    -----
    Unlike the Stack() parsing functions that decode Geometry objects, this function
    decodes geometry strings. This approach may have performance benefits.

    The workflow for creating an ordered stack sequence is manual, contained in a list:
       outer1 + inner_i + middle + inner_i(reversed) + outer2

    The outer is checked for a duple.  If one is found, the tensile entry is parsed.
    The inner_i is forward iterated, parsing only tensile inners if duples found.
    Next the middle is added to the list, pre-processed, stripped of symmetry flag.
    The inner_i is iterated over a reversed list.
    The final outer is checked for a duple.  If one is found, compressive entry is parsed.

    See Also
    --------
    - constructs.Stack.decode_geometry(): similar methodology applied to Geometry objects.
    - _get_outer(), _get_inner_i(), _get_middle(): helper functions for preparing tokens.

    '''
    # General Abraction for handling duples and non-dulples in outer and inner_i
    # Attempt to unwrap duples in inner_i
    stack_seq = []
    if isinstance(outer, tuple):
        stack_seq.append(outer[0])
    else:
        stack_seq.append(outer)

    # Forward iter
    for inner in inner_i:
        if isinstance(inner, tuple):
            stack_seq.append(inner[0])
        else:
            stack_seq.append(inner)

    stack_seq.append(middle)

    # "Reverse" iter
    for inner in inner_i[::-1]:
        if isinstance(inner, tuple):
            stack_seq.append(inner[1])
        else:
            stack_seq.append(inner)

    if isinstance(outer, tuple):
        stack_seq.append(outer[1])
    else:
        stack_seq.append(outer)

    # Algorithms
    ## For outer duples only
    #stack_seq = outer[0] + inner_i + middle + inner_i_r + outer[1]

    ## For non-duples
    ##inner_i_r = inner_i[::-1]                           # non-duples only
    ##stack_seq = outer + inner_i + middle + inner_i_r + outer
    return stack_seq


# Main function
def analyze_geostring(geo_string):
    '''Return a tuple of nplies, thickness and order given a geo_string.'''
    # TODO: _to_gen_convention() needs to handle duples
    # Pre-process geo_string
    conv_geostring = la.input_.Geometry._to_gen_convention(geo_string)
    tokens = conv_geostring.split('-')
    #tokens = geo_string.split('-')                         # beta; allow unconventional

    # Token processing
    outer = _get_outer(tokens[0])
    inner_i = _get_inner_i(tokens[1])
    middle = _get_middle(tokens[2])

    # Attributes
    order = _unfold_geometry(outer, inner_i, middle)       # stack assembly
    nplies = len(order)
    t_total = sum(order) / 1000.0

    return nplies, t_total, order


# Analyze Plots --------------------------------------------------------------
def extract_plot_LM_xy(cases, normalized=True, extrema=False):
    '''Return tuples of xy data from case plots and LaminateModel DataFrames.

    Parameters
    ----------
    cases : Cases-like object
        One or more cases contained in an iterable, e.g. laminator or Cases
        objects.  Cases contain the critical LamainateModels from which to plot
        lines and later pull DataFrame data.
    normalized : bool, default: True
        Passed to _distriplot to pull df data from `k` column; else uses `d(m)` column.
    extrema : bool, default: False
        Passed to _distribplot.  If True, uses only two datapoints/layer, i.e.
        "interface" and "discont."

    Returns
    -------
    tuple
        A tuple of two lists: line plot and df data.  These lists represent extracted
        xy-data for all cases.  Inside the lists are tuples of listed x, y data.

    See Also
    --------
    - TestDistribplotLines: uses 1st and 2nd tuples as actual, expected data

    Examples
    --------
    >>> # 2 cases of size 3; assumes default loading parameters and material properties
    >>> cases = ut.laminator(['400-200-800', '400-400-400', '100-100-100'], ps=[3, 4])
    >>> extract_plot_LM_xy(cases)
    # [<(lists of x plot data, list of y plot data), (lists of x df data, list of y df data)>]

    '''
    for i, case in enumerate(cases.values()):
        fig, ax = plt.subplots()
        plot = la.output_._distribplot(
            case.LMs, normalized=normalized, extrema=extrema, ax=ax
        )
        #print(plot)

        # Extract plot data from lines; contain lines per case
        line_cases = []
        for line in plot.lines:
            xs, ys = line.get_data()
            #line_cases.append(zip(xs.tolist(), ys.tolist()))
            line_cases.append((xs.tolist(), ys.tolist()))
        logging.debug('Case: {}, Plot points per line | xs, ys: {}'.format(i, line_cases))

        # Extract data from LaminateModel; only
        df_cases = []
        for LM in case.LMs:
            df = LM.LMFrame
            condition = (df['label'] == 'interface') | (df['label'] == 'discont.')
            df_xs = df[condition].ix[:, -1]
            if not extrema:
                df_xs = df.ix[:, -1]
            if normalized:
                df_ys = df[condition]['k']
                if not extrema:
                    df_ys = df['k']
            elif not normalized:
                df_ys = df[condition]['d(m)']
                if not extrema:
                    df_ys = df['d(m)']
            #df_cases.append(zip(df_xs.tolist(), df_ys.tolist()))
            df_cases.append((df_xs.tolist(), df_ys.tolist()))
        logging.debug('Case {}, LaminateModel data | df_xs, df_ys: {}'.format(i, df_cases))

        plt.close()

    return line_cases, df_cases


#def analyze_matprops():
#    ''''Return int of number of materials.'''
#    pass


#def analyze_colors():
#    ''''Return int of number of materials.'''
#    pass


def has_annotations(texts):
    '''Return True if at least annotation is found.

    Parameters
    ----------
    texts : list
        Contains matplolib plotting objects.

    See Also
    --------
    - test_distribplot_annotate#: used to verify annotations on text.

    '''
    for text in texts:
        # Relies on annotations to be Annotation objects
        if isinstance(text, mpl.text.Annotation):
            return True
    return False

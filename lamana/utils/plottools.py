#------------------------------------------------------------------------------
'''Tools to assist in testing plotting outputs.'''
# Separated from tools.py since specific to troubleshooting output_ tests.


import re
import logging

import lamana as la
#import collections as ct
#import itertools as it


# Analyze Geometries ----------------------------------------------------------
def _get_duples(geo_string):
    '''Return list of tuples given an outer or inner_i; (position, duple).

    If none found, return empty list.

    Parameters
    ----------
    geo_string: str
        Pure geo_string of General Convention, e.g. '400.0-[100.0,100.0]-800.0'.

    Examples
    --------
    >>> _get_duples('[100,(200.0,200),300]')
    [(5, '(200.0,200)')]
    >>> _get_non_duples('[100,300]'')                       # if non-duple, empty list
    []

    Returns
    -------
    list of tuples
        [(string position, duple), ...]

    '''
    pattern = r'(\( *\d+\.*\d*\, *\d+\.*\d* *\))'          # duple; includes whitespace

    list_of_duples = []
    for match in re.finditer(pattern, geo_string):
        pos = match.start()
        end = match.end()
        #print(pos, end)
        duple = geo_string[pos:end]

        # Convert to float
        duple = duple.strip('()')
        duple = tuple(float(inner) for inner in duple.split(','))
        #print(duple)

        list_of_duples.append((pos, duple))
        logging.debug('Using _get_duple. position: {},'
                      ' duple: {} for string {}'.format(pos, duple, geo_string))
    return list_of_duples


def _get_non_duples(geo_string):
    '''Return list of pure inner numbers (non-duples) given an inner_i or outer geo_string.

    If none found, return empty list.

    Parameters
    ----------
    geo_string: str
        Pure geo_string of General Convention, e.g. '400.0-[100.0,100.0]-800.0'.

    Examples
    --------
    >>> _get_non_duples('[100,(200.0,200),300]')
    [(1, '100.0'), (17, '300.0')]
    >>> _get_non_duples('[(200.0,200)]')                   # if duple, empty list
    []

    Returns
    -------
    list of tuples
        [(string position, duple), ...]

    '''
    # NOTE: adding tests may require refining the regex pattern
    # Assume only duples and inners in the inner_i string
    pattern = r'(?<![(\d+])(\d+\.*\d+ *\,*?)(?![\d\.)])'   # inners only; exlude duples
    # Test string: '[100.0, (200.0, 200.0), 300, (100.0,300),(100,300.0)]'

    list_of_non_duples = []
    for match in re.finditer(pattern, geo_string):
        pos = match.start()
        end = match.end()
        #print(pos, end)
        layer = float(geo_string[pos:end])                 # convert to float
        list_of_non_duples.append((pos, layer))
        logging.debug('Using _get_nonduples. position: {},'
                      ' layer: {} for string {}'.format(pos, layer, geo_string))
    return list_of_non_duples


def _get_outer(token):
    '''Return a float or tuple of the outer.

    Parameters
    ----------
    token : str
        String representations of ints, floats and duples
        e.g '400', '400.0', '(300.0, 100)'

    Notes
    -----
    Parse the outer.  Get either:
    1. a float (position, outer) or
    2. tuple (position, outer)

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
        String representations of inner_i ints, floats and duples
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
        String representations of middle ints, floats symmetric
        e.g. '800', '800.0', '400S'

    Notes
    -----
    The symmetry flag 'S' indicates doubling the numeric value.

    '''
    if 'S' in token:
        return 2 * float(token[:-1])
    else:
        return float(token)


# TODO: Performance comparison of this function with Stack.decode_geometry().
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
       outer1 + inner_i1 + middle + inner_i (reversed) + outer2

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


def analyze_geostring(geo_string):
    '''Return a tuple of nplies, thickness and order given a geo_string.'''
    # TODO: _to_gen_convention() needs to handle duples
    conv_geostring = la.input_.Geometry._to_gen_convention(geo_string)
    tokens = conv_geostring.split('-')
    #tokens = geo_string.split('-')                         # beta; allow unconventional
    outer = _get_outer(tokens[0])
    inner_i = _get_inner_i(tokens[1])
    middle = _get_middle(tokens[2])

    order = _unfold_geometry(outer, inner_i, middle)
    nplies = len(order)
    t_total = sum(order) / 1000.0

    return nplies, t_total, order


def analyze_matprops():
    ''''Return int of number of materials.'''
    pass


def extract_patches():
    '''Return dict of layered patch from a plot with coordinates for each patch.'''
    pass

# -----------------------------------------------------------------------------
'''Classes and functions for handling user inputs.'''
# Geometry(): parse user input geometry strings to a tuple of floats (and lists/str)
# BaseDefaults(): library of general geometry defaults; subclassed by the user.
# flake8 input_.py --ignore=E265, E501, N803, N806, N802, N813, E133

import re
import logging
import itertools as it
import collections as ct

import pandas as pd

from .lt_exceptions import FormatError
from .utils import tools as ut


# =============================================================================
# USER INPUT ------------------------------------------------------------------
# =============================================================================
# Parses informations and generates User Input objects, i.e. Geometry()


def tokenize_geostring(geo_string):
    '''Return a tuple of tokens; outer, inner_i, middle tokens.'''
    # Convert to General Convention
    # TODO: Add handling of duples into _to_gen_convention first
    # For now, assume strings are formated correctly
    #g_conv = la.input_.Geometry._to_gen_convention(geo_string)

    # Check is_valid(); if not attempt to_gen_convention

    # Prepare string
    geo_string = geo_string.upper()                        # auto uppercase
    geo_string = geo_string.replace(' ','')                # auto whitespace strip

    # Return tokens
    tokens = geo_string.split('-')
    return tokens


class Geometry(object):
    '''Parse input geometry string into floats.

    When a single (or a list of) geometry string(s) is passed to the
    `lamana.distributions.Case.apply()` method, this class parses those strings
    into (outer, [inner], middle, 'S') format'; 'S' is optional.

    Here are examples of conventions used to write geometry strings:

    - General: outer-[inner_i]-middle
    - Short-hand: outer-inner-middle

    Formatted in General Convention, a converted namedtuple of the geometry
    is returned.  Examples of GeometryTuples:

    - (400.0, [200.0], 800.0)                              # multi-ply
    - (400.0, [200.0], 800.0, 'S')                         # multi-ply, symmetric
    - (400.0, [100.0, 100.0], 800.0)                       # multi-ply, [inner_i]

    Parameters
    ----------
    geo_input : str or tupled str
        Geometry string of layer thicknesses in a laminate.

    Attributes
    ----------
    total
    total_middle
    total_inner
    total_inner_i
    total_outer
    is_symmetric
    namedtuple : namedtuple
        A GeometryTuple in General Convention, e.g. (400.0, [200.0], 800.0, 'S').
    geometry : list
        The converted and parsed geometry string.
    middle : float
        Middle layer thickness.
    inner : list of floats
        Inner layer thicknesses in micrometers.
    outer : float
        Outer layer thickness.
    string : str
        The input geometry string converted to General Convention format.

    Examples
    --------
    >>> g1 = ('0-0-2000')                                  # Monolith
    >>> g2 = ('1000-0-0')                                  # Bilayer
    >>> g3 = ('600-0-800')                                 # Trilayer
    >>> g4 = ('500-500-0')                                 # 4-ply
    >>> g5 = ('400-200-800')                               # Short-hand; <= 5-ply
    >>> g6 = ('400-200-400S')                              # Symmetric
    >>> g7 = ('400-[200]-800')                             # Gen. convention; 5-ply
    >>> g8 = ('400-[100,100]-800')                         # Gen. convention; 7-plys
    >>> la.input_.Geometry(g5)
    Geometry object (400.0-[200.0]-800.0)

    '''

    def __init__(self, geo_input):
        '''Ideally a want to call Geometry and get namedtuple auto; return self?'''

        # TODO: Consolidate into namedtuple or self
        # TODO: rename geometrytuple
        self.string = self.__class__._to_gen_convention(geo_input)
        self.namedtuple = self._parse_geometry(self.string)# a namedtuple; see collections lib
        self.geometry = self._parse_geometry(self.string)  # a namedtuple; see collections lib

##        self.namedtuple = self._parse_geometry(geo_input)  # a namedtuple; see collections lib
##        self.geometry = self._parse_geometry(geo_input)    # a namedtuple; see collections lib
        self.middle = self.geometry.middle                 # attributes from namedtuple; symmetric sensitive
        self.inner = self.geometry.inner
        self.outer = self.geometry.outer

##        self.string = self.__class__._to_gen_convention(geo_input)

        # Private attribute used for set comparisons and hashing
        # TODO: should we pass in geo_string instead of geo_inputs?
        self._geometry_hash = self._parse_geometry(geo_input, hash_=True)

    def __str__(self):
        '''Returns trimmed geometry string.'''
        return self.string

    def __repr__(self):                                    # for object calls
        '''Returns Geometry object string.'''
        return '{} object ({})'.format(self.__class__.__name__, self.string)

    def __eq__(self, other):
        '''Compare GeometryTuples.'''
        if isinstance(other, self.__class__):
            #print(self.__dict__)
            #print(other.__dict__)
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        '''Allow set comparisons.

        The only required property for a hash is that objects which equally
        compare have the same hash value (REF 035).  `self.__dict__` is unhashable
        due to the inner list (lists are mutable, thus unhashable).  So a copy is
        made called `_geometry_hash` of GeometryTuple where the inner value is
        tupled instead.

        '''
        return hash(self._geometry_hash)
        #return hash(tuple(sorted(self.__dict__.items())))
        #return hash(self._geo_string)

    def _parse_geometry(self, geo_string, hash_=False):
        '''Return a namedtuple of outer-inner-middle geometry values.

        Per General Convention, a GeometryTuple has floats and an inner list.
        Checks for symmetry, handles inner list, then makes the GeometryTuple.

        Also can create a hashable version of GeometryTuple; tuple instead of
        list for inner_i.

        Parameters
        ---------
        geo_string : tupled str or str
            outer-inner-middle values or outer-[inner]-middle values;
            formatted in general convention (0.4.11).

        Returns
        -------
        namedtuple of mixed types
            GeometryTuple: numeric values converted to floats; (outer, [inner], middle,'S?')
        '''

        def check_symmetry(last):
            '''Yield float or str if 'S' is in the last token of the geometry string.

            Examples
            --------
            >>> [i for i in check_symmetry('400S')]
            [400.0, 'S']
            >>> [i for i in check_symmetry('400')]
            [400.0]
            '''
            if last.endswith('S'):
                # Converts last '400S' to [400.0,'S']
                #print(type(last))
                number = float(last[:-1])
                letter = last[-1]
                yield number
                yield letter
            else:
                # Converts last '400' to [400.0]
                yield float(last)

        # Inner Parsing
        def parse_inner(inside):
            '''Yield values from the inner list of a geometry string.

            Also parses inner_i (if multiple inners are found) str to floats.
            This is later converted to a list of inner_i, as required by LPEP 001.01.

            Examples
            --------
            >>> list(parse_inner('[100,100]'))
            [100.0, 100.0]
            >>> list(parse_inner('[200]'))
            [200.0]
            >>> list(parse_inner('200'))
            [200.0]

            Raises
            ------
            TypeError
                If a non-string is passed in for the geo_string arg.
            FormatError
                If the parsed geo string is less than 3 tokens.

            '''
            if inside.startswith('['):
                if ',' in inside:
                    # Convert inside string '[100,100]' to [100.0,100.0]
                    for item in inside[1:-1].split(','):
                        yield float(item)
                else:
                    # Convert inside string '[200]' to [200.0]
                    converted = inside[1:-1]               # excludes bracket strings
                    #print(converted)
                    yield float(converted)
            else:
                # Convert insde string '200' to [200] if brackets aren't found
                yield float(inside)

        # Convert Input String
        def _make_GeometryTuple(tokens, hashable=False):
            '''Return a namedtuple of floats representing geometry thicknesses.'''
            outer = float(tokens[0])
            inner_hash = tuple(parse_inner(tokens[1]))     # tupled inner for hash()
            inner = list(parse_inner(tokens[1]))           # complies w LPEP 001.01
            middle = tuple(check_symmetry(tokens[-1]))

            '''Should warn the object is symmetric though.'''
            if 'S' not in geo_string:
                GeometryTuple = ct.namedtuple(
                    'GeometryTuple', ['outer', 'inner', 'middle'])
                if hashable:
                    return GeometryTuple(outer, inner_hash, middle[0])
                return GeometryTuple(outer, inner, middle[0])
            else:
                GeometryTuple = ct.namedtuple(
                    'GeometryTuple', ['outer', 'inner', 'middle', 'symmetric'])
                if hashable:
                    return GeometryTuple(outer, inner_hash, middle[0], middle[-1])
                return GeometryTuple(outer, inner, middle[0], middle[-1])

        # Create --------------------------------------------------------------
        '''Replace with try-except block.'''
        # Tests geo_string is a string
        # TODO: change to geo_string
        tokens = geo_string.split('-')
        # TODO: Find another name for hash_ which is a bool'''
        # Gets hash_ bool passed in from parsed_geometry
        return _make_GeometryTuple(tokens, hashable=hash_)

        ##tokens = geo_input.split('-')
        ##if not isinstance(geo_input, str):
            ##raise TypeError("Cannot parse input type.  Supported types: str")
        ##elif len(tokens) < 3:
                # TODO: Replace with custom exception
                ##raise exc.FormatError(
                ##    "Input token is too short. Supported geometry string format:"
                ##    " 'outer-[inner_i]-middle'"
                ##)
        ##else:
            # TODO: Find another name for hash_ which is a bool'''
            # Gets hash_ bool from parsed_geometry
            ##return _make_GeometryTuple(tokens, hashable=hash_)

    @classmethod
    def _to_gen_convention(cls, geo_input):
        '''Return a geometry string converted to general convention.

        Handles string-validation Exceptions.
        '''
        try:
            # Check geo_input is a string
            tokens = geo_input.split('-')

            # Check for letters in the input
            any_letters = re.compile('[a-zA-Z]', re.IGNORECASE)
            if any_letters.search(geo_input):
                all_letters = any_letters.findall(geo_input)
                # Raise if more than one letter in the Input
                if len(all_letters) > 1:
                    ##raise exc.FormatError(
                    raise FormatError(
                        "Input must not contain more than one letter, 'S'."
                    )
                # Raise if 's' or 'S' is not the letter
                if not set(all_letters).issubset(['s', 'S']):
                    ##raise exc.FormatError(
                    raise FormatError(
                        "Invalid letter detected; only 'S' allowed."
                    )
            if len(tokens) < 3:
                ##raise exc.FormatError(
                raise FormatError(
                    "Input token is too short. Supported geometry string format:"
                    " 'outer-[inner_i]-middle'"
                )
            if len(tokens) > 3:
                ##raise exc.FormatError(
                raise FormatError(
                    "Input token is too long. Supported geometry string format:"
                    " 'outer-[inner_i]-middle'"
                )
        except(AttributeError):
            # Needed in general and for distributions.Cases()
            raise TypeError(
                "Cannot parse input type.  Supported types: str. {} given.".format(geo_input)
            )

        first = tokens[0]
        inside = tokens[1]
        last = tokens[-1]
        #print(inside)

        # Convert strings to general convention
        first = str(float(first))

        if inside.startswith('['):
            # Convert inside string '[100,100]' to '100.0,100.0'
            if ',' in inside:
                converted = [str(float(item)) for item in inside[1:-1].split(',')]
                inside = ','.join(converted)
            else:
                # Convert inside string '[200]' to '200.0'
                inside = str(float(inside[1:-1]))
        elif not inside.startswith('['):
            # Convert inside string '200' to 200.0 if brackets aren't found
            inside = str(float(inside))
        # Always add brackets
        inside = ''.join(['[', inside, ']'])
        #print('Converting geometry string to general convention.')

        if last.endswith('S'):
            last = str(float(last[:-1]))
            last = ''.join([last, 'S'])
        elif not last.endswith('S'):
            last = str(float(last))

        geo_string = '-'.join([first, inside, last])
        return geo_string

    # API --------------------------------------------------------------------
    # DEPRECATED: itotal() in 0.4.3d
    @property
    def total(self):
        '''Calculate total thickness for laminates using any convention.'''
        if self.is_symmetric:
            factor = 2
        else:
            factor = 1
        return 2 * self.outer + 2 * sum(self.inner) + factor * self.middle

    @property
    def total_middle(self):
        '''Calculate total thickness for middle lamina using any convention.'''
        if self.is_symmetric:
            return 2 * self.middle
        else:
            return self.middle

    @property
    def total_inner(self):
        '''Calculate total thickness for inner lamina using any convention.'''
        return 2 * sum(self.inner)

    @property
    def total_inner_i(self):
        '''Calculate total thickness for the ith inner lamina.'''
        result = [inner_i * 2 for inner_i in self.inner]
        return result

    @property
    def total_outer(self):
        '''Calculate total thickness for outer lamina using any convention.'''
        return 2 * self.outer

    @property
    def is_symmetric(self):
        '''Return True if 'S' convention is used.

        Examples
        --------
        >>> g5 = ('400-200-800')                           # Short-hand use; <= 5-ply
        >>> g6 = ('400-200-400S')                          # Symmetric
        >>> for geo in [g5, g6]
        ...     geo.is_symmetric
        False True
        '''
        return 'S' in self.geometry


# -----------------------------------------------------------------------------
# UTILITY
# -----------------------------------------------------------------------------
# Supplies basic dicts and methods by supplying custom case-building information.

class BaseDefaults(object):
    '''Common geometry strings, objects and methods for building defaults.

    Allows quick access to default parameters.  It is useful for consistent testing.

    Users can subclass geometric defaults and add specific parameters
    (loading, material, geometric, etc.) to improve start-up and reduce
    redundant code. Here are some objects that can be found in and subclassed
    from this base class:

    - Base : Default geometry strings
    - Base : Default Geometry objects
    - Subclass : Default material and geometric/loading parameters
    - Subclass : Default FeatureInputs

    Defaults are maintained in two dicts:

    - `geo_inputs` : A dict of standard geometry strings and special groups.
    - `Geo_objects` : A dict of converted geo_inputs into Geometry objects.

    Methods
    -------
    get_FeatureInput(Geometry, load_params=None, mat_props=None, **kwargs)
        Return a dict of the basic FeatureInput object; subclass in a model.
    get_materials(mat_props)
        Return a list of materials in order from a mat_props dict or DataFrame.
    generate(selection=None, geo_inputs=False)
        Yield a generator of selected geometries.

    Notes
    -----
    DEV: add entries to the Default dicts.  Removing existing dict entries or
    "trimming" the Default dicts will break tests (not recommended).

    Material properties, geometric/loading parameters and FeatureInput cannot be
    generalized and are thus left to the author to define in their custom defaults
    subclass.  The best place to customize this is in a custom models module.

    Examples
    --------
    Base: Idiomatic instantiation of Base Defaults

    >>> bdft = BaseDefaults()                              # instantiation

    Access a set of built-in geometry strings

    >>> bdft.geos_most                                     # list of geometry Input strings
    [('0-0-2000'), ('1000-0-0'), ('600-0-800'),
     ('500-500-0'), ('400-200-800')]

    Access a set of built-in Geometry objects (converted geometry strings)

    >>> bdft.Geos_simple                                   # list of Geometry objects
    [<Geometry object ('0-0-2000')>,
     <Geometry object ('1000-0-0')>,
     <Geometry object '600-0-800')>,
     <Geometry object ('500-500-0')>,]

    Subclass: Idiomatic import and instantiation of custom Defaults (see Wilson_LT ex.)

    >>> from lamana.models import Wilson_LT as wlt         # user-implemmented Defaults
    >>> dft = wlt.Defaults()                               # subclassed from BaseDefaults

    Access Defaults loading parameters, material properties and FeatureInput

    >>> dft.load_params
    {'R': 12e-3, 'a': 7.5e-3, 'p': 1, 'P_a': 1, 'r': 2e-4}
    >>> dft.mat_props
    {'HA': [5.2e10, 0.25], 'PSu': [2.7e9, 0.33],}
    >>> dft.FeatureInput
    {'Geometry': '400-[200]-800',
     'Geometric': {'R' : 12e-3, 'a' : 7.5e-3, 'p' : 1, 'P_a' : 1, 'r' : 2e-4,},
     'Materials': {'HA' : [5.2e10, 0.25], 'PSu' : [2.7e9, 0.33],},
     'Custom': None,
     'Model': Wilson_LT,
     'Globals': None,}

    Reassign Defaults instances (e.g. R, p)

    >>> dft.load_params = {
    ...     'R': 50e-3, 'a': 7.5e-3, 'p' : 5,
    ...     'P_a': 1, 'r': 2e-4,
    ... }
    >>> dft.load_params
    {'R': 50e-3, 'a': 7.5e-3, 'p' : 5, 'P_a': 1, 'r': 2e-4,}

    '''
    def __init__(self):

        # TODO: Add BaseDefaults attributes to claim the namespace
        # i.e, load_params = None, mat_props = None, FeatureInput = None
        # Consider this architexture rather than leave the author with oneous to def vars

        # Geometry Input Strings
        # DEV: Add geometry strings here.  Do not remove.
        self.geo_inputs = {
            '1-ply': ['0-0-2000', '0-0-1000'],
            '2-ply': ['1000-0-0'],
            '3-ply': ['600-0-800', '600-0-400S'],
            '4-ply': ['500-500-0', '400-[200]-0'],
            '5-ply': ['400-200-800', '400-[200]-800', '400-200-400S'],
            '6-ply': ['400-[100,100]-0', '500-[250,250]-0'],
            '7-ply': ['400-[100,100]-800', '400-[100,100]-400S'],
            '9-ply': ['400-[100,100,100]-800'],
            '10-ply': ['500-[50,50,50,50]-0'],
            '11-ply': ['400-[100,100,100,100]-800'],
            '13-ply': ['400-[100,100,100,100,100]-800'],
            }

        # To add keys, first add logic to automate appending dict_ in groupify
        # This should add a key to geo_inputs.  Geo_objects will auto-mimic this logic.
        # Then define attributes (below) of geo_inputs and Geo_objects for API access.
        self.geo_inputs = self._groupify_dict(self.geo_inputs)     # needed for next line
        self.Geo_objects = self._groupify_dict(self.geo_inputs, Geo_obj=True)

        # ATTRIBUTES ----------------------------------------------------------
        # Quick access to geometry related groups
        # Geometry Input String Attributes
        self.geos_even = self.geo_inputs['even']
        self.geos_odd = self.geo_inputs['odd']
        self.geos_most = self.geo_inputs['most']
        self.geos_special = self.geo_inputs['special']
        self.geos_full = self.geo_inputs['full']
        self.geos_full2 = self.geo_inputs['full2']
        self.geos_full3 = self.geo_inputs['full3']
        self.geos_all = self.geo_inputs['all']
        self.geos_standard = self.geo_inputs['standard']
        self.geos_symmetric = self.geo_inputs['symmetric']
        self.geos_inner_i = self.geo_inputs['inner_i']
        self.geos_general = self.geo_inputs['general conv.']
        self.geos_unconventional = self.geo_inputs['unconventional']
        self.geos_dissimilar = self.geo_inputs['dissimilar']
        self.geos_sample = self.geo_inputs['sample']

        # TODO: must be way to automate these assignments; reduce redundancy.
        # Geometry Object Attributes
        self.Geos_even = self.Geo_objects['even']
        self.Geos_odd = self.Geo_objects['odd']
        self.Geos_most = self.Geo_objects['most']
        self.Geos_special = self.Geo_objects['special']
        self.Geos_full = self.Geo_objects['full']
        self.Geos_full2 = self.Geo_objects['full2']
        self.Geos_full3 = self.Geo_objects['full3']
        self.Geos_all = self.Geo_objects['all']
        self.Geos_standard = self.Geo_objects['standard']
        self.Geos_symmetric = self.Geo_objects['symmetric']
        self.Geos_inner_i = self.Geo_objects['inner_i']
        self.Geos_general = self.Geo_objects['general conv.']
        self.Geos_unconventional = self.Geo_objects['unconventional']
        self.Geos_dissimilar = self.Geo_objects['dissimilar']
        self.geos_sample = self.geo_inputs['sample']

    @classmethod
    def _extract_number(cls, string):
        '''Return integer of numerics found in a string, i.e. '5-ply' --> 5.'''
        for s in string.split('-'):                           # separate ply from number
            if s.isdigit():
                #print(s)
                return int(s)

    @classmethod
    def _groupify_dict(cls, dict_default, Geo_obj=False):
        '''Return a dict of logical groups.

        This method is useful for automating groupings; new ply keys or
        values can be added to the dict with relative ease.

        Parameters
        ----------
        dict_default : dict
            Given a dict of "plies (str):geo strings (list)", key-value pairs.
        Geo_obj : bool; Default False
            True if a returned dict is desired of Geometry objects.

        Returns
        -------
        dict
            Keys of specified groups.

        See Also
        --------
        utils.tools.natural_sort : order dict.items() in loops; needed for tests

        Notes
        -----
        This methods requires:

        - name keys by number of plies; e.g. '14-ply' (human sorts)
        - add values as a list of strings
        - add to the geo_inputs dict (Geo_objects mimics and updates automatically)

        '''
        d = ct.defaultdict(list)
        dict_ = dict_default.copy()
        # Sort dict naturally to help order the list values
        ##for k,v in sorted(dict_.items(), key=natural_sort):
        for k, v in sorted(dict_.items(), key=ut.natural_sort):
            # Prepare k, v
            num = cls._extract_number(k)
            if Geo_obj:                                    # build Geo_objects simul.
                # G = la.input_.Geometry
                G = Geometry
                v = [G(geo_string) for geo_string in v]
                dict_[k] = v                               # overwrite original dict_
            # Group keys
            if (num is not None) and (num % 2 == 0):
                #print(num)
                d['even'].extend(v)
            elif (num is not None) and (num % 2 != 0):
                d['odd'].extend(v)
            if (num is not None) and (num <= 5):
                d['most'].append(v[0])
            if (num is not None) and (num < 5):
                d['special'].append(v[0])
            if (num is not None) and (num == 5):
                d['standard'].append(v[1])
            if (num is not None) and (num <= 9):
                #print(num)
                d['full'].append(v[0])
            if num is not None:
                d['all'].extend(v)
            # Inside strings
            if not Geo_obj:
                for geo_string in v:
                    if 'S' in geo_string:
                        #print(geo_string)
                        d['symmetric'].append(geo_string)
                    if ('[' in geo_string) and (',' in geo_string):
                        d['inner_i'].append(geo_string)
                    if '[' in geo_string:
                        #print(geo_string)
                        d['general conv.'].append(geo_string)
                    # TODO: refactor logic; test_BaseDefaults_unconventional1() should cover this
                    if '[' not in geo_string:
                        d['unconventional'].append(geo_string)

        dict_.update(d)

        # Post-fix groups; manual
        # Note, manually adding strings here (vs. __init__) won't be grouped in Geo_object
        # You must add to geo_input; the Geo_obj will be auto-made.
        if Geo_obj:
            '''Make smarter; look for unequal inners then make dissimilar.'''
            dict_['dissimilar'] = [G('400-[150,50]-800'), G('400-[25,125,50]-800')]
        else:
            dict_['dissimilar'] = ['400-[150,50]-800', '400-[25,125,50]-800', ]
        # Dict_references are auto added to Geo_obects
        dict_['full2'] = dict_['full'] + dict_['symmetric']
        dict_['full3'] = dict_['full2']
        dict_['full3'].append(dict_['6-ply'][1])
        dict_['full3'].append(dict_['10-ply'][0])

        # A group that samples the first item of other groups except fulls and all
        dict_['sample'] = []
        for k, v in sorted(dict_.items(), key=ut.natural_sort):
            if k not in ('full', 'full2', 'full3', 'all'):
                sample = dict_[k][0]
                if sample not in dict_['sample']:
                    dict_['sample'].append(sample)

        return dict_


    # HELPERS -------------------------------------------------------------
    # Material Manipulations
    @classmethod
    def _convert_material_parameters(cls, mat_props):
        '''Handle exceptions for converting input material dict in Standard Form.

        Returns
        -------
        dict
            Material properties converted to Standard Form.

        Raises
        ------
        TypeError
            If mat_props is neither in Quick or Standard Form, but requires to
            be written as a nested dict.

        '''
        try:
            if mat_props is None:
                dict_prop = {}
            # Nested dict (Standard Form), directly assign
            elif isinstance(mat_props, dict):
                # Standard (Nested) Dict
                mat_props['Modulus'].keys()                # needed; triggers KeyError if not Standard Form
                ##_trigger = mat_props['Modulus'].keys()     # needed; triggers KeyError if not Standard Form
                dict_prop = mat_props
            else:
                raise TypeError('Nested dict of material parameters required.  See Tutorial.')
        except(KeyError):
            # Un-nested dict (Quick Form), convert, then assign
            # Assumes Quick Form; attempts to convert
            ##print('Converting mat_props to Standard Form...')
            logging.info('Converting mat_props to Standard Form...')
            dict_prop = cls._to_standard_dict(mat_props)
            #dict_prop = la.distributions.Case._to_standard_dict(mat_props)
        #print(dict_prop)
        return dict_prop

    @classmethod
    def _to_standard_dict(cls, dict_, mat_properties=['Modulus', 'Poissons']):
        '''Return dict from Quick Form to Standard Form (DataFrame-friendly).

        Quick Form assumes input dict lists values ordered by
        Modulus and Poisson's Ratio respectively.  Used internally.

        Quick Form: dict of lists
            d = {'HA' : [5.2e10, 0.25],
                 PSu' : [2.7e9, 0.33]}

        Standard Form: dict of dicts
            d = {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
                 'Poissons': {'HA': 0.25, 'PSu': 0.33}}

        Returns
        -------
        defaultdict
            A dict of materials properties; names as keys, materials:
            properties as key-value pairs.

        '''
        dict_prop = ct.defaultdict(dict)
        for idx, k in enumerate(mat_properties):
            # Modulus --> idx=0; Poissons --> idx=1
            for matl in dict_:
                dict_prop[k][matl] = dict_[matl][idx]
        return dict_prop

    @classmethod
    def get_materials(cls, mat_props):
        '''Return a list of ordered materials. Order can be overridden by a list.

        Parameters
        ----------
        mat_props : dict
            Material properties in Standard or Quick Form.

        Returns
        -------
        list
            An ordered list of materials; uses a pandas DataFrame to order it.

        '''
        mat_props_conv = cls._convert_material_parameters(mat_props)
        return pd.DataFrame(mat_props_conv).index.values.tolist()

    # TODO: Look into why global_vars is used instead of globals
    # TODO: Rename Geo
    def get_FeatureInput(self, Geo, load_params=None, mat_props=None,
                         materials=None, model=None, global_vars=None):
        '''Return a FeatureInput for a given Geometry object.

        Handles conversions to different formats.  Idiomatic approach to building
        FeatureInput objects, especially in custom models.  All parameters
        require user/author input.

        Parameters
        ----------
        Geo : Geometry object
            A native data type comprising geometry information.
        load_params : dict; default None
            Loading parameters.
        mat_props : dict; default None
            Material parameters.
        materials : list; default None
            Unique materials in stacking order; > 1 materials assumes alternating
            layers.  Will be converted to Standard Form.
        model : str; default None
            Custom model name located in `models` directory.
        global_vars : dict, optional; default None
            Additional variables that may be locally calculated though
            globally pertinent.

        Returns
        -------
        FeatureInput
            Essential dict of user-provided values.

        See Also
        --------
        la.distributions.Case.apply() : main creator of FeatureInput objects
        la.models.Wilson_LT() : used to build default instance FeatureInput

        '''
        mat_props_conv = self._convert_material_parameters(mat_props)

        if materials is None:
            materials = self.get_materials(mat_props_conv)

        # TODO: Add Exception handling of materials order list and mat_props here.
        FeatureInput = {
            'Geometry': Geo,
            'Parameters': load_params,
            'Properties': mat_props_conv,
            'Materials': materials,
            'Model': model,
            'Globals': global_vars,
        }
        return FeatureInput

    # Make generators of custom geometry strings or objects
    def generate(self, selection=None, geo_inputs=False):
        '''Yield a generator of selected geometry strings or objects given a key.

        Parameters
        ----------
        selection : list of strings; default None
            The strings are key names within the geo_inputs dict.
        geo_inputs : bool; default False
            If true, uses geo_inputs from BaseDefaults class; else defaults to Geo_objects

        See Also
        --------
        utils.tools.natural_sort : orders `dict.items()` in loops; needed for tests

        Examples
        --------
        >>> from lamana.input_ import BaseDefaults
        >>> bdft = BaseDefaults()
        >>> bdft.generate()
        <itertools.chain at 0x7d1e278>                     # yields a generator

        >>> list(bdft.generate(selection=['5-ply'], geo_inputs=True))
        >>> list(gen)
        ['400-200-800', '400-[200]-800', '400-200-400S']   # geometry strings

        >>> list(bdft.generate(selection=['standard'], geo_inputs=False))
        [Geometry object (400.0-[200.0]-800.0)]            # Geometry object; default

        '''
        # Default to all strings/objects (not groups) if None selected
        try:
            # selection='invalid key'
            if not set(selection).intersection(self.geo_inputs.keys()):
                raise KeyError('Key not found in geo_inputs dict.')
        except(TypeError):
            # selection=None; default 'all' key
            if geo_inputs is True:
                return self.geo_inputs['all']
            elif geo_inputs is False:
                return self.Geo_objects['all']
        #print(selection)
        else:
            # selection=['valid key']
            if geo_inputs is True:
                dict_ = self.geo_inputs                    # geometry strings
            else:
                dict_ = self.Geo_objects                   # Geometry objects

            # Sorted values filtered by selected keys
            nested_lists = (dict_[k] for k in selection
                            if k in sorted(dict_, key=ut.natural_sort))
            # print(list(flattened))
            return it.chain(*nested_lists)                 # flattened


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
        mid_con = ['0']                                    # for even plies
    out_con = convert_lists(out_lst)

    # Make geometry string
    geo = []
    geo.extend(out_con)
    geo.append(str(in_lst))
    geo.extend(mid_con)
    geo_string = '-'.join(geo)
    # TODO: format geo_strings to General Convention
    # NOTE: geo_string comes in int-[float]-int format; _to_gen_convention should patch
    geo_string = Geometry._to_gen_convention(geo_string)
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
    #    str(int(thickness)) for thickness                  # gets unique values
    #    in laminate.groupby('type', sort=False)['t(um)'].first()
    #]
    nplies = len(Frame['layer'].unique())
    geo = [
        str(int(thickness)) for thickness                  # gets unique values
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
    geo_string = Geometry._to_gen_convention(geo_string)
    return geo_string


#TODO: Add extract_dataframe and fix_discontinuities here from controls.py; make tests.

#DEPRECATE: remove and replace with Cases() (0.4.11.dev0)
#Does not print cases accurately
#Did not fail test although alias given for name
def get_frames(cases, name=None, nplies=None, ps=None):
#def select_frames(cases, name=None, nplies=None, ps=None):
    '''Yield and print a subset of case DataFrames given cases.

    Else, print all DataFrames for all cases.

   .. note:: DEPRECATE LamAna 0.4.11.dev0
           `lamanator` will be removed in LamAna 0.5 and replaced by
           `lamana.distributions.Cases` because the latter is more efficient.

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
    >>> cases_selected = ut.select_frames(cases, name='Trilayer', ps=[])
    >>> LMs_list = list(cases)                             # capture generator contents
    >>> LMs_list = [LM for LM in cases_selected]           # capture and exhaust generator
    >>> for LMs in cases_selected:                         # exhaust generator; see contents
    ...    print(LMs)

    Notes
    -----
    This function is a predecessor to the modern Cases.select() method.  It is
    no longer maintained (0.4.11.dev0), though possibly useful for extracting
    selected DataFrames from existing cases.  Formerly `get_frames()`.

    See Also
    --------
    lamana.distributions.Cases.select() : canonical way to select df subsets.

    Yields
    ------
    DataFrame
        Extracted data from a sequence of case objects.

    '''
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

# TODO: Transferred from utils.tools
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
        elif isinstance(v, Geometry):                          # class
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

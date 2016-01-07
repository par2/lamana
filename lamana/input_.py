# -----------------------------------------------------------------------------
# Classes and functions for handling user inputs.
# Geometry(): parse user input geometry strings to a tuple of floats (and lists/str)
# BaseDefaults(): library of general geometry defaults; subclassed by the user.
# flake8 input_.py --ignore=E265,E501,F841,N802,N803,N806

import itertools as it
import collections as ct

import pandas as pd

import lamana as la
from lamana.utils import tools as ut

# =============================================================================
# USER INPUT ------------------------------------------------------------------
# =============================================================================
# Parses informations and generates User Input objects, i.e. Geometry()


class Geometry(object):
    '''Parse input geometry string into floats; return a namedtuple (GeometryTuple).

    When a single (or a list of) string(s) is passed to
    distributions.Case.apply() method, this class parses those strings into
    (outer, [inner], middle, 'S?') format. Formatted in General Convention,
    a converted namedtuple object is returned.

    Objects
    =======
    (400.0, [200.0], 800.0)                                # multi-ply
    (400.0, [200.0], 800.0, 'S')                           # multi-ply, symmetric
    (400.0, [100.0, 100.0], 800.0)                         # multi-ply, [inner_i]

    Uses
    ====
    General: outer-[inner_i]-middle
    Short-hand: outer-inner-middle

    Variables
    =========
    geo_input : list or tupled list
        Geometry thicknesses of a laminate.

    Properties
    ==========
    total : float
        Calculate total thickness for laminates using any convention.
    total_middle : list; float
        Calculate total thickness for middle lamina using any convention.
    total_inner : list; float
        Calculate total thickness for inner lamina using any convention.
    total_inner_i : list; float
        Calculate total thickness for each inner_i lamina.
    total_outer : list; float
        Calculate total thickness for outer lamina using any convention.
    is_symmetric : bool
        Return True if 'S' convention is used.

    Examples
    ========
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


    Preferred
    =========
    >>> G1 = la.input_.Geometry('400-200-800')
    >>> G1
    GeometryTuple(outer=400.0, inner=[200.0], middle=800.0)
    >>> G1.inner
    [200.0]
    '''

    def __init__(self, geo_input):
        '''Ideally a want to call Geometry and get namedtuple auto; return self?'''

        '''Consolidate into namedtuple or self.'''
        self.namedtuple = self._parse_geometry(geo_input)  # a namedtuple; see collections lib
        self.geometry = self._parse_geometry(geo_input)    # a namedtuple; see collections lib
        self.middle = self.geometry.middle                 # attributes from namedtuple; symmetric sensitive
        self.inner = self.geometry.inner
        self.outer = self.geometry.outer

        self.string = self.__class__._to_gen_convention(geo_input)

        # Private attribute used for hashing and set comparisons
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

        The only required property is that objects which compare equal
        have the same hash value (REF 035).  self.__dict__ is unhashable
        due to the inner list.  So a copy is made called _geometry_hash
        of GeometryTuple with tupled inner instead.'''
        return hash(self._geometry_hash)
        #return hash(tuple(sorted(self.__dict__.items())))
        #return hash(self._geo_string)

    def _parse_geometry(self, geo_input, hash_=False):
        '''Return a namedtuple of outer-inner-middle geometry values.

        Per General Convention, a GeometryTuple has floats and an inner list.
        Checks for symmetry, handles inner list, then makes the GeometryTuple.

        Also can create a hashable version of GeometryTuple; tuple instead of
        list for inner_i.

        Formats
        =======
        ('outer-[inner,...]-middle')
        ('outer-[inner,...]-middleS')
        'outer-[inner,...]-middle'

        Variables
        =========
        geo_input : tupled str or str
            outer-inner-middle values or outer-[inner]-middle values.

        Returns
        =======
        geo_namedtuple : namedtuple; mixed
            Numeric values converted to floats; (outer, [inner], middle,'S?')
        '''

        def check_symmetry(last):
            '''Yield float or str if 'S' is in the last token of the geometry string.

            Example
            =======
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

            Example
            =======
            >>> list(parse_inner('[100,100]'))
            [100.0, 100.0]
            >>> list(parse_inner('[200]'))
            [200.0]
            >>> list(parse_inner('200'))
            [200.0]
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
            if 'S' not in geo_input:
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
        # Crude exception handling
        tokens = geo_input.split('-')
        if not isinstance(geo_input, str):
            raise TypeError("Cannot parse input type.  Supported types: str")
        elif len(tokens) < 3:
                '''Replace with custom exception'''
                raise Exception("Input token is too short. Supported geometry string format: 'outer-[inner_i]-middle'")
        else:
            '''Find another name for hash_ which is a bool'''
            # Gets hash_ bool from parsed_geometry
            return _make_GeometryTuple(tokens, hashable=hash_)

    @classmethod
    def _to_gen_convention(cls, geo_input):
        '''Return a geometry string converted to general convention.'''
        tokens = geo_input.split('-')
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
        '''Calculate total thickness for each inner_i lamina.'''
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
        ========
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
    '''Subclass general defaults for laminate geometries and objects.

    Allows quick access to default parameters.  Useful in consistent testing.

    - Base : Default geometry strings
    - Base : Default Geometry objects
    - Sub-class : Default material and geometric/loading parameters
    - Sub-class : Default FeatureInputs

    Users can subclass these geometric defaults and add specific parameters
    (loading, material, geometric, etc.) to improve start-up and reduce
    redundant code.

    New geometry strings can be added to the geo_inputs dict (extension).
    NOTE: removing dict entries (trimming) will break tests (not recommended).

    Methods
    =======
    get_FeatureInput --> dict
        Get the basic FeatureInput object; subclass in models.
    get_materials --> list
        Get a list of materials in order from a mat_props dict or DataFrame.
    generate --> generator
        Build a generator of selected geo

    Examples
    ========
    >>> bdft = BaseDefaults()
    >>> bdft.geos_most                                     # list of geometry Input strings
    [('0-0-2000'), ('1000-0-0'), ('600-0-800'),
    ('500-500-0'), ('400-200-800')]

    >>> bdft.Geos_simple                                   # list of Geometry objects
    [<Geometry object ('0-0-2000')>,
     <Geometry object ('1000-0-0')>,
     <Geometry object '600-0-800')>,
     <Geometry object ('500-500-0')>,]

    >>> from lamana.models import Wilson_LT as wlt         # user-implemmented Defaults
    >>> dft = wlt.Defaults()                               # sub-classed from BaseDefaults
    >>> dft.load_params = {'R' : 12e-3, 'a' : 7.5e-3, 'p' : 1,
                         'P_a' : 1, 'r' : 2e-4,}

    >>> dft.mat_props = {'HA' : [5.2e10, 0.25], 'PSu' : [2.7e9, 0.33],}
    >>> dft.FeatureInput
    {'Geometry' : '400-[200]-800',
     'Geometric' : {'R' : 12e-3, 'a' : 7.5e-3, 'p' : 1, 'P_a' : 1, 'r' : 2e-4,},
     'Materials' : {'HA' : [5.2e10, 0.25], 'PSu' : [2.7e9, 0.33],},
     'Custom' : None,
     'Model' : Wilson_LT,
    }

    '''

    def __init__(self):
        # Geometry Input Strings
        '''DEV: Add geometry strings here.  Do not remove.'''
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
        # Then define attributes (below) for geo_inputs and Geo_objects for API access.
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
        '''Return an updated dict with keys of specified groups.

        This method is useful for automating groupings; new ply keys or
        values can be added with relative ease to the dict. This method should
        group them easily.

        Requires
        ========
        - name keys by number of plies; e.g. '14-ply' (human sorts)
        - add values as a list of strings
        - add to the geo_inputs dict (Geo_objects mimics and updates automatically)

        See Also
        ========
        utils.tools.natural_sort: order dict.items() in loops; needed for tests

        '''
        d = ct.defaultdict(list)
        dict_ = dict_default.copy()
        # Sort dict naturally to help order the list values
        #for k,v in sorted(dict_.items(), key=natural_sort):
        for k, v in sorted(dict_.items(), key=ut.natural_sort):
            # Prepare k, v
            num = cls._extract_number(k)
            if Geo_obj:                             # build Geo_objects simul.
                G = la.input_.Geometry
                v = [G(geo_string) for geo_string in v]
                dict_[k] = v                        # overwrite original dict_
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
                    elif '[' not in geo_string:
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
    '''Consider separating'''
    # Material Manipulations
    @classmethod
    def _convert_material_parameters(cls, mat_props):
        '''Handle exceptions for converting input material dict in Standard Form.'''
        try:
            if mat_props is None:
                dict_prop = {}
            # Nested dict (Standard Form), directly assign
            elif isinstance(mat_props, dict):
                # Standard (Nested) Dict
                mat_props['Modulus'].keys()                     # needed; triggers KeyError if not Standard Form
                ##_trigger = mat_props['Modulus'].keys()        # needed; triggers KeyError if not Standard Form
                dict_prop = mat_props
            else:
                raise TypeError('Nested dict of material parameters required.  See Tutorial')
        except(KeyError):
            # Un-nested dict (Quick Form), convert, then assign
            # Assumes Quick Form; attempts to convert
            print('Converting mat_props to Standard Form.')
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
        =======
        dict_prop : dict (defaultdict)
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
        '''Return a list of ordered materials. Order can be overridden by a list.'''
        mat_props_conv = cls._convert_material_parameters(mat_props)
        return pd.DataFrame(mat_props_conv).index.values.tolist()

    def get_FeatureInput(self, Geometry, load_params=None, mat_props=None,
                         materials=None, model=None, global_vars=None):
        '''Return a FeatureInput for a given Geometry object.'''
        mat_props_conv = self._convert_material_parameters(mat_props)

        if materials is None:
            materials = self.get_materials(mat_props_conv)

        '''Add Exception handling of materials order list and mat_props here.'''
        FeatureInput = {'Geometry': Geometry,
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
        ==========
        selection : list; None
            Of strings of keys within the geo_inputs dict.
        geo_inputs : bool; False
            If true, uses geo_inputs from BaseDefaults class; else defaults to Geo_objects

        Examples
        ========
        >>> from lamana.input_ import BaseDefaults
        >>> bdft = BaseDefaults()
        >>> bdft.generate()
        <itertools.chain at 0x7d1e278>                        # yields a generator

        >>> list(bdft.generate(selection=['5-ply'], geo_inputs=True))
        >>> list(gen)
        ['400-200-800', '400-[200]-800', '400-200-400S']      # geometry strings

        >>> list(bdft.generate(selection=['standard'], geo_inputs=False))
        [Geometry object (400.0-[200.0]-800.0)]               # Geometry object; default

        See Also
        ========
        utils.tools.natural_sort: order dict.items() in loops; needed for tests

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
                dict_ = self.geo_inputs                      # geometry strings
            else:
                dict_ = self.Geo_objects                     # Geometry objects

            # Sorted values filtered by selected keys
            nested_lists = (dict_[k] for k in selection
                            if k in sorted(dict_, key=ut.natural_sort))
            # print(list(flattened))
            return it.chain(*nested_lists)                   # flattened

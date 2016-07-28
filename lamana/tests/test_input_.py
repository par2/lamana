#------------------------------------------------------------------------------
'''Test user Input Geometry class: attributes, geometry parsing and properties.'''

import nose.tools as nt

from .. import input_
from ..lt_exceptions import FormatError
from ..models import Wilson_LT as wlt
from ..utils import tools as ut


# Setup -----------------------------------------------------------------------
# User Geometry Strings, g, of Different Laminate Types
g1 = ('0-0-2000')                                          # Monolith
g2 = ('1000-0-0')                                          # Bilayer
g3 = ('600-0-800')                                         # Trilayer
g4 = ('500-500-0')                                         # 4-ply
g5 = ('400-200-800')                                       # Short-hand; <= 5-ply
g6 = ('400-200-400S')                                      # Symmetric
g7 = ('400-[200]-800')                                     # General convention; 5-ply
g8 = ('400-[100,100]-800')                                 # General convention; 7-plys
g9 = ('400-[100,100]-400S')                                # General and Symmetric convention; 7-plys
g10 = ('400-[100,100,100]-800')
g11 = ('400-[100,100,100,100]-800')
g12 = ('400-[100,100,100,100,100]-800')

geos_most = [g1, g2, g3, g4, g5]
geos_special = [g6, g7, g8, g9]
geos_full = [g1, g2, g3, g4, g5, g6, g7, g8, g9]
geos_full2 = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12]


# input_.Geometry Object, G
G = input_.Geometry

Geo1 = G('0-0-2000')
Geo2 = G('1000-0-0')
Geo3 = G('600-0-800')
Geo4 = G('500-500-0')
Geo5 = G('400-200-800')
Geo6 = G('400-200-400S')
Geo7 = G('400-[200]-800')
Geo8 = G('400-[100,100]-800')
Geo9 = G('400-[100,100]-400S')
Geos_inner = [Geo7, Geo8, Geo9]
Geos_full = [Geo1, Geo2, Geo3, Geo4, Geo5, Geo6, Geo7, Geo8, Geo9]

bdft = input_.BaseDefaults()                                      # Defaults indep. from models
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
# Geometry objects are pre-generated (Geo) and compiled into lists (Geo_name).
# Geometry attrs are tested for various geometries.
# Or geometry lists (geo_name) are iterated to test Geometry object creation.
'''Can the list comparison be sped up.'''
'''https://pythonhosted.org/testfixtures/comparing.html#generators'''


# Test String Conversion and Types
def test_tokenize_geostring1():
    '''Check result is converted outer, inner_i, middle tokens.'''
    # Parse geometry string by dashes
    geo_strings = {
        0: '400-[150,50]-800',                             # regular geometry string
        1: '(300,100)-[150,50]-800',                       # irregualar geometry string; outer duple
        2: '400-[(150,50)]-800',                           # irregualar geometry string; inner_i duple
        3: '400-[150,(75,50),25]-800',                     # irregualar geometry string; inner_i duple and regular inners
        4: '(300,100)-[150,(75,50),25]-800',               # irregualar geometry string; outer and inner_i duple + reg. inners
    }

    # TODO: Change post general convention fix
    expected_lists = {
        0: ['400', '[150,50]', '800'],
        1: ['(300,100)', '[150,50]', '800'],
        2: ['400', '[(150,50)]', '800'],
        3: ['400', '[150,(75,50),25]', '800'],
        4: ['(300,100)', '[150,(75,50),25]', '800'],
    }
    for geo_string, expected in zip(geo_strings.values(), expected_lists.values()):
        actual = input_.tokenize_geostring(geo_string)
        nt.assert_equals(actual, expected)


def test_geo_inner1():
    '''Check non-decimal inner converts to decimal.'''
    # Convert inside string '200' to 200.0 if brackets aren't found
    conv = input_.Geometry._to_gen_convention
    geo1 = '400-200-800'
    geo2 = '400-200.0-800'
    expected = '400.0-[200.0]-800.0'
    nt.assert_equal(conv(geo1), expected)
    nt.assert_equal(conv(geo2), expected)

# Test Exception Handling in _to_gen_convention()
@nt.raises(TypeError)
def test_geo_string1():
    '''Throw TypeError if geo_input is non-string; list'''
    err = G(['400-200-800'])                               # list


@nt.raises(TypeError)
def test_geo_string2():
    '''Throw TypeError if geo_input is non-string; floats'''
    err = G(400, 200, 800)                                 # floats


@nt.raises(FormatError)
def test_geo_token1():
    '''Check geo_input throws Exception if less than 3 tokens.'''
    G('400-200')


@nt.raises(FormatError)
def test_geo_token2():
    '''Check geo_input throws Exception if more than 3 tokens; 4 splits.'''
    G('400-200-800-100')


@nt.raises(FormatError)
def test_geo_letters1():
    '''Check geo_input throws Exception if non-'S' letter found.'''
    G('400-200-800A')


@nt.raises(FormatError)
def test_geo_letters2():
    '''Check geo_input throws Exception if more than one letter found.'''
    G('400-200-800SS')


# Test Validations of geo_strings

#@nt.raises(InvalidError)
#def test_laminator_validation1():
#    '''Check valid: if inner, must have outer.'''
#    case = ut.laminator(['0-200-400S'])


# Test Geometry() Attributes
def test_Geo_middle1():
    '''Check for 'S' in the middle layer.'''
    # 400-[100,100]-800, 400-[100,100]-400S
    ##Geos = [dft.Geo_objects[8], dft.Geo_objects[14]]
    Geos = [Geo8, Geo9]
    actual = [Geo.middle for Geo in Geos]
    expected = [800.0, 400.0]
    nt.assert_equal(actual, expected)


def test_Geo_inner1():
    '''Check values of the inner layer.'''
    # 0-0-2000, 400-200-400S, 400-[200]-800, 400-[100,100]-800
    Geos = [Geo1, Geo6, Geo7, Geo8]
    actual = [Geo.inner for Geo in Geos]
    expected = [[0.0], [200.0], [200.0], [100.0, 100.0]]
    nt.assert_equal(actual, expected)


def test_Geo_inner2():
    '''Check conversion of inner to [inner]; LPEP 001.01 compliance.'''
    ##actual = [Geo.inner for Geo in dft.Geos_full]
    actual = [Geo.inner for Geo in Geos_full]
    expected = [
        [0.0], [0.0], [0.0], [500.0], [200.0],
        [200.0], [200.0], [100, 100], [100, 100]
    ]
    nt.assert_equal(actual, expected)


def test_Geo_outer1():
    '''Check values in the outer layer.'''
    # 0-0-2000, 1000-0-0, 600-0-800
    Geos = [Geo1, Geo2, Geo3]
    actual = [Geo.outer for Geo in Geos]
    expected = [0.0, 1000.0, 600.0]
    nt.assert_equal(actual, expected)


def test_Geo_string1():
    '''Check conversion of geometry string to general convention.'''
    G = input_.Geometry
    actual1 = G('400.0-200.0-800.0').string
    actual2 = G('400-200-800').string
    actual3 = G('400-[200]-800').string
    actual4 = G('400.0-[200.0]-800.0').string
    actual5 = G('400-[100,100]-800').string
    actual6 = G('400.0-[100.0,100.0]-800.0').string
    actual7 = G('400.0-[100.0,100.0,100,100]-800.0').string
    actual8 = G('400-200-400S').string
    expected1 = '400.0-[200.0]-800.0'
    expected2 = '400.0-[100.0,100.0]-800.0'
    expected3 = '400.0-[100.0,100.0,100.0,100.0]-800.0'
    expected4 = '400.0-[200.0]-400.0S'
    #print(actual1)
    #print(actual2)
    #print(expected1)

    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected1)
    nt.assert_equal(actual3, expected1)
    nt.assert_equal(actual4, expected1)
    nt.assert_equal(actual5, expected2)
    nt.assert_equal(actual6, expected2)
    nt.assert_equal(actual7, expected3)
    nt.assert_equal(actual8, expected4)


# Test Geometry() Propetries
def test_Geo_symmetric1():
    '''Check for 'S' in the middle layer; few.'''
    Geos = [Geo8, Geo9]
    actual = [Geo.is_symmetric for Geo in Geos]
    expected = [False, True]
    nt.assert_equal(actual, expected)


def test_Geo_symmetric2():
    '''Check for 'S' in the middle layer' many.'''
    actual = [G.is_symmetric for G in Geos_full]
    expected = [False, False, False, False, False, True, False, False, True]
    nt.assert_equal(actual, expected)


def test_Geo_total_inner_i1():
    '''Calculate totals for each inner_i lamina thickness.'''
    actual = [G.total_inner_i for G in Geos_full]
    expected = [
        [0.0], [0.0], [0.0], [1000.0], [400.0], [400.0],
        [400.0], [200.0, 200.0], [200.0, 200.0]
    ]
    nt.assert_equal(actual, expected)


def test_Geo_total_inner_i2():
    '''Calculate totals for last slice in inner_i.'''
    actual = [G.total_inner_i[-1] for G in Geos_full]
    expected = [0.0, 0.0, 0.0, 1000.0, 400.0, 400.0, 400.0, 200.0, 200.0]
    nt.assert_equal(actual, expected)


def test_Geo_total_layers1():
    ''' total laminate thickness for any convention, using .totals_.'''
    actual = [G.total_middle + G.total_inner + G.total_outer for G in Geos_full]
    expected = [
        2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0
    ]
    nt.assert_equal(actual, expected)


'''Need tests for exceptions of improper inputs.'''


# Test Geometry._parse_geometery() Method
def test_Geo_parse1():
    ''' Parse geometries as list of tuples with floats'; 1 Geo.'''
    geos = [('400-200-800')]
    actual = [G(geo).geometry for geo in geos]
    expected = [(400.0, [200.0], 800.0)]
    nt.assert_equal(actual, expected)


def test_Geo_parse2():
    '''Parse geometries as list of tuples with floats; 2 Geos.'''
    g4 = ('500-500-0')
    g5 = ('400-200-800')
    geos = [g4, g5]
    actual = [G(geo).geometry for geo in geos]
    expected = [(500.0, [500.0], 0.0), (400.0, [200.0], 800.0)]
    nt.assert_equal(actual, expected)


def test_Geo_parse3():
    '''Parse geometries as list of tuples with floats; many.'''
    actual = [G(geo).geometry for geo in geos_most]
    expected = [
        (0.0, [0.0], 2000.0), (1000.0, [0.0], 0.0), (600.0, [0.0], 800.0),
        (500.0, [500.0], 0.0), (400.0, [200.0], 800.0)
    ]
    nt.assert_equal(actual, expected)


def test_Geo_parse4():
    '''Parse geometries as list of tuples with floats; special cases.'''
    actual = [G(geo).geometry for geo in geos_special]
    expected = [
        (400.0, [200.0], 400.0, 'S'), (400.0, [200.0], 800.0),
        (400.0, [100.0, 100.0], 800.0), (400.0, [100.0, 100.0], 400.0, 'S')
    ]
    nt.assert_equal(actual, expected)


def test_Geo_parse5():
    '''Parse geometries as list of tuples with floats; special cases.'''
    actual = [G(geo).geometry for geo in geos_full]
    expected = [
        (0.0, [0.0], 2000.0), (1000.0, [0.0], 0.0), (600.0, [0.0], 800.0),
        (500.0, [500.0], 0.0), (400.0, [200.0], 800.0),
        (400.0, [200.0], 400.0, 'S'), (400.0, [200.0], 800.0),
        (400.0, [100.0, 100.0], 800.0), (400.0, [100.0, 100.0], 400.0, 'S')
    ]
    nt.assert_equal(actual, expected)


# Test Geometry.itotal Method
def test_Geo_total1():
    '''Calculate total laminate thickness for any convention.'''
    actual = [G.total for G in Geos_full]
    expected = [
        2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0
    ]
    nt.assert_equal(actual, expected)


def test_Geo_total_middle1():
    '''Calculate total lamina thickness for any convention.'''
    actual = [G.total_middle for G in Geos_full]
    expected = [2000.0, 0, 800.0, 0, 800.0, 800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected)


# Now totals inner_i
def test_Geo_total_inner1():
    '''Calculate total lamina thickness for inner_i.'''
    '''CAUTION: since GeometryTuple, this output is different.'''
    actual = [G.total_inner_i for G in Geos_full]
    expected = [
        [0.0],
        [0.0],
        [0.0],
        [1000.0],
        [400.0],
        [400.0],
        [400.0],
        [200.0, 200.0],
        [200.0, 200.0]
    ]
    nt.assert_equal(actual, expected)


def test_Geo_total_inner2():
    '''Calculate total for inner_i slice.'''
    actual = [Geo8.total_inner_i[0], Geo9.total_inner_i[0]]
    expected = [200.0, 200.0]
    nt.assert_equal(actual, expected)


def test_Geo_total_outer1():
    '''Calculate total lamina thickness for any convention.'''
    actual = [G.total_outer for G in Geos_full]
    expected = [0.0, 2000.0, 1200.0, 1000.0, 800.0, 800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected)


# Tests Geometry Special Methods
def test_Geo_eq1():
    '''Compare Geometry objects are the same namedtuple.'''
    expected = bdft.Geos_standard[0]
    for actual in dft.Geo_objects['5-ply']:
        if not actual.is_symmetric:
            nt.assert_equal(actual, expected)


def test_Geo_ne1():
    '''Compare Geometry objects are not the same namedtuple.'''
    expected = bdft.Geos_standard[0]
    for actual in dft.Geos_even:
        nt.assert_not_equal(actual, expected)


# TODO: Make global manual standard Geos for these comparisons
# Instance comparisons
def test_Geo_compare_instances1a():
    '''Check __eq__ between hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')
    G3 = input_.Geometry('400-200-800')

    #assert G1 == G2
    #assert G1 == G3
    #assert G2 == G1
    #assert G3 == G1
    nt.assert_equal(G1, G2)
    nt.assert_equal(G1, G3)
    nt.assert_equal(G2, G1)
    nt.assert_equal(G3, G1)


def test_Geo_compare_instances1b():
    '''Check __eq__ between hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')
    G3 = input_.Geometry('400-200-800')

    #assert G1 == G2
    #assert G1 == G3
    #assert G2 == G1
    #assert G3 == G1
    nt.assert_true(G1 == G2)
    nt.assert_true(G1 == G3)
    nt.assert_true(G2 == G1)
    nt.assert_true(G3 == G1)


def test_Geo_compare_instances2():
    '''Check __ne__ between hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')
    G3 = input_.Geometry('400-200-800')

    #assert not G1 != G2
    #assert not G1 != G3
    #assert not G2 != G1
    #assert not G3 != G1
    nt.assert_false(G1 != G2)
    nt.assert_false(G1 != G3)
    nt.assert_false(G2 != G1)
    nt.assert_false(G3 != G1)


def test_Geo_compare_instances3():
    '''Check __eq__ between unequal hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G4 = input_.Geometry('1000-[0]-0')
    G5 = input_.Geometry('400-[150,50]-800')

    #assert not G1 == G4
    #assert not G1 == G5
    #assert not G4 == G1
    #assert not G5 == G1
    nt.assert_false(G1 == G4)
    nt.assert_false(G1 == G4)
    nt.assert_false(G4 == G1)
    nt.assert_false(G5 == G1)


def test_Geo_compare_instances4():
    '''Check __ne__ between unequal hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G4 = input_.Geometry('1000-[0]-0')
    G5 = input_.Geometry('400-[150,50]-800')

    #assert G1 != G4
    #assert G1 != G5
    #assert G4 != G1
    #assert G5 != G1
    nt.assert_true(G1 != G4)
    nt.assert_true(G1 != G4)
    nt.assert_true(G4 != G1)
    nt.assert_true(G5 != G1)


# Subclass comparisons
def test_Geo_compare_subclasses1():
    '''Check __eq__ between hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')

    class SubGeometry(input_.Geometry):
        pass
    G6 = SubGeometry('400-[200]-800')

    #assert G1 == G6
    #assert G2 == G6
    #assert G6 == G1
    #assert G6 == G2
    nt.assert_equal(G1, G6)
    nt.assert_equal(G2, G6)
    nt.assert_equal(G6, G1)
    nt.assert_equal(G6, G2)


def test_Geo_compare_subclasses2():
    '''Check __ne__ between hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')

    class SubGeometry(input_.Geometry):
        pass
    G6 = SubGeometry('400-[200]-800')

    #assert not G1 != G6
    #assert not G2 != G6
    #assert not G6 != G1
    #assert not G6 != G2
    nt.assert_false(G1 != G6)
    nt.assert_false(G2 != G6)
    nt.assert_false(G6 != G1)
    nt.assert_false(G6 != G2)


def test_Geo_compare_subclasses3():
    '''Check __eq__ between unequal hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')

    class SubGeometry(input_.Geometry):
        pass
    G7 = SubGeometry('1000-[0]-0')
    G8 = SubGeometry('400-[100,100]-0')

    #assert not G1 == G7
    #assert not G7 == G1
    #assert not G1 == G8
    #assert not G8 == G1
    nt.assert_false(G1 == G7)
    nt.assert_false(G7 == G1)
    nt.assert_false(G1 == G8)
    nt.assert_false(G8 == G1)


def test_Geo_compare_subclasses4():
    '''Check __ne__ between unequal hashable Geometry object instances.'''
    G1 = input_.Geometry('400-[200]-800')

    class SubGeometry(input_.Geometry):
        pass
    G7 = SubGeometry('1000-[0]-0')
    G8 = SubGeometry('400-[100,100]-0')

    #assert G1 != G7
    #assert G7 != G1
    #assert G1 != G8
    #assert G8 != G1
    nt.assert_true(G1 != G7)
    nt.assert_true(G7 != G1)
    nt.assert_true(G1 != G8)
    nt.assert_true(G8 != G1)


# Hash comparisons
def test_Geo_compare_hashes1():
    '''Check __eq__ between Geometry object hashes.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')
    G3 = input_.Geometry('400-200-800')

    nt.assert_equal(G1.__hash__, G2.__hash__)
    nt.assert_equal(G1.__hash__, G3.__hash__)
    nt.assert_equal(G2.__hash__, G1.__hash__)
    nt.assert_equal(G3.__hash__, G1.__hash__)


def test_Geo_compare_hashes2():
    '''Check __eq__ between private Geometry hash.'''
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')
    G3 = input_.Geometry('400-200-800')

    nt.assert_equal(G1._geometry_hash, G2._geometry_hash)
    nt.assert_equal(G1._geometry_hash, G3._geometry_hash)
    nt.assert_equal(G2._geometry_hash, G1._geometry_hash)
    nt.assert_equal(G3._geometry_hash, G1._geometry_hash)


# Set comparisons
def test_Geo_compare_sets1():
    '''Check __eq__, __ne__ and sets containing Geometry object instances.'''
    # Tests __hash__ and _geometry_hash()
    G1 = input_.Geometry('400-[200]-800')
    G2 = input_.Geometry('400-[200]-800')
    G3 = input_.Geometry('400-200-800')
    G4 = input_.Geometry('1000-[0]-0')
    G5 = input_.Geometry('400-[150,50]-800')

    class SubGeometry(input_.Geometry):
        pass
    G6 = SubGeometry('400-[200]-800')
    G7 = SubGeometry('1000-[0]-0')
    G8 = SubGeometry('400-[100,100]-0')

    #assert set([G1, G2])
    #assert set([G1]) == set([G2])
    #assert set([G1]) == set([G3])
    #assert set([G1]) != set([G4])
    #assert set([G1]) != set([G5])
    #assert len(set([G1,G2,G3,G4,G5,G6,G7,G8])) == 4

    nt.assert_set_equal(set([G1, G2]), set([G1, G2]))
    nt.assert_set_equal(set([G1]), set([G2]))
    nt.assert_set_equal(set([G1]), set([G3]))
    nt.assert_true(set([G1]) != set([G4]))
    nt.assert_true(set([G1]) != set([G5]))
    nt.assert_equal(len(set([G1, G2, G3, G4, G5, G6, G7, G8])), 4)


# Tests for Geometry Prints
def test_Geo_print1():
    '''Check Geometry.__repr__ output.'''
    geo_input = '400-[200]-800'
    actual = input_.Geometry(geo_input).__repr__()
    expected = 'Geometry object (400.0-[200.0]-800.0)'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Geo_print2():
    '''Check Geometry.__repr__ symmetry output.'''
    geo_input = '400-[200]-400S'
    actual = input_.Geometry(geo_input).__repr__()
    expected = 'Geometry object (400.0-[200.0]-400.0S)'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Geo_print3():
    '''Check trimmed Geometry.__str__ output.'''
    geo_input = '400-[200]-800'
    actual = input_.Geometry(geo_input).__str__()
    expected = '400.0-[200.0]-800.0'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Geo_print4():
    '''Check trimmed Geometry.__str__ symmetry output.'''
    geo_input = '400-[200]-400S'
    actual = input_.Geometry(geo_input).__str__()
    expected = '400.0-[200.0]-400.0S'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


# BaseDefaults ----------------------------------------------------------------
# Defaults can change.  If Defaults are altered, static tests will break.
# The 'static' attributes are commonly used, i.e. standard, special, full.
# The 'variable' attributes can be changed in BaseDefaults.
# Certain tests are designed to be be flexible to user/dev extension (comparing sets).
# Thus, BaseDefaults can be extended (not trimmed) and tests will still pass.


# FeatureInput Maker Attributes
def test_BaseDefaults_getFeatureInput1():
    '''Confirm get_FeatureInput gives proper values.'''
    G = input_.Geometry
    # NOTE: why do we need mat_praps?
    mat_props = {
        'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
        'Poissons': {'HA': 0.25, 'PSu': 0.33}
    }
    mod_FeatureInput = {
        'Geometry': G('400-[200]-800'),
        'Parameters': load_params,
        'Properties': {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
                       'Poissons': {'HA': 0.25, 'PSu': 0.33}},
        'Materials': ['HA', 'PSu'],
        ##'Materials' : None,
        'Model': 'Wilson_LT',
        'Globals': None,
    }
    actual = bdft.get_FeatureInput(
        G('400-[200]-800'),
        load_params=load_params, mat_props=mat_props,
        model='Wilson_LT', global_vars=None
    )
    expected = mod_FeatureInput
    nt.assert_equal(actual, expected)


# Static Attributes
def test_BaseDefaults_geostandard1():
    '''Confirm standard values of a 'static' attribute.'''
    actual1 = bdft.geo_inputs['standard']                  # dict
    actual2 = bdft.geos_standard                           # attribute
    expected = ['400-[200]-800']
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


def test_BaseDefaults_geospecial1():
    '''Confirm special values of a 'static' attribute.'''
    actual1 = bdft.geo_inputs['special']                   # dict
    actual2 = bdft.geos_special                            # attribute
    expected = ['0-0-2000', '1000-0-0', '600-0-800', '500-500-0']
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


def test_BaseDefaults_geofull1():
    '''Confirm full values of a 'static' attribute.'''
    actual1 = bdft.geo_inputs['full']                      # dict
    actual2 = bdft.geos_full                               # attribute
    expected = [
        '0-0-2000',
        '1000-0-0',
        '600-0-800',
        '500-500-0',
        '400-200-800',
        '400-[100,100]-0',
        '400-[100,100]-800',
        '400-[100,100,100]-800'
    ]
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


# Variable Attributes
def test_BaseDefaults_geofull2():
    '''Confirm full (v2) values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['full2']                # dict
    default_attr = bdft.geos_full2                         # attribute
    expected = [
        '0-0-2000',
        '1000-0-0',
        '600-0-800',
        '500-500-0',
        '400-200-800',
        '400-[100,100]-0',
        '400-[100,100]-800',
        '400-[100,100,100]-800',
        '600-0-400S',
        '400-200-400S',
        '400-[100,100]-400S'
    ]
    #print(set(default_dict))
    #print(set(expected))
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    #print(actual1)
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_geofull3():
    '''Confirm full (v3) values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['full3']                # dict
    default_attr = bdft.geos_full3                         # attribute
    expected = [
        '0-0-2000',
        '1000-0-0',
        '600-0-800',
        '500-500-0',
        '400-200-800',
        '400-[100,100]-0',
        '400-[100,100]-800',
        '400-[100,100,100]-800',
        '600-0-400S',
        '400-200-400S',
        '400-[100,100]-400S',
        '500-[250,250]-0',
        '500-[50,50,50,50]-0'
    ]
    #print(set(default_dict))
    #print(set(expected))
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    #print(actual1)
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_geoall1():
    '''Confirm basic expected values are in a 'variable' attribute.'''
    geos_all = [
        '0-0-2000',
        '0-0-1000',
        '1000-0-0',
        '600-0-800',
        '600-0-400S',
        '500-500-0',
        '400-[200]-0',
        '400-200-800',
        '400-[200]-800',
        '400-200-400S',
        '400-[100,100]-0',
        '500-[250,250]-0',
        '400-[100,100]-800',
        '400-[100,100]-400S',
        '400-[100,100,100]-800',
        '500-[50,50,50,50]-0',
        '400-[100,100,100,100]-800',
        '400-[100,100,100,100,100]-800'
    ]
    default_dict = bdft.geo_inputs['all']                  # dict
    default_attr = bdft.geos_all                           # attribute
    expected = geos_all
    #print(set(default_dict))
    #print(set(expected)
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    #print(actual1)
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_geomost1():
    '''Confirm most values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['most']                 # dict
    default_attr = bdft.geos_most                          # attribute
    expected = [
        '0-0-2000',
        '1000-0-0',
        '600-0-800',
        '500-500-0',
        '400-200-800'
    ]
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_geoeven1():
    '''Confirm even values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['even']                 # dict
    default_attr = bdft.geos_even                          # attribute
    expected = [
        '1000-0-0',
        '500-500-0',
        '400-[200]-0',
        '400-[100,100]-0',
        '500-[250,250]-0',
        '500-[50,50,50,50]-0',
    ]
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_geoodd1():
    '''Confirm odd values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['odd']                  # dict
    default_attr = bdft.geos_odd                           # attribute
    expected = [
        '0-0-2000',
        '0-0-1000',
        '600-0-800',
        '600-0-400S',
        '400-200-800',
        '400-[200]-800',
        '400-200-400S',
        '400-[100,100]-800',
        '400-[100,100]-400S',
        '400-[100,100,100]-800',
        '400-[100,100,100,100]-800',
        '400-[100,100,100,100,100]-800'
    ]
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_geosymmetric():
    '''Confirm symmetric values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['symmetric']            # dict
    default_attr = bdft.geos_symmetric                     # attribute
    expected = ['600-0-400S',
                '400-200-400S',
                '400-[100,100]-400S']
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_inner_i1():
    '''Confirm inner_i with i > 1.'''
    default_dict = bdft.geo_inputs['inner_i']              # dict
    default_attr = bdft.geos_inner_i                       # attribute
    expected = [
        '400-[100,100]-0',
        '500-[250,250]-0',
        '400-[100,100]-800',
        '400-[100,100]-400S',
        '400-[100,100,100]-800',
        '500-[50,50,50,50]-0',
        '400-[100,100,100,100]-800',
        '400-[100,100,100,100,100]-800'
    ]
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_genconvention1():
    '''Confirm general conventions are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['general conv.']        # dict
    default_attr = bdft.geos_general                       # attribute
    expected = [
        '400-[200]-0',
        '400-[200]-800',
        '400-[100,100]-0',
        '500-[250,250]-0',
        '400-[100,100]-800',
        '400-[100,100]-400S',
        '400-[100,100,100]-800',
        '500-[50,50,50,50]-0',
        '400-[100,100,100,100]-800',
        '400-[100,100,100,100,100]-800'
    ]
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_unconventional1():
    '''Confirm unconventionals are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['unconventional']       # dict
    default_attr = bdft.geos_unconventional                # attribute
    expected = [
        '0-0-2000',
        '0-0-1000',
        '1000-0-0',
        '600-0-800',
        '600-0-400S',
        '500-500-0',
        '400-200-800',
        '400-200-400S',
    ]
    print(default_attr)
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)


def test_BaseDefaults_dissimilar1():
    '''Confirm unconventionals of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['dissimilar']           # dict
    default_attr = bdft.geos_dissimilar                    # attribute
    expected = ['400-[150,50]-800',
                '400-[25,125,50]-800']
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_dict) >= set(expected))
    actual2 = (set(default_attr) >= set(expected))
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)

'''When Geometry objects support comparisons, modify these tests.  See example.'''
'''TODO: Remove following'''
G = input_.Geometry


def test_BaseDefaults_geostandard1_example():
    '''Confirm standard values of a 'static' attribute.'''
    actual1 = bdft.geo_inputs['standard']                  # dict
    actual2 = bdft.geos_standard                           # attribute
    actual3 = bdft.Geos_standard                           # object
    expected1 = ['400-[200]-800']
    expected2 = [G('400-[200]-800')]
    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected1)
    nt.assert_equal(actual3, expected2)                    # test object


def test_BaseDefaults_geomost1_example():
    '''Confirm most values of are in a 'variable' attribute.'''
    default_dict = bdft.geo_inputs['most']                 # dict
    default_attr = bdft.geos_most                          # attribute
    default_objs = bdft.Geos_most                          # objects
    expected1 = ['0-0-2000',
                 '1000-0-0',
                 '600-0-800',
                 '500-500-0',
                 '400-200-800']
    expected2 = [G(geo) for geo in expected1]

    # zip terminates at the shortest list
    # Thus test should be protected if BaseDefaults.geo_inputs is extended
    #for a1, a2, a3, e1, e2 in zip(
    #    default_dict, default_attr, default_objs, expected1, expected2):
    zipped = zip(default_dict, default_attr, default_objs, expected1, expected2)
    for a1, a2, a3, e1, e2 in zipped:
        nt.assert_equal(a1, e1)
        nt.assert_equal(a2, e1)
        nt.assert_equal(a3, e2)


# Generate Attribute
def test_BaseDefaults_generate_Geos1():
    '''Check full Geo_objects from the generator with .generate.'''
    default_dict = bdft.Geo_objects
    default_attr = bdft.Geos_all
    default_gen = [Geo_object for Geo_object in bdft.generate()]
    G = input_.Geometry
    expected1 = [
        [G('0-0-2000'), G('0-0-1000')],
        [G('1000-0-0')],
        [G('600-0-800'), G('600-0-400S')],
        [G('500-500-0'), G('400-[200]-0')],
        [G('400-200-800'), G('400-[200]-800'), G('400-200-400S')],
        [G('400-[100,100]-0'), G('500-[250,250]-0')],
        [G('400-[100,100]-800'), G('400-[100,100]-400S')],
        [G('400-[100,100,100]-800')],
        [G('500-[50,50,50,50]-0')],
        [G('400-[100,100,100,100]-800')],
        [G('400-[100,100,100,100,100]-800')]
    ]
    expected2 = sum(expected1, [])                         # flatten list
    #print(default_dict)
    #print(expected)
    # zip terminates at the shortest list
    # Thus test should be protected if BaseDefaults.geo_inputs is extended
    ##for (k, a1), a2, a3, e1, e2 in zip(
    ##    sorted(default_dict.items(), key=ut.natural_sort),
    ##           default_attr, default_gen, expected1, expected2):
    zipped = zip(
        sorted(default_dict.items(), key=ut.natural_sort),
        default_attr, default_gen, expected1, expected2
    )
    for (k, a1), a2, a3, e1, e2 in zipped:
        nt.assert_equal(a1, e1)
        nt.assert_equal(a2, e2)
        nt.assert_equal(a3, e2)


def test_BaseDefaults_generate_Geos2():
    '''Check the selection of specific Geometry objects from geo_inputs.'''
    actual = [geo_input for geo_input in
              bdft.generate(selection=['1-ply', '2-ply', '3-ply'])]
    G = input_.Geometry
    expected = [
        G('0.0-[0.0]-2000.0'),
        G('0.0-[0.0]-1000.0'),
        G('1000.0-[0.0]-0.0'),
        G('600.0-[0.0]-800.0'),
        G('600.0-[0.0]-400.0S')
    ]
    for a, e in zip(actual, expected):
        #print(a.__dict__)
        #print(e.__dict__)
        #print('\n')
        #assert a.__dict__ == e.__dict__
        nt.assert_equal(a, e)


def test_BaseDefaults_generate_Geos3():
    '''Check 'symmetric' Geo_objects are consistent in generator, key and attr.'''
    generator = bdft.generate(selection=['symmetric'])
    sym_1 = bdft.Geo_objects['symmetric']
    sym_2 = bdft.Geos_symmetric
    ##for Geo_object1, Geo_object2, Geo_object3 in zip(
    ##        generator, bdft.Geo_objects['symmetric'], bdft.Geos_symmetric,):
    for Geo_object1, Geo_object2, Geo_object3 in zip(generator, sym_1, sym_2):
        nt.assert_true(Geo_object1.is_symmetric)
        nt.assert_true(Geo_object2.is_symmetric)
        nt.assert_true(Geo_object3.is_symmetric)


def test_BaseDefaults_generate_Geo4():
    '''Check TypeError is consumed if invalid None key given to Geo_objects dict.'''
    gen = bdft.generate(selection=None, geo_inputs=False)
    actual = list(gen)
    expected = bdft.Geo_objects['all']
    nt.assert_equal(actual, expected)


def test_BaseDefaults_generate_geo1():
    '''Check .generate yields a consumable generator.'''
    gen = bdft.generate(selection=['5-ply'], geo_inputs=True)
    actual = list(gen)
    expected = ['400-200-800', '400-[200]-800', '400-200-400S']
    nt.assert_equal(actual, expected)


def test_BaseDefaults_generate_geos2():
    '''Check 'all' geo_inputs are consistent in generator, key and attr.'''
    generator = bdft.generate(geo_inputs=True)
    all_1 = bdft.geo_inputs['all']
    all_2 = bdft.geos_all
    ##for geo_input1, geo_input2, geo_input3 in zip(
    ##    generator, bdft.geo_inputs['all'], bdft.geos_all):
    for geo_input1, geo_input2, geo_input3 in zip(generator, all_1, all_2):
        nt.assert_equal(geo_input1, geo_input2)
        nt.assert_equal(geo_input2, geo_input3)
        nt.assert_equal(geo_input1, geo_input3)


def test_BaseDefaults_generate_geos3():
    '''Check .generate combines multiple keys.'''
    # ['0-0-2000', '1000-0-0', '600-0-800', '500-500-0', '400-[200]-800']
    generator = bdft.generate(selection=['special', 'standard'], geo_inputs=True)
    list_by_key = []
    list_by_attr = []
    list_by_key.extend(bdft.geo_inputs['special'])
    list_by_key.extend(bdft.geo_inputs['standard'])
    list_by_attr.extend(bdft.geos_special)
    list_by_attr.extend(bdft.geos_standard)
    #print(list_by_key)
    #print(list_by_attr)
    for geo_input1, geo_input2, geo_input3 in zip(generator, list_by_key, list_by_attr):
        #print(geo_input1)
        nt.assert_equal(geo_input1, geo_input2)
        nt.assert_equal(geo_input2, geo_input3)
        nt.assert_equal(geo_input1, geo_input3)


def test_BaseDefaults_generate_geo5():
    '''Check TypeError is consumed if invalid None key given to geos_input dict.'''
    gen = bdft.generate(selection=None, geo_inputs=True)
    actual = list(gen)
    expected = bdft.geo_inputs['all']
    nt.assert_equal(actual, expected)


@nt.raises(KeyError)
def test_BaseDefaults_generate_geo5():
    '''Check KeyError is raised is key is not found in geos_input dict.'''
    gen = bdft.generate(selection=['invalid-key'], geo_inputs=True)
    actual = list(gen)
    expected = ['400-200-800', '400-[200]-800', '400-200-400S']
    nt.assert_equal(actual, expected)


# FeatureInput Methods
def test_BaseDefaults_helper_convertmatparams_none():
    ##standard_form = {
    ##    'Modulus': {'PSu': 2.7e9, 'HA': 5.2e10},
    ##    'Poissons': {'PSu': 0.33, 'HA': 0.25}
    ##}                                                      # unused
    mat_props = None
    actual = bdft._convert_material_parameters(mat_props)
    expected = {}
    nt.assert_equal(actual, expected)


def test_BaseDefaults_helper_convertmatparams_default():
    '''Confirm function handles Standard Form, mat_props, nested dict.'''
    standard_form = {
        'Modulus': {'PSu': 2.7e9, 'HA': 5.2e10},
        'Poissons': {'PSu': 0.33, 'HA': 0.25}
    }
    mat_props = {
        'Modulus': {'PSu': 2.7e9, 'HA': 5.2e10},
        'Poissons': {'PSu': 0.33, 'HA': 0.25}
    }                                                      # explicit copy
    actual = bdft._convert_material_parameters(mat_props)
    expected = standard_form
    nt.assert_equal(actual, expected)


def test_BaseDefaults_helper_convertmatparams_conversion():
    '''Confirm function handles converstion to Standard From from Quick Form.'''
    standard_form = {
        'Modulus': {'PSu': 2.7e9, 'HA': 5.2e10},
        'Poissons': {'PSu': 0.33, 'HA': 0.25}
    }
    mat_props = {
        'HA': [5.2e10, 0.25],
        'PSu': [2.7e9, 0.33],
    }
    actual = bdft._convert_material_parameters(mat_props)
    expected = standard_form
    nt.assert_equal(actual, expected)


@nt.raises(TypeError)
def test_BaseDefaults_helper_convertmatparams_nondict():
    '''Handles TypeError if non-dict is passed into helper function.'''
    standard_form = {
        'Modulus': {'PSu': 2.7e9, 'HA': 5.2e10},
        'Poissons': {'PSu': 0.33, 'HA': 0.25}
    }
    mat_props = [
        'HA', [5.2e10, 0.25],
        'PSu', [2.7e9, 0.33],
    ]                                                      # incorrect, non-dict
    actual = bdft._convert_material_parameters(mat_props)
    expected = standard_form
    nt.assert_equal(actual, expected)


def test_BaseDefaults_helper_tostandarddict_():
    '''Check helper function converts a general dict to standard form.'''
    params1 = {'matl1': [1.0, 0.1],
               'matl2': [2.0, 0.2],
               'matl3': [3.0, 0.3]}

    actual = bdft._to_standard_dict(params1,
                                    mat_properties=['prop1', 'prop2'])
    # Add default property columns to nested dicts
    expected = {'prop1': {'matl1': 1.0, 'matl2': 2.0, 'matl3': 3.0},
                'prop2': {'matl1': 0.1, 'matl2': 0.2, 'matl3': 0.3}}
    nt.assert_equal(actual, expected)


def test_BaseDefaults_helper_getmaterials1():
    '''Check helper function extracts and returns list of material from mat_props.'''
    # Should handle quick and standard forms
    quick_form = {
        'HA': [5.2e10, 0.25],
        'PSu': [2.7e9, 0.33]
    }
    standard_form = {
        'Modulus': {'HA': 52000000000.0, 'PSu': 2700000000.0},
        'Poissons': {'HA': 0.25, 'PSu': 0.33}
    }

    forms = [standard_form, quick_form]

    # When no overriding list is None
    for mat_props in forms:
        actual = bdft.get_materials(mat_props)
        ##actual = bdft.get_materials(mmat_props, lst_materials=None)
        expected = ['HA', 'PSu']
        nt.assert_equal(actual, expected)


@nt.raises(TypeError)
def test_BaseDefaults_helper_getmaterials2():
    '''Check helper function raise TypeError when non-list passed to kwarg.'''
    # Should handle quick and standard forms
    mat_props = {'Modulus': {'HA': 52000000000.0, 'PSu': 2700000000.0},
                 'Poissons': {'HA': 0.25, 'PSu': 0.33}}

    # When no overriding list is None
    actual = bdft.get_materials(mat_props, lst_materials={'PSu': 0.3, 'HA': 0.2})
    expected = ['dummy']
    nt.assert_equal(actual, expected)

# TODO: add test for subclassing basedefaults; test ability to overwrite defaults; see class Example

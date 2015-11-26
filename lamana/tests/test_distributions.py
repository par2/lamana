#------------------------------------------------------------------------------
# Confirms accurate execution of building cases

import copy
import itertools as it

import nose.tools as nt 

import pandas as pd

import lamana as la
from lamana.input_ import BaseDefaults
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt                 # for post Laminate, i.e. Cases only

# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {'R' : 12e-3,                                # specimen radius
              'a' : 7.5e-3,                                # support ring radius
              'p' : 4,                                     # points/layer
              'P_a' : 1,                                   # applied load 
              'r' : 2e-4,                                  # radial distance from center loading
              }

mat_props = {'HA' : [5.2e10, 0.25],
             'PSu' : [2.7e9, 0.33],            
             }
mat_props2 = {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9, 'dummy': 1.0e9},
              'Poissons': {'HA': 0.25, 'PSu': 0.33, 'dummy': 0.5}}

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

bdft = BaseDefaults()
case1 = la.distributions.Case(load_params, mat_props) 
case2 = la.distributions.Case(load_params, mat_props)       
case3 = la.distributions.Case(load_params, mat_props2)

# Material Order
# Homogenous
expected1 = [['HA'],
             ['HA', 'HA'],
             ['HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA', 'HA', 'HA'],
             ['HA', 'HA', 'HA'],
           ]

# Biphasic
expected2 = [['PSu'],
             ['PSu', 'HA'],
             ['PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'PSu', 'HA', 'PSu'],
             ['PSu', 'HA', 'PSu'],
            ]

# Repeated
expected3 = [['PSu'],
             ['PSu', 'HA'],
             ['PSu', 'HA', 'HA'],
             ['PSu', 'HA', 'HA', 'PSu'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu', 'HA', 'HA'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA', 'HA', 'PSu'],
             ['PSu', 'HA', 'HA', 'PSu'],
             ['PSu', 'HA', 'HA', 'PSu', 'HA'],
             ['PSu', 'HA', 'HA'],
            ]

# Multi-phasic
expected4 = [['PSu'],
             ['PSu', 'HA'],
             ['PSu', 'HA', 'dummy'],
             ['PSu', 'HA', 'dummy', 'PSu'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu', 'HA'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA', 'dummy', 'PSu'],
             ['PSu', 'HA', 'dummy', 'PSu'],
             ['PSu', 'HA', 'dummy', 'PSu', 'HA'],
             ['PSu', 'HA', 'dummy'],
            ] 

# TESTS -----------------------------------------------------------------------
# -----------------------------------------------------------------------------
#  CASE
# -----------------------------------------------------------------------------
@nt.raises(TypeError)
def test_emptyCase1():
    '''If no parameters passed to Case(), raise TypeError'''
    case0 = la.distributions.Case()    
    
def test_Case_parameters1():
    '''Confirm dict inputs (static data).'''
    actual = case1.load_params
    expected  = {'P_a': 1, 'R': 0.012, 'a': 0.0075, 
                 'p': 4, 'r': 2e-4}
    nt.assert_equal(actual, expected) 

'''Test load parameters Series equality'''
# Case attributes
# Using a sampling of geometries 
def test_Case_material_order0():
    '''Check property setter; materials changes the _material attribute.'''
    case2.materials = ['PSu', 'HA']
    actual = case2._materials 
    expected = case2.materials
    nt.assert_equal(actual, expected)
    
def test_Case_materials_order1():
    '''Check homogenous laminate gives same material.'''
    case2.materials = ['HA']                               # set order
    case2.apply(bdft.geos_sample)
    for snap, e in zip(case2.snapshots, expected1):        # truncates to expected list
        actual = snap['matl'].tolist()
        #print(actual)
        nt.assert_equal(actual, e)

def test_Case_materials_order2():
    '''Check material setting of biphasic laminate in snapshots.'''
    case2.materials = ['PSu', 'HA']                        # set order
    case2.apply(bdft.geos_sample)
    actual1 = case2.materials
    expected = case2._materials
    for snap, e in zip(case2.snapshots, expected2):        # truncates to expected list
        actual2 = snap['matl'].tolist()
        #print(actual2)
        nt.assert_equal(actual1, expected)
        nt.assert_equal(actual2, e)     

def test_Case_materials_order3():
    '''Check order for repeated materials.'''
    case2.materials = ['PSu', 'HA', 'HA']                  # set order
    case2.apply(bdft.geos_sample)
    actual1 = case2.materials
    expected = case2._materials
    for snap, e in zip(case2.snapshots, expected3):        # truncates to expected list
        actual2 = snap['matl'].tolist()
        #print(actual2)
        nt.assert_equal(actual1, expected)        
        nt.assert_equal(actual2, e)    
    #print(case2.snapshots[-1])
    
def test_Case_materials_order4():
    '''Check multi-phase laminate, matl > 2, cycles through list.'''
    case3.materials = ['PSu', 'HA', 'dummy']               # set order
    case3.apply(bdft.geos_sample)
    for snap, e in zip(case3.snapshots, expected4):        # truncates to expected list
        actual = snap['matl'].tolist()
        #print(actual)
        nt.assert_equal(actual, e)  
    
@nt.raises(NameError)
def test_Case_materials_order5():
    '''Check error is thrown if materials are not found inmat_props.'''
    case2.materials = ['PSu', 'HA', 'dummy']               # set order
    case2.apply(bdft.geos_sample)
    for snap, e in zip(case2.snapshots, expected2):        # truncates to expected list
        actual = snap['matl'].tolist()
        nt.assert_equal(actual, e)   

def test_Case_properties1():
    '''Confirm dict conversion to dataframe (static data) and values.'''
    d = {'Modulus'  : pd.Series([52e9,2.7e9], index=['HA', 'PSu']),
         'Poissons' : pd.Series([0.25, 0.33], index=['HA', 'PSu'])}
    expected = all(pd.DataFrame(d))
    actual = all(case1.properties)
    nt.assert_equal(actual, expected)  
        
def test_Case_properties2():
    '''Check the order of the properties DataFrame when materials is reset.'''
    expected = ['PSu', 'HA']
    case2.materials = expected                             # set order
    case2.apply(bdft.geos_standard)
    actual = case2.properties.index.tolist()               # truncates to expected list
    #print(actual)
    nt.assert_equal(actual, expected)  

def test_Case_compare1():
    '''Check __eq__, __ne__ of case.'''
    case1 = la.distributions.Case(dft.load_params, dft.mat_props)
    case2 = la.distributions.Case(dft.load_params, dft.mat_props)
    case3 = la.distributions.Case(dft.load_params, dft.mat_props)
    case1.apply(dft.geos_most)
    case2.apply(dft.geos_most)
    case3.apply(dft.geos_standard)
    
    expected = case1
    actual1 = case2
    actual2 = case3
    #print(actual1)
    #print(actual2) 
    nt.assert_equal(actual1, expected)
    nt.assert_not_equal(actual2, expected)    
    
# Test Case().apply() properties
# The following use the same geos
case1.apply(geos_full)

def test_Case_apply_middle1():
    '''Check output for middle layer.'''
    #case1.apply(geos_full) 
    actual = case1.middle
    expected = [2000.0, 0.0, 800.0, 0.0, 800.0, 400.0, 800.0, 800.0, 400.0]
    nt.assert_equal(actual, expected) 

def test_Case_apply_inner1():
    '''Check output for inner layer.'''
    #case1.apply(geos_full) 
    actual = case1.inner
    expected = [[0.0], [0.0], [0.0],[500.0], [200.0], 
                [200.0], [200.0], [100.0, 100.0], [100.0, 100.0]]
    nt.assert_equal(actual, expected) 

def test_Case_apply_outer1():
    '''Check output for inner layer.'''
    #case1.apply(geos_full) 
    actual = case1.outer
    expected = [0.0, 1000.0, 600.0, 500.0, 400.0,
                400.0, 400.0, 400.0, 400.0]
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_index1():
    '''Check list indexing of the last index.'''
    #case1.apply(geos_full) 
    actual = case1.inner[-1]
    expected = [100.0, 100.0]
    nt.assert_equal(actual, expected) 

def test_Case_apply_index2():
    '''Check list indexing of the last element.'''
    #case1.apply(geos_full) 
    actual = case1.inner[-1][-1]
    expected = 100.0
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_iterate1():
    '''Check iterating indexed list; first element of every inner_i.'''
    #case1.apply(geos_full) 
    actual = [first[0] for first in case1.inner]
    expected = [0.0, 0.0, 0.0, 500.0, 200.0, 200.0, 200.0, 100.0, 100.0]
    nt.assert_equal(actual, expected) 

def test_Case_apply_iterate2():
    '''Check iterating indexed list; operate on last element of every inner_i.'''
    #case1.apply(geos_full) 
    actual = [inner_i[-1]/2.0 for inner_i in case1.total_inner_i]
    expected = [0.0, 0.0, 0.0, 500.0, 200.0, 200.0, 200.0, 100.0, 100.0]
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_total1():
    '''Calculate total thicknesses (all).'''
    actual = case1.total
    expected = [2000.0, 2000.0, 2000.0, 2000.0, 2000.0,
                2000.0, 2000.0, 2000.0, 2000.0]
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_total2():
    '''Calculate total middle layer thicknesses; all.'''
    actual = case1.total_middle
    expected = [2000.0, 0.0, 800.0, 0.0, 800.0, 800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_total3():
    '''Calculate total inner layer thicknesses; all.'''
    actual = case1.total_inner
    expected =  [0.0, 0.0, 0.0, 1000.0, 400.0, 400.0, 400.0, 400.0, 400.0]
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_total4():
    '''Calculate total of each inner_i layer thicknesses; all.'''
    actual = case1.total_inner_i
    expected = [[0.0], [0.0], [0.0], [1000.0], [400.0],
                [400.0], [400.0], [200.0, 200.0], [200.0, 200.0]]
    nt.assert_equal(actual, expected) 
    
def test_Case_apply_total5():
    '''Calculate total outer layer thicknesses; all.'''
    actual = case1.total_outer
    expected = [0.0, 2000.0, 1200.0, 1000.0, 800.0, 800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected) 

def test_Case_apply_slice1():
    '''Check list slicing of total thicknesses.'''
    #case1.apply(geos_full) 
    actual = case1.total_outer[4:-1]         
    expected = [800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected) 

def test_Case_apply_unique1():
    '''Check getting a unique set of LaminateModels when unique=True.'''
    actual = la.distributions.Case(dft.load_params, dft.mat_props)
    actual.apply(['400-[200]-800'])
    expected = la.distributions.Case(dft.load_params, dft.mat_props)
    expected.apply(['400-200-800', '400-[200]-800'], unique=True)
    nt.assert_equal(actual, expected)

def test_Case_apply_unique2():
    '''Check getting a unique set of LaminateModels when unique=False.'''
    actual = la.distributions.Case(dft.load_params, dft.mat_props)
    actual.apply(['400-[200]-800', '400-[200]-800'])
    expected = la.distributions.Case(dft.load_params, dft.mat_props)
    expected.apply(['400-200-800', '400-[200]-800'], unique=False)
    nt.assert_equal(actual, expected)    

@nt.raises(AssertionError)
def test_Case_apply_unique3():
    '''Check exception if comparing inaccurately LaminateModels when unique is False.'''
    actual = la.distributions.Case(dft.load_params, dft.mat_props)
    actual.apply(['400-[200]-800'])                   # wrong actual
    expected = la.distributions.Case(dft.load_params, dft.mat_props)
    expected.apply(['400-200-800', '400-[200]-800'], unique=False)
    nt.assert_equal(actual, expected)  

def test_Case_apply_unique4():
    '''Check unique word skips iterating same geo strings; gives only one.'''
    standards = ['400-200-800', '400-[200]-800',
                 '400-200-800', '400-[200]-800',
                 '400-200-800', '400-[200]-800',
                 '400-200-800', '400-[200]-800',]
    case1 = la.distributions.Case(dft.load_params, dft.mat_props)
    case2 = la.distributions.Case(dft.load_params, dft.mat_props)
    actual = case1.apply(standards, unique=True)
    expected = case2.apply(['400-[200]-800'])
    nt.assert_equal(actual, expected)
    
# Case refactor 0.4.5a1
def test_Case_apply_reapply():
    '''Check same result is returned by calling apply more than once.'''
    case1 = la.distributions.Case(dft.load_params, dft.mat_props)
    case1.apply(['400-[200]-800', '400-[200]-800', '100-200-1400'])
    case1.total_outer[1:-1]
    case1.apply(['400-[200]-800', '400-[200]-800', '100-200-1400'])
    case1.total_outer[1:-1]
    case1.apply(['400-[200]-800', '400-[200]-800', '100-200-1400'])
    actual = case1.total_outer
    expected = [800.0, 800.0, 200.0]
    nt.assert_equal(actual, expected)


    
# Laminate Structure ----------------------------------------------------------
#Test LaminateModels
def test_Case_apply_Snapshots1():
    '''Test the native DataFrame elements and dtypes. Resorts columns.  Uses pandas equals test.'''
    case1.apply(geos_full)
    cols = ['layer', 'matl', 'type', 't(um)']
    d = {'layer': [1,2,3,4,5,6,7],
         'matl' : ['HA','PSu','HA','PSu','HA','PSu','HA'],
         'type' : ['outer','inner','inner','middle','inner','inner','outer'],
         't(um)' : [400.0,100.0,100.0,800.0,100.0,100.0,400.0]}
    
    actual = case1.snapshots[8]
    expected = pd.DataFrame(d)
#     bool_test = actual[cols].sort(axis=1).equals(expected.sort(axis=1))
#     #nt.assert_equal(bool_test, True)
#     nt.assert_true(bool_test)
    ut.assertFrameEqual(actual[cols], expected[cols])
    
def test_Case_apply_LaminateModels1():
    '''Test the native DataFrame elements and dtypes. Resorts columns.
    Uses pandas equals() test.  p is even.'''
    case1.apply(geos_full)
    d = {'layer': [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7],
         'matl' : ['HA','HA','HA','HA',
                   'PSu','PSu','PSu','PSu',
                   'HA','HA','HA','HA',
                   'PSu','PSu','PSu','PSu',
                   'HA','HA','HA','HA',
                   'PSu','PSu','PSu','PSu',
                   'HA','HA','HA','HA'],
         'type' : ['outer','outer','outer','outer',
                   'inner','inner','inner','inner',
                   'inner','inner','inner','inner',
                   'middle','middle','middle','middle',
                   'inner','inner','inner','inner',
                   'inner','inner','inner','inner',
                   'outer','outer','outer','outer'],
         't(um)': [400.0,400.0,400.0,400.0,
                   100.0,100.0,100.0,100.0,
                   100.0,100.0,100.0,100.0,
                   800.0,800.0,800.0,800.0,
                   100.0,100.0,100.0,100.0,
                   100.0,100.0,100.0,100.0,
                   400.0,400.0,400.0,400.0]}
    cols = ['layer', 'matl', 'type', 't(um)']
    actual = case1.frames[8][cols]
    expected = pd.DataFrame(d)
    #print(case1.materials)
    #print(actual)
    #print(expected)
#     bool_test = actual.sort(axis=1).equals(expected.sort(axis=1))
#     #nt.assert_equal(bool_test, True)
#     nt.assert_true(bool_test)
    ut.assertFrameEqual(actual, expected)
    
# DataFrames ------------------------------------------------------------------  
# Test p    
'''Building expected DataFrames for tests can be tedious.  The following
functions help to build DataFrames for any p, i.e. the number 
of replicated rows within each layer.'''


def replicate_values(dict_, dict_keys=[], multiplier=1):
    '''Read starter dict values and returns a dict with p replicated values.
    
    Example
    =======
    >>> d1 = {'layer' : [1,],
              'matl'  : ['HA',],
              'type'  : ['middle'],
              't(um)' : [2000.0,]}
    >>> keys = ['layer', 'matl', 'type', 't(um)']          # columns to iterate
    >>> replicate_values(d1, dict_keys=keys, multiplier=2)
    [{'layer': [1, 1]},
     {'matl': ['HA', 'HA']},
     {'type': ['middle', 'middle']},
     {'t(um)': [2000.0, 2000.0]}]
    
    '''
    # Repeats items in a list p times; hacker trick
    result = [{key :[val for val in value for _ in [value]*multiplier]}
              for key, value in dict_.items() for _ in [value]]
    
    # Order the list of dicts by dict_keys
    reordered_result = []
    for key in dict_keys:
        for dict_ in result:
            #print(dict_.keys())
            if key in dict_.keys():
                reordered_result.append(dict_)    
    
    # Merge separate dicts into one dict
    new_dict = {}
    for d in reordered_result:
        new_dict.update(d)
    
    return new_dict

def make_dfs(dicts, dict_keys=None, p=1):
#def make_dfs(dicts, dict_keys=[], p=1):
    '''Call replicate_values() to return a list of custom DataFrames with p
    number of repeated values.
    
    Example
    =======
    >>>dicts = [d1, ..., dn]
    >>>build_dfs(dicts, dict_keys=keys, p=2)
    [   layer matl  t(um)    type
     0      1   HA   2000  middle
     1      1   HA   2000  middle,
     ...
    
    '''
    if dict_keys is None:
        dict_keys = []
    dfs = []    
    for dict_ in dicts:
        #print(dict_)
        result = replicate_values(dict_, dict_keys=dict_keys, multiplier=p)
        dfs.append(pd.DataFrame(result))
    return dfs

# Starter dicts
'''These dicts are for p=1.  These are used to build dicts of any p.'''

d1 = {'layer' : [1,],
      'matl'  : ['HA',],
      'type'  : ['middle'],
      't(um)' : [2000.0,]}

d2 = {'layer' : [1,2,],
      'matl'  : ['HA',
                 'PSu',],
      'type'  : ['outer',
                 'outer',],
      't(um)' : [1000.0,
                 1000.0,]}
d3 = {'layer' : [1,2,3,],
      'matl'  : ['HA',
                 'PSu',
                 'HA',],
      'type'  : ['outer',
                 'middle',
                 'outer',],
      't(um)' : [600.0,
                 800.0,
                 600.0,]}

d4 = {'layer' : [1,2,3,4,],
      'matl'  : ['HA',
                 'PSu',
                 'HA',
                 'PSu',],
      'type'  : ['outer',
                 'inner',
                 'inner',
                 'outer',],
      't(um)' : [500.0,
                 500.0,
                 500.0,
                 500.0,]}
        
d5 = {'layer' : [1,2,3,4,5],
      'matl'  : ['HA',
                 'PSu',
                 'HA',
                 'PSu',
                 'HA'],
      'type'  : ['outer',
                 'inner',
                 'middle',
                 'inner',
                 'outer',],
      't(um)' : [400.0,
                 200.0,
                 800.0,
                 200.0,
                 400.0,]}
d8 = {'layer' : [1,2,3,4,5,6,7],
      'matl'  : ['HA',
                'PSu',
                'HA',
                'PSu',
                'HA',
                'PSu',
                'HA'],
      'type' : ['outer',
                'inner',
                'inner',
                'middle',
                'inner',
                'inner',
                'outer',],
      't(um)' : [400.0,  
                 100.0,
                 100.0,
                 800.0,
                 100.0,
                 100.0,
                 400.0,]}

#------------------------------------------------------------------------------
def test_apply_LaminateModels_frames_p1():
    '''Check built DataFrames have correct p for each Lamina.
    
    Using two functions to build DataFrames: make_dfs() and replicate_values().  
    This only tests four columns  ['layer', 'matl', 'type', 't(um)'].
    Be sure to test single, odd and even p, i.e. p = [1, 3, 4].
        
        1. Access DataFrames from laminate using frames
        2. Build dicts and expected dataframes for a range of ps
        3. Equate the dataframes and assert the truth of elements.
    
    UPDATE: the following functions should not be used.  makes_dfs is recommended
    for future tests.  
    '''
    def make_actual_dfs(geos, p=1):
        '''Returns a list of DataFrames using the API '''
        load_params['p'] = p
        #print(load_params)
        case = la.distributions.Case(load_params, mat_props) 
        case.apply(geos) 
        #print(case.frames)
        return case.frames

    def make_expected_dfs(starter_dicts, keys, p=1):
        '''Return a list of custom DataFrames with p number rows.'''
        dfs = []
        for points in range(1, p+1):                       # skips 0 (empty df)
            for dict_ in make_dfs(starter_dicts, dict_keys=keys, p=p):
                dfs.append(pd.DataFrame(dict_))
            return dfs

    # Starting inputs
    geos_custom = [g1, g2, g3, g4, g5, g8]
    dicts = [d1, d2, d3, d4, d5, d8]
    keys = ['layer', 'matl', 'type', 't(um)']
    load_params = {'R' : 12e-3,                            # specimen radius
                  'a' : 7.5e-3,                            # support ring radius
                  'p' : 4,                                 # points/layer
                  'P_a' : 1,                               # applied load 
                  'r' : 2e-4,                              # radial distance from center loading
                  }
    mat_props = {'HA' : [5.2e10, 0.25],
                 'PSu' : [2.7e9, 0.33],            
                 }
    p_range = 5                                            # test 1 to this number rows

    for n in range(1, p_range):
        actual = make_actual_dfs(geos_custom, p=n)
        expected = make_expected_dfs(dicts, keys, p=n) 
        #print(type(expected))

    # Test all values in DataFrames are True (for column in keys)
        for i, df in enumerate(expected):
            #print(bool_test)
            #assert bool_test == True, 'False elements detected'  
            #bool_test = actual[i][keys].sort(axis=1).equals(expected[i].sort(axis=1))
            #nt.assert_equal(bool_test, True) 
            #nt.assert_true(bool_test)
            ut.assertFrameEqual(actual[i][keys], expected[i])
            
# Test stress sides
def test_apply_LaminateModels_side_p1():
    '''Check None is assigned in the middle for LaminateModels with odd rows.'''
    load_params = {'R' : 12e-3,                            # specimen radius
                  'a' : 7.5e-3,                            # support ring radius
                  'p' : 3,                                 # points/layer
                  'P_a' : 1,                               # applied load 
                  'r' : 2e-4,                              # radial distance from center loading
                }
    case = la.distributions.Case(load_params, mat_props) 
    case.apply(geos_full2)
    dfs = case.frames
    #print(dfs)
    
    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index)//2
        #print(half_the_stack)
        if 'None' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])  # None at the middle of odd rows
            #print(df['side'])
        if len(df.index)%2 != 0:
            expected.append('None')
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)

def test_apply_LaminateModels_side_p2():
    '''Check None is not in the DataFrame having even rows.'''
    load_params = {'R' : 12e-3,                            # specimen radius
                  'a' : 7.5e-3,                            # support ring radius
                  'p' : 8,                                 # points/layer
                  'P_a' : 1,                               # applied load 
                  'r' : 2e-4,                              # radial distance from center loading
                }
    case = la.distributions.Case(load_params, mat_props) 
    case.apply(geos_full2)
    dfs = case.frames
    #print(dfs)
    
    actual = []
    expected = []
    for df in dfs:
        if 'None' not in df['side'].values:
            actual.append(True)     
        expected.append(True)
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)

def test_apply_LaminateModels_INDET1():
    '''Test INDET in the middle row for p = 1, odd laminates.'''
    load_params = {'R' : 12e-3,                            # specimen radius
                  'a' : 7.5e-3,                            # support ring radius
                  'p' : 1,                                 # points/layer
                  'P_a' : 1,                               # applied load 
                  'r' : 2e-4,                              # radial distance from center loading
                 }
    case = la.distributions.Case(load_params, mat_props) 
    case.apply(geos_full2)
    dfs = case.frames
    
    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index)//2
        #print(half_the_stack)
        if 'INDET' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])
            #print(df['side'])
        if len(df.index)%2 != 0:
            expected.append('INDET')
    #print(df)
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)

def test_apply_LaminateModels_INDET2():
    '''Test INDET in the middle rows for p = 1, odd laminates.'''
    load_params = {'R' : 12e-3,                            # specimen radius
                  'a' : 7.5e-3,                            # support ring radius
                  'p' : 1,                                 # points/layer
                  'P_a' : 1,                               # applied load 
                  'r' : 2e-4,                              # radial distance from center loading
                 }
    case = la.distributions.Case(load_params, mat_props) 
    case.apply(geos_full2)
    dfs = case.frames
    
    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index)//2
        #print(half_the_stack)
        if 'INDET' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])
            #print(df['side'])
        if len(df.index)%2 != 0:
            expected.append('INDET')
    #print(df)
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)    
    
def test_apply_LaminateModels_None1():
    '''Check None is assigned in the middle for LaminateModels with odd rows.'''
    load_params = {'R' : 12e-3,                            # specimen radius
                  'a' : 7.5e-3,                            # support ring radius
                  'p' : 3,                                 # points/layer
                  'P_a' : 1,                               # applied load 
                  'r' : 2e-4,                              # radial distance from center loading
                }
    case = la.distributions.Case(load_params, mat_props) 
    case.apply(geos_full2)
    dfs = case.frames
    #print(dfs)
    
    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index)//2
        #print(half_the_stack)
        if 'None' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])
            #print(df['side'])
        if len(df.index)%2 != 0:
            expected.append('None')
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


#------------------------------------------------------------------------------      
# CASES
#------------------------------------------------------------------------------  
dft = wlt.Defaults()
load_params = copy.deepcopy(dft.load_params)
#load_params = dft.load_params

# Manual and Auto Cases for Attribute Tests
cases1a = la.distributions.Cases(dft.geo_inputs['5-ply'], ps=[2,3,4])    
cases1b = la.distributions.Cases(dft.geo_inputs['5-ply'], ps=[2,3,4])     
#cases1a = Cases(dft.geo_inputs['5-ply'], ps=[2,3,4])     # assumes Defaults
#cases1b = Cases(dft.geo_inputs['5-ply'], ps=[2,3,4])     # assumes Defaults
load_params['p'] = 2
cases1c = la.distributions.Case(load_params, dft.mat_props)
cases1c.apply(dft.geo_inputs['5-ply'])

# Manual Cases for Selection Tests
cases2a = la.distributions.Cases(dft.geos_special, ps=[2,3,4])
#cases2a = Cases(dft.geos_special, ps=[2,3,4])
load_params['p'] = 2
cases2b2 = la.distributions.Case(load_params, dft.mat_props)
cases2b2.apply(dft.geos_special) 
load_params['p'] = 3
cases2b3 = la.distributions.Case(load_params, dft.mat_props) 
cases2b3.apply(dft.geos_special)
load_params['p'] = 4
cases2b4 = la.distributions.Case(load_params, dft.mat_props) 
cases2b4.apply(dft.geos_special)  

# Manual for mixed geometry string inputs
mix = dft.geos_most + dft.geos_standard                   # 400-[200]-800 common to both 
cases3a = la.distributions.Cases(mix, unique=True)
#cases3a = Cases(mix, unique=True)
load_params['p'] = 5
cases3b5 = la.distributions.Case(load_params, dft.mat_props)
cases3b5.apply(mix) 

def test_Cases_attr_len1():
    '''Check __len__ of all cases contained in cases.'''
    actual1 = cases1a.__len__()
    actual2 = len(cases1a)
    ps = {case.p for case in cases1a}
    ncases = len(dft.geo_inputs['5-ply'])*len(ps)
    expected = ncases
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)
    
def test_Cases_attr_get1():
    '''Check __getitem__ of all cases contained in cases.'''
    actual1 = cases1a.__getitem__(0)
    actual2 = cases1a.get(0)
    actual3 = cases1a[0]
    expected = cases1b[0]
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)    
    nt.assert_equal(actual3, expected) 
    
@nt.raises(KeyError)
def test_Cases_attr_get2():
    '''Check __getitem__ of non-item in cases.'''
    actual1 = cases1a[300]
    expected = 'dummy'
    nt.assert_equal(actual1, expected)

@nt.raises(NotImplementedError)
def test_Cases_attr_set1():
    '''Check __setitem__ is not implemented.'''
    actual1 = cases1a[2] = 'test'
    expected = NotImplemented
    nt.assert_equal(actual1, expected)

def test_Cases_attr_del1():
    '''Check __del__ of all cases contained in cases.'''
    cases = cases1b
    del cases[1]
    actual1 = len(cases)
    ps = {case.p for case in cases1a}
    ncases = len(dft.geo_inputs['5-ply'])*len(ps)
    expected = ncases - 1
    nt.assert_equal(actual1, expected)

def test_Cases_prop_LMs1():
    '''Check viewing inside cases gives correct list.'''
    actual1 = cases1a.LMs
    # Manual cases
    load_params['p'] = 2
    cases1c2 = la.distributions.Case(load_params, dft.mat_props)
    cases1c2.apply(dft.geo_inputs['5-ply']) 
    load_params['p'] = 3
    cases1c3 = la.distributions.Case(load_params, dft.mat_props) 
    cases1c3.apply(dft.geo_inputs['5-ply'])
    load_params['p'] = 4
    cases1c4 = la.distributions.Case(load_params, dft.mat_props) 
    cases1c4.apply(dft.geo_inputs['5-ply'])  
    expected = cases1c2.LMs + cases1c3.LMs + cases1c4.LMs 
    #print(cases1a2)
    #print(cases1a3)
    #print(cases1a4)
    #print(expected)
    nt.assert_equal(actual1, expected)    

# Cases selections
def test_Cases_prop_select1():
    '''Check output of select method; single nplies only.'''
    actual = cases2a.select(nplies=4)  
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                      cases2b4.LMs) if LM.nplies == 4}
    nt.assert_set_equal(actual, expected)
    
def test_Cases_prop_select2():
    '''Check output of select method; single ps only.'''
    actual = cases2a.select(ps=3) 
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                      cases2b4.LMs) if LM.p == 3}
    nt.assert_set_equal(actual, expected)
    
def test_Cases_prop_select3():
    '''Check output of select method; nplies only.'''
    actual = cases2a.select(nplies=[2,4])  
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                      cases2b4.LMs) if LM.nplies in (2, 4)}
    nt.assert_set_equal(actual, expected)
    
def test_Cases_prop_select4():
    '''Check output of select method; ps only.'''
    actual = cases2a.select(ps=[2,4]) 
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                      cases2b4.LMs) if LM.p in (2, 4)}
    nt.assert_set_equal(actual, expected)
    
# Cases cross selections
def test_Cases_prop_crossselect1():
    '''Check (union) output of select method; single nplies and ps.'''
    actual1 = cases2a.select(nplies=4, ps=3)  
    actual2 = cases2a.select(nplies=4, ps=3, how='union') 
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                       cases2b4.LMs) if (LM.nplies == 4) | (LM.p == 3)}
    nt.assert_set_equal(actual1, expected)
    nt.assert_set_equal(actual2, expected)
    
def test_Cases_prop_crossselect2():
    '''Check (intersection) output of select method; single nplies and ps.'''
    actual = cases2a.select(nplies=4, ps=3, how='intersection') 
    expected1 = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                       cases2b4.LMs) if (LM.nplies == 4) & (LM.p == 3)}
    expected2 = {cases2b3.LMs[-1]}
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)
    
def test_Cases_prop_crossselect3():
    '''Check (difference) output of select method; single nplies and ps.'''
    actual = cases2a.select(nplies=4, ps=3, how='difference')
    expected1 = cases2a.select(ps=3) -  cases2a.select(nplies=4)
    expected2 = set(cases2b3.LMs[:-1])
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)
    
def test_Cases_prop_crossselect4():
    '''Check (symmetric difference) output of select method; single nplies and ps.'''
    actual = cases2a.select(nplies=4, ps=3, how='symmetric difference') 
    expected1 = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                       cases2b4.LMs) if (LM.nplies == 4) ^ (LM.p == 3)}
    list_p3 = list(cases2b3.LMs[:-1])                  # copy list
    list_p3 .append(cases2b2.LMs[-1])
    list_p3 .append(cases2b4.LMs[-1])
    expected2 = set(list_p3) 
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)
    
def test_Cases_prop_crossselect5():
    '''Check (union) output of select method; multiple nplies and ps.'''
    actual1 = cases2a.select(nplies=[2,4], ps=[3,4])  
    actual2 = cases2a.select(nplies=[2,4], ps=[3,4], how='union') 
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                       cases2b4.LMs) if (LM.nplies in (2,4)) | (LM.p in (3,4))}
    nt.assert_set_equal(actual1, expected)
    nt.assert_set_equal(actual2, expected)
    
def test_Cases_prop_crossselect6():
    '''Check (intersection) output of select method; multiple nplies and ps.'''
    actual = cases2a.select(nplies=[2,4], ps=[3,4], how='intersection') 
    expected1 = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                       cases2b4.LMs) if (LM.nplies in (2,4)) & (LM.p in (3,4))}
    nt.assert_set_equal(actual, expected1)
    
def test_Cases_prop_crossselect7():
    '''Check (difference) output of select method; multiple nplies and single ps.'''
    # Subtracts nplies from ps.
    actual = cases2a.select(nplies=[2,4], ps=3, how='difference')
    expected1 = cases2a.select(ps=3) - cases2a.select(nplies=[2,4])
    expected2 = set(cases2b3.LMs[::2])
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)
    
def test_Cases_prop_crossselect8():
    '''Check (symmetric difference) output of select method; single nplies, multi ps.'''
    actual = cases2a.select(nplies=4, ps=[3,4], how='symmetric difference') 
    expected1 = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                       cases2b4.LMs) if (LM.nplies == 4) ^ (LM.p in (3,4))}
    nt.assert_set_equal(actual, expected1)
    

# This section is dedicated to Cases() tests primarily from 0.4.4b3
str_caselets = ['350-400-500',  '400-200-800', '400-[200]-800']
list_caselets = [['400-400-400', '400-[400]-400'],
                 ['200-100-1400', '100-200-1400',], 
                 ['400-400-400', '400-200-800','350-400-500',], 
                 ['350-400-500']] 
case_1 = la.distributions.Case(dft.load_params, dft.mat_props)
case_2 = la.distributions.Case(dft.load_params, dft.mat_props)
case_3 = la.distributions.Case(dft.load_params, dft.mat_props)
case_1.apply(['400-200-800', '400-[200]-800'])
case_2.apply(['350-400-500', '400-200-800'])
case_3.apply(['350-400-500', '400-200-800', '400-400-400'])
case_caselets = [case_1, case_2, case_3]

def test_Cases_caselets1():
    '''Check cases from caselets of geometry strings.'''
    cases = la.distributions.Cases(str_caselets)
    #cases = Cases(str_caselets)
    actual = cases
    dict_expected = {}
    for i, caselet in enumerate(str_caselets):
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply([caselet])
        dict_expected[i] = case
    expected = dict_expected 
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)
    
def test_Cases_caselets2():
    '''Check cases from caselets of lists of geometry strings.'''
    cases = la.distributions.Cases(list_caselets)
    #cases = Cases(list_caselets)
    actual = cases
    dict_expected = {}
    for i, caselet in enumerate(list_caselets):
        #print(caselet)
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply(caselet)
        dict_expected[i] = case
    expected = dict_expected
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)

def test_Cases_caselets3():
    '''Check cases from caselets of cases.'''
    cases = la.distributions.Cases(case_caselets)
    #cases = Cases(case_caselets)
    actual = cases
    dict_expected = {}
    for i, caselet in enumerate(case_caselets):
        #print(caselet)
        dict_expected[i] = caselet
    expected = dict_expected
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)      
        
def test_Cases_caselets_ps1():
    '''Check strs from caselets form for each ps.'''
    cases = la.distributions.Cases(str_caselets, ps=[4,5])
    #cases = Cases(str_caselets, ps=[4,5])
    actual = cases
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    actual_ps = []
    for case in cases:
        actual_ps.append(case.p)
    actual1 = set(actual_ps)
    actual2 = len(actual_ps)
    actual3 = len(cases)
    expected1 = {4,5}
    expected2 = 6
    expected3 = 6
    nt.assert_equal(actual1, expected1) 
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)
    
#cases = Cases(list_caselets, ps=[2,3,4,5,7,9])
def test_Cases_caselets_ps2():
    '''Check cases from string caselets form for each ps.'''
    cases = la.distributions.Cases(list_caselets, ps=[4,5])
    #cases = Cases(list_caselets, ps=[4,5])
    actual = cases
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    actual_ps = []
    for case in cases:
        actual_ps.append(case.p)
    actual1 = set(actual_ps)
    actual2 = len(actual_ps)
    actual3 = len(cases)
    expected1 = {4,5}
    expected2 = 8
    expected3 = 8
    nt.assert_equal(actual1, expected1) 
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)

def test_Cases_caselets_ps3():
    '''Check cases from list caselets form for each ps.'''
    cases = la.distributions.Cases(case_caselets, ps=[2,3,4,5,7,9])
    #cases = Cases(case_caselets, ps=[2,3,4,5,7,9])
    actual = cases
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    actual_ps = []
    for case in cases:
        actual_ps.append(case.p)
    actual1 = set(actual_ps)
    actual2 = len(actual_ps)
    actual3 = len(cases)
    expected1 = {2,3,4,5,7,9}
    expected2 = 18
    expected3 = 18
    nt.assert_equal(actual1, expected1) 
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)
    
def test_Cases_keyword_combine1():
    '''Check caselets of geometry strings combine into a single case.'''
    cases = la.distributions.Cases(str_caselets, combine=True)
    #cases = Cases(str_caselets, combine=True)
    actual = cases
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(str_caselets)
    expected = {0: case}
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)    

def test_Cases_keyword_combine2():
    '''Check caselets of listed geometry strings combine into a single case.'''
    cases = la.distributions.Cases(list_caselets, combine=True)
    #cases = Cases(list_caselets, combine=True)
    actual = cases
    list_combined = ['100.0-[200.0]-1400.0' , '400.0-[400.0]-400.0', 
                     '350.0-[400.0]-500.0', '400.0-[200.0]-800.0', 
                     '200.0-[100.0]-1400.0']
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(list_combined)
    expected = {0: case}
    print(actual.LMs, expected[0].LMs)
    # Any use of set() changes order; this case _get_unique makes these dissimlar
    nt.assert_set_equal(set(actual.LMs), set(expected[0].LMs)) 
        
def test_Cases_keyword_combine3():
    '''Check caselets of cases combine into a single case.'''
    cases = la.distributions.Cases(case_caselets, combine=True)
    #cases = Cases(case_caselets, combine=True)
    actual = cases
    list_combined = ['400.0-[400.0]-400.0', '400.0-[200.0]-800.0',
                     '350.0-[400.0]-500.0',]
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(list_combined)
    expected = {0: case}
    print(actual.LMs, expected[0].LMs)
    # Any use of set() changes order; this case _get_unique makes these dissimlar
    nt.assert_set_equal(set(actual.LMs), set(expected[0].LMs)) 

@nt.raises(TypeError)
def test_Cases_keyword_combine4():
    '''Check empty caselet throw error.'''
    cases = la.distributions.Cases([], combine=True)
    #cases = Cases([], combine=True)
    actual = cases
    list_combined = ['400.0-[400.0]-400.0', '400.0-[200.0]-800.0',
                     '350.0-[400.0]-500.0',]
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(list_combined)
    expected = {0: case}
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)   

def test_Cases_keyword_unique1():
    '''Check unque keyword of string caselets; ignores singles since already unique.'''
    cases = la.distributions.Cases(str_caselets, unique=True)
    #cases = Cases(str_caselets, unique=True)
    actual = set(cases.LMs)
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['350-400-500', '400-200-800',  '400-200-800'])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected) 

def test_Cases_keyword_unique2():
    '''Check unque keyword of string caselets gives unique cases.'''
    cases = la.distributions.Cases(list_caselets, unique=True)
    #cases = Cases(list_caselets, unique=True)
    actual = set(cases.LMs)
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['400-[400]-400', '200-100-1400', '100-200-1400',
                '400-200-800','350-400-500',])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected) 
        
def test_Cases_keyword_unique3():
    '''Check unque keyword of string caselets gives unique cases.'''
    cases = la.distributions.Cases(case_caselets, unique=True)
    #cases = Cases(case_caselets, unique=True)
    actual = set(cases.LMs)
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['400-[200]-800', '350-400-500','400-400-400'])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected) 
        
def test_Cases_keyword_unique4():
    '''Check unique/combine keyword of string caselets gives unique cases; unifies singles.'''
    cases = la.distributions.Cases(str_caselets, combine=True, unique=True)
    #cases = Cases(str_caselets, combine=True, unique=True)
    actual = set(cases.LMs)
    case = la.distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['350-400-500', '400-200-800',])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected)
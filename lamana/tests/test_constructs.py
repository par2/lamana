#------------------------------------------------------------------------------
# Confirms output of general Laminate structure
'''NOTE: Refactoring in 0.4.3c5b led to patching container orders. '''

import nose.tools as nt
import pandas as pd
import numpy as np

import lamana as la
from lamana.input_ import BaseDefaults
from lamana import constructs as con
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt


bdft = BaseDefaults()
dft = wlt.Defaults()
G = la.input_.Geometry
constr = la.constructs.Laminate


# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {'R' : 12e-3,                                # specimen radius
              'a' : 7.5e-3,                                # support ring radius
              'p' : 4,                                     # points/layer
              'P_a' : 1,                                   # applied load 
              'r' : 2e-4,                                  # radial distance from center loading
              }

# # Quick Form
# mat_props = {'HA' : [5.2e10, 0.25],
#              'PSu' : [2.7e9, 0.33],            
#              }

# # Conversion to Standard Form
# mat_props = bdft._convert_material_parameters(mat_props)

mat_props = {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9}, 
             'Poissons': {'HA': 0.25, 'PSu': 0.33}}

# What geometries to test?
# Make tuples of desired geometeries to analyze: outer - {inner...-....}_i - middle

# Current Style
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
g13 = ('500-[250,250]-0')                                  # 6-ply
g14 = ('500-[50,50,50,50]-0')                              # 10-ply


geos_most = [g1, g2, g3, g4, g5]
geos_special = [g6, g7, g8, g9]
geos_full = [g1, g2, g3, g4, g5, g6, g7, g8, g9]
geos_full2 = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12]
geos_full3 = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14] 

# G = la.input_.Geometry

Geo1 = G('0-0-2000')
Geo1S = G('0-0-1000S')
Geo2 = G('1000-0-0')        
Geo3 = G('600-0-800')
Geo3S = G('600-0-400S')
Geo4 = G('500-500-0')        
Geo5 = G('400-200-800')   
Geo6 = G('400-200-400S')    
Geo7 = G('400-[200]-800') 
Geo8 = G('400-[100,100]-800')
Geo9 = G('400-[100,100]-400S')
Geo10 = G('400-[100,100,100]-800')
Geo11 = G('400-[100,100,100,100]-800')
Geo12 = G('400-[100,100,100,100,100]-800')

Geos_simple = [Geo1, Geo2, Geo3, Geo4]
Geos_symmetric = [Geo1S, Geo3S, Geo6, Geo9]
Geos_inner = [Geo7, Geo8, Geo9]
Geos_full = [Geo1, Geo2, Geo3, Geo4, Geo5, Geo6, Geo7, Geo8, Geo9]
Geos_full2 = [Geo1, Geo2, Geo3, Geo4, Geo5, Geo6, Geo7,
              Geo8, Geo9, Geo10, Geo11, Geo12]

#------------------------------------------------------------------------------
# STACK 
#------------------------------------------------------------------------------
# Decode Geometries
def test_Stack_decode_1():
    '''Check decoding and unfolding simple geometries.'''
    unfolded = [con.Stack(Geo).unfolded for Geo in Geos_simple]
    actual = unfolded
    expected = [[# Monolith
                  (0.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (2000.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'outer')[::-1]],
                # Bilayer
                 [(1000.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (1000.0, 'outer')[::-1]],
                # Trilayer
                 [(600.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (600.0, 'outer')[::-1]],
                # Quadlayer
                 [(500.0, 'outer')[::-1],
                  (500.0, 'inner')[::-1],
                  (0.0, 'middle')[::-1],
                  (500.0, 'inner')[::-1],
                  (500.0, 'outer')[::-1]],]
    nt.assert_equal(actual, expected) 

def test_Stack_decode_2():
    '''Check decoding and unfolding geometries with [inner_i].'''
    unfolded = [con.Stack(Geo).unfolded for Geo in Geos_inner]
    actual = unfolded
    expected = [[(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],]
    nt.assert_equal(actual, expected) 

def test_Stack_decode_3():
    '''Check decoding and unfolding of more geometries.'''    
    unfolded = [con.Stack(Geo).unfolded for Geo in Geos_full]
    actual = unfolded
    expected = [[(0.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (2000.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'outer')[::-1]],
                
                 [(1000.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (1000.0, 'outer')[::-1]],
                
                 [(600.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (600.0, 'outer')[::-1]],
                
                 [(500.0, 'outer')[::-1],
                  (500.0, 'inner')[::-1],
                  (0.0, 'middle')[::-1],
                  (500.0, 'inner')[::-1],
                  (500.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],]
    nt.assert_equal(actual, expected) 

def test_Stack_decode_4():
    '''Checks decoding and unfolding even more geometries.'''
    unfolded = [con.Stack(Geo).unfolded for Geo in Geos_full2]
    actual = unfolded
    expected = [[(0.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (2000.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'outer')[::-1]],
                
                 [(1000.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (1000.0, 'outer')[::-1]],
                
                 [(600.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (600.0, 'outer')[::-1]],
                
                 [(500.0, 'outer')[::-1],
                  (500.0, 'inner')[::-1],
                  (0.0, 'middle')[::-1],
                  (500.0, 'inner')[::-1],
                  (500.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]]]
    nt.assert_equal(actual, expected) 
    
def test_Stack_decode_5():
    '''Check decoding and unfolding of symmetric geometries.'''    
    unfolded = [con.Stack(Geo).unfolded for Geo in Geos_symmetric]
    actual = unfolded
    expected = [[(0.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (2000.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (0.0, 'outer')[::-1]],
                
                 [(600.0, 'outer')[::-1],
                  (0.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (0.0, 'inner')[::-1],
                  (600.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (200.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (200.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]],
                
                 [(400.0, 'outer')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (800.0, 'middle')[::-1],
                  (100.0, 'inner')[::-1],
                  (100.0, 'inner')[::-1],
                  (400.0, 'outer')[::-1]]]
    nt.assert_equal(actual, expected) 
    

# Build dicts of stacks
#stack = {layer_ : [thicness, type_ ], ...}
def test_Stack_identify1():
    '''Check building dicts for simple geometry.'''
    stacks = [con.Stack(Geo).StackTuple for Geo in Geos_simple]
    actual = stacks
    expected = [({1: [2000.0, 'middle'][::-1]},
                 1, '1-ply','Monolith'),
                 ({1: [1000.0, 'outer'][::-1],
                   2: [1000.0, 'outer'][::-1]},
                  2, '2-ply','Bilayer'),
                 ({1: [600.0, 'outer'][::-1],
                   2: [800.0, 'middle'][::-1],
                   3: [600.0, 'outer'][::-1]},
                  3, '3-ply', 'Trilayer'),
                 ({1: [500.0, 'outer'][::-1],
                   2: [500.0, 'inner'][::-1],
                   3: [500.0, 'inner'][::-1],
                   4: [500.0, 'outer'][::-1]},
                  4, '4-ply', 'Quadlayer'),]
    nt.assert_equal(actual, expected) 
    
def test_Stack_identify2():
    '''Check building dicts for inner_i geometry.'''
    stacks = [con.Stack(Geo).StackTuple for Geo in Geos_inner]
    actual = stacks
    expected = [({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [800.0, 'middle'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [400.0, 'outer'][::-1]},
                  7, '7-ply', None),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [800.0, 'middle'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [400.0, 'outer'][::-1]},
                  7, '7-ply', None)]
    nt.assert_equal(actual, expected)  
    
def test_Stack_identify3():
    '''Check building dicts for full  geometry.'''
    stacks = [con.Stack(Geo).StackTuple for Geo in Geos_full]
    actual = stacks
    expected = [({1: [2000.0, 'middle'][::-1]},
                 1, '1-ply','Monolith'),
                 ({1: [1000.0, 'outer'][::-1],
                   2: [1000.0, 'outer'][::-1]},
                  2, '2-ply','Bilayer'),
                 ({1: [600.0, 'outer'][::-1],
                   2: [800.0, 'middle'][::-1],
                   3: [600.0, 'outer'][::-1]},
                  3, '3-ply', 'Trilayer'),
                 ({1: [500.0, 'outer'][::-1],
                   2: [500.0, 'inner'][::-1],
                   3: [500.0, 'inner'][::-1],
                   4: [500.0, 'outer'][::-1]},
                  4, '4-ply', 'Quadlayer'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [800.0, 'middle'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [400.0, 'outer'][::-1]},
                  7, '7-ply', None),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [800.0, 'middle'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [400.0, 'outer'][::-1]},
                  7, '7-ply', None)]
    nt.assert_equal(actual, expected) 
    
def test_Stack_identify4():
    '''Check building dicts for full2 geometry.'''
    stacks = [con.Stack(Geo).StackTuple for Geo in Geos_full2]
    actual = stacks
    expected = [({1: [2000.0, 'middle'][::-1]},
                 1, '1-ply','Monolith'),
                 ({1: [1000.0, 'outer'][::-1],
                   2: [1000.0, 'outer'][::-1]},
                  2, '2-ply','Bilayer'),
                 ({1: [600.0, 'outer'][::-1],
                   2: [800.0, 'middle'][::-1],
                   3: [600.0, 'outer'][::-1]},
                  3, '3-ply', 'Trilayer'),
                 ({1: [500.0, 'outer'][::-1],
                   2: [500.0, 'inner'][::-1],
                   3: [500.0, 'inner'][::-1],
                   4: [500.0, 'outer'][::-1]},
                  4, '4-ply', 'Quadlayer'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [200.0, 'inner'][::-1],
                   3: [800.0, 'middle'][::-1],
                   4: [200.0, 'inner'][::-1],
                   5: [400.0, 'outer'][::-1]},
                  5, '5-ply', 'Standard'),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [800.0, 'middle'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [400.0, 'outer'][::-1]},
                  7, '7-ply', None),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [800.0, 'middle'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [400.0, 'outer'][::-1]},
                  7, '7-ply', None),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [100.0, 'inner'][::-1],
                   5: [800.0, 'middle'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [100.0, 'inner'][::-1],
                   8: [100.0, 'inner'][::-1],
                   9: [400.0, 'outer'][::-1]},
                  9, '9-ply', None),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [100.0, 'inner'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [800.0, 'middle'][::-1],
                   7: [100.0, 'inner'][::-1],
                   8: [100.0, 'inner'][::-1],
                   9: [100.0, 'inner'][::-1],
                   10: [100.0, 'inner'][::-1],
                   11: [400.0, 'outer'][::-1]},
                  11, '11-ply', None),
                 ({1: [400.0, 'outer'][::-1],
                   2: [100.0, 'inner'][::-1],
                   3: [100.0, 'inner'][::-1],
                   4: [100.0, 'inner'][::-1],
                   5: [100.0, 'inner'][::-1],
                   6: [100.0, 'inner'][::-1],
                   7: [800.0, 'middle'][::-1],
                   8: [100.0, 'inner'][::-1],
                   9: [100.0, 'inner'][::-1],
                   10: [100.0, 'inner'][::-1],
                   11: [100.0, 'inner'][::-1],
                   12: [100.0, 'inner'][::-1],
                   13: [400.0, 'outer'][::-1]},
                  13, '13-ply', None)]
    nt.assert_equal(actual, expected) 
    
def test_Stack_identify5():
    '''Check identifying for symmetric geometry.'''
    stacks = [con.Stack(Geo).StackTuple for Geo in Geos_symmetric]
    actual = stacks
    expected = [({1: ['middle',2000.0]}, 
                 1, '1-ply', 'Monolith'),
                 ({1: ['outer', 600.0], 
                   2: ['middle',800.0, ], 
                   3: ['outer',600.0,]},
                  3, '3-ply', 'Trilayer'),
                 ({1: [ 'outer', 400.0,],
                   2: ['inner', 200.0, ],
                   3: ['middle', 800.0,],
                   4: [ 'inner', 200.0,],
                   5: ['outer', 400.0, ]},
                  5, '5-ply', 'Standard'),
                 ({1: ['outer', 400.0,],
                   2: ['inner', 100.0,],
                   3: [ 'inner', 100.0,],
                   4: ['middle', 800.0,],
                   5: ['inner', 100.0,],
                   6: ['inner', 100.0,],
                   7: ['outer', 400.0,]},
                  7, '7-ply', None)]
    nt.assert_equal(actual, expected)     

# Test StackTuples
def test_Stack_identify6():
    '''Check StackTuple attribute access; stack.'''
    stacks = [con.Stack(Geo).StackTuple.order for Geo in Geos_simple]
    actual = stacks                                        # StackTuple attr     
    expected = [{1: ['middle', 2000.0,]},
                {1: ['outer', 1000.0, ], 2: ['outer',1000.0, ]},
                {1: ['outer',600.0, ], 2: ['middle',800.0], 3: ['outer',600.0, ]},
                {1: ['outer', 500.0, ],
                 2: ['inner',500.0,],
                 3: ['inner',500.0, ],
                 4: ['outer',500.0, ]},
                ]
    nt.assert_equal(actual, expected) 
    
def test_Stack_identify7():
    '''Check StackTuple attribute access; nplies.'''
    stacks = [con.Stack(Geo).StackTuple.nplies for Geo in Geos_simple]
    actual = stacks                                        # StackTuple attr     
    expected = [1,2,3,4]
    nt.assert_equal(actual, expected)     

def test_Stack_identify8():
    '''Check StackTuple attribute access; name.'''
    stacks = [con.Stack(Geo).StackTuple.name for Geo in Geos_simple]
    actual = stacks                                        # StackTuple attr     
    expected = ['1-ply', '2-ply', '3-ply', '4-ply']
    nt.assert_equal(actual, expected)     

def test_Stack_identify9():
    '''Check StackTuple attribute access; alias.'''
    stacks = [con.Stack(Geo).StackTuple.alias for Geo in Geos_full]
    actual = stacks                                        # StackTuple attr     
    expected = ['Monolith', 'Bilayer', 'Trilayer', 'Quadlayer', 'Standard',
               'Standard', 'Standard', None, None]
    nt.assert_equal(actual, expected)  
    
    
# Test adding materials to stacks
def test_Stack_materials1():
    '''Check directly, add_materials for static parameters; builds dicts.'''
    actual = []
    ##mat_props_df = la.input_.to_df(mat_props)
    ##mat_props_df = la.distributions.Case.materials_to_df(mat_props)
    model = 'Wilson_LT'
    custom_matls = []    
    for Geo in Geos_full2:
        stack_dict = con.Stack(Geo).StackTuple.order
        
        ##con.Stack.add_materials(stack_dict, mat_props_df) 
        ##con.Stack.add_materials(stack_dict, mat_props)
        con.Stack.add_materials(stack_dict, bdft.get_materials(mat_props))
        actual.append(stack_dict)  
    
    expected = [{1: ['middle', 2000.0, 'HA']},
                 {1: ['outer', 1000.0, 'HA'], 
                   2: ['outer', 1000.0, 'PSu']},
                 {1: ['outer', 600.0, 'HA'],
                   2: ['middle', 800.0, 'PSu'],
                   3: ['outer', 600.0,'HA']},
                 {1: ['outer', 500.0, 'HA'],
                   2: ['inner', 500.0, 'PSu'],
                   3: ['inner', 500.0, 'HA'],
                   4: ['outer', 500.0, 'PSu']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 200.0, 'PSu'],
                   3: ['middle', 800.0,'HA'],
                   4: ['inner', 200.0, 'PSu'],
                   5: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 200.0, 'PSu'],
                   3: ['middle', 800.0,'HA'],
                   4: ['inner', 200.0, 'PSu'],
                   5: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 200.0, 'PSu'],
                   3: ['middle', 800.0,'HA'],
                   4: ['inner', 200.0, 'PSu'],
                   5: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 100.0, 'PSu'],
                   3: ['inner', 100.0, 'HA'],
                   4: ['middle', 800.0,'PSu'],
                   5: ['inner', 100.0, 'HA'],
                   6: ['inner', 100.0, 'PSu'],
                   7: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 100.0, 'PSu'],
                   3: ['inner', 100.0, 'HA'],
                   4: ['middle', 800.0,'PSu'],
                   5: ['inner', 100.0, 'HA'],
                   6: ['inner', 100.0, 'PSu'],
                   7: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 100.0, 'PSu'],
                   3: ['inner', 100.0, 'HA'],
                   4: ['inner', 100.0, 'PSu'],
                   5: ['middle', 800.0,'HA'],
                   6: ['inner', 100.0, 'PSu'],
                   7: ['inner', 100.0, 'HA'],
                   8: ['inner', 100.0, 'PSu'],
                   9: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 100.0, 'PSu'],
                   3: ['inner', 100.0, 'HA'],
                   4: ['inner', 100.0, 'PSu'],
                   5: ['inner', 100.0, 'HA'],
                   6: ['middle', 800.0,'PSu'],
                   7: ['inner', 100.0, 'HA'],
                   8: ['inner', 100.0, 'PSu'],
                   9: ['inner', 100.0, 'HA'],
                   10: ['inner', 100.0, 'PSu'],
                   11: ['outer', 400.0, 'HA']},
                 {1: ['outer', 400.0, 'HA'],
                   2: ['inner', 100.0, 'PSu'],
                   3: ['inner', 100.0, 'HA'],
                   4: ['inner', 100.0, 'PSu'],
                   5: ['inner', 100.0, 'HA'],
                   6: ['inner', 100.0, 'PSu'],
                   7: ['middle', 800.0,'HA'],
                   8: ['inner', 100.0, 'PSu'],
                   9: ['inner', 100.0, 'HA'],
                   10: ['inner', 100.0, 'PSu'],
                   11: ['inner', 100.0, 'HA'],
                   12: ['inner', 100.0, 'PSu'],
                   13: ['outer', 400.0, 'HA']}]
    #print(actual)
    #assert actual == expected
    nt.assert_equal(actual, expected)  

    
def test_Stack_num_middle1():
    '''Check no more than one middle layer is in a stack.'''
    actual = []
    for Geo in Geos_full2:
        stack_tuple = la.constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple
        n_middle = [v for k, v in stack_tuple.order.items() if 'middle' in v]
        ##n_middle = [v for k, v in stack_tuple.stack.items() if 'middle' in v]
        actual.append(len(n_middle))
    expected = [1]*len(Geos_full2)
    assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return expected

def test_Stack_num_outer1():
    '''Check no more than two outer layers are in a stack.'''
    actual = []  
    for Geo in Geos_full2:
        stack_tuple = la.constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple
        n_outer = [v for k, v in stack_tuple.order.items() if 'outer' in v]
        ##n_outer = [v for k, v in stack_tuple.stack.items() if 'outer' in v]
        actual.append(len(n_outer))
    expected = [2]*len(Geos_full2)
    assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return actual    
    
#------------------------------------------------------------------------------
# LAMINATE
#------------------------------------------------------------------------------
'''Tests > 1s are here, likely due to calling constructors.'''

# dft = wlt.Defaults()
# G = la.input_.Geometry
# constr = la.constructs.Laminate

# Tests for Laminate prints
def test_Laminate_print1():
    '''Check Laminate.__repr__ output.'''
    geo_input = '400-[200]-800'
    #G = la.input_.Geometry(geo_input)
    
    #dft = wlt.Defaults()
    ##dft = ut.Defaults()
    FI = dft.FeatureInput
    FI['Geometry'] = G(geo_input)
    #FI['Geometry'] = G

    actual = constr(FI).__repr__()
    #actual = la.constructs.Laminate(FI).__repr__()
    expected = '<lamana LaminateModel object (400.0-[200.0]-800.0), p=5>'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)
    
def test_Laminate_print2():
    '''Check Laminate.__repr__ symmetry output.'''
    geo_input = '400-[200]-400S'
    #G = la.input_.Geometry(geo_input)
    
    #dft = wlt.Defaults()
    ##dft = ut.Defaults()
    FI = dft.FeatureInput
    FI['Geometry'] = G(geo_input)
    #FI['Geometry'] = G

    actual = constr(FI).__repr__()
    #actual = la.constructs.Laminate(FI).__repr__()
    expected = '<lamana LaminateModel object (400.0-[200.0]-400.0S), p=5>'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)    

            
# Using laminator -------------------------------------------------------------
# Tests for Checking that DataFrames Make Sense
'''CAUTION: many cases will be loaded.  This may lower performance.'''
'''Decide to extend laminator for all tests or deprecate.'''

# Global Cases
#dft = wlt.Defaults()
##dft = ut.Defaults()
case = ut.laminator(geos=dft.geos_standard) 
#cases = ut.laminator(geos=dft.geos_all, ps=[2,3,4,5], verbose=True)
cases = ut.laminator(geos=dft.geos_all, ps=[1,2,3,4,5], verbose=True)
#cases = ut.laminator(geos=geos_full3, ps=[1,2,3,4,5], verbose=True)


# The following tests simply iterate over the latter case suite.
def test_Laminate_materials1():
    '''Check materials are in the matl column.'''
    for case_ in case.values():
        for LM in case_.LMs:
            materials = LM. materials
            column = LM.LMFrame['matl'].values
            actual = (set(materials).intersection(column))
            #print(materials)
            #print(column)
            #print(actual)
            nt.assert_true(actual)
            
def test_Laminate_sanity1():
    '''Check the first d_ row is 0.'''
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            print(LM)
            df = LM.LMFrame
            #print(df)
            if (LM.p%2 != 0) & (LM.nplies > 1):
                expected = 0
                actual = df.loc[0, 'd(m)']
                #print(actual)
                #assert actual == expected
                nt.assert_equal(actual, expected)
                
def test_Laminate_sanity2():
    '''Check the last d_ row equals the total thickness.'''
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            if LM.p > 1:  
                df = LM.LMFrame
                t_total = LM.total
                print(df)
                expected = t_total
                '''Find faster way to get last element.'''
                actual = df['d(m)'][-1::].values[0]        # get last item
                print(actual)
                #assert actual == expected 
                nt.assert_equal(actual, expected) 
                
def test_Laminate_sanity3():
    '''Check values are mirrored across the neutral axis for label_, t_, h_.'''
    cols = ['label', 't(um)', 'h(m)']
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            if LM.p > 1:
                df = LM.LMFrame
                #print(df)
                tensile = LM.tensile.reset_index(drop=True)
                compressive = LM.compressive[::-1].reset_index(drop=True)
                #print(tensile[cols])
                #print(compressive[cols])
                print(LM.Geometry)
                #print(LM.name)
                print(LM.p)
                #print(LM.LMFrame)
                #assert tensile[cols] == compressive[cols]
                ut.assertFrameEqual(tensile[cols], compressive[cols])
                
def test_Laminate_sanity4():
    '''Check values are mirrored across the neutral axis for Z_, z_'''
    cols = ['Z(m)', 'z(m)', 'z(m)*']
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            if LM.p > 1:
                df = LM.LMFrame
                #print(df)
                tensile = LM.tensile.reset_index(drop=True)
                compressive = LM.compressive[::-1].reset_index(drop=True)
                #print(tensile[cols])
                #print(-compressive[cols])
                print(LM.Geometry)
                #print(LM.name)
                print(LM.p)
                print(LM.LMFrame)
                #assert tensile[cols] == compressive[cols]
                ut.assertFrameEqual(tensile[cols], -compressive[cols])
                
def test_Laminate_sanity5():
    '''Check intf_, k_ equal Nan for Monoliths with p < 2.'''
    cols = ['intf', 'k']
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            if (LM.name == 'Monolith') & (LM.p < 2):
                df = LM.LMFrame
                df_null = pd.DataFrame(index=df.index, columns=df.columns)
                expected = df_null.fillna(np.nan)
                actual = df
                #print(actual[cols])
                #print(expected[cols])
                print(LM.Geometry)
                #print(LM.name)
                print(LM.p)
                ut.assertFrameEqual(actual[cols], expected[cols])

def test_Laminate_sanity6():
    '''Check middle d_ is half the total thickness.'''
    cols = ['t(um)']
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            if (LM.nplies%2 != 0) & (LM.p%2 != 0) & (LM.p > 3):
                print(LM.Geometry)
                #print(LM.name)
                print(LM.p)
                #print(LM.LMFrame)
                df = LM.LMFrame
                #t_total = df.groupby('layer')['t(um)'].unique().sum()[0] * 1e-6
                #print(t_total)
                #print(LM.total)
                #print(type(LM.total))
                t_mid = df.loc[df['label'] == 'neut. axis', 'd(m)']
                actual = t_mid.iloc[0]
                expected = LM.total/2
                #print(actual)
                #print(expected)
                
                # Regular assert breaks due to float.  Using assert_almost_equals'''
                np.testing.assert_almost_equal(actual, expected) 
                nt.assert_almost_equals(actual, expected) 
        
def test_Laminate_sanity7():
    '''Check z_ = 0 for even plies, p>1.'''
    import numpy as np
    cols = ['z(m)']
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            #print(LM)
            if LM.nplies%2 == 0:
                #print(LM)
                #print(LM.Geometry)
                df = LM.LMFrame
                # Select middle most indices, should be zero
                halfidx = len(df.index)//2 
                #print(halfidx)
                actual = df.loc[halfidx-1: halfidx, cols].values
                expected = np.zeros((2,1))
                #print(actual)
                #print(expected)
                np.testing.assert_array_equal(actual, expected)
                
def test_Laminate_sanity8():
    '''Check DataFrame length equals nplies*p.'''
    for case in cases.values():
        for LM in case.LMs:
#     for LMs in cases.values():
#         for LM in LMs:
            #print(LM)
            df = LM.LMFrame
            actual = df.shape[0]
            length = LM.nplies*LM.p
            expected = length
            #print(actual)
            #print(expected)
            #assert actual == expected
            nt.assert_almost_equals(actual, expected)   

def test_Laminate_sanity9():
    '''Check Monoliths, p=1 have positive values.
    Now using ut.get_frames() for specific case selections.
    '''
    cases_selected = ut.get_frames(cases, name='Monolith', ps=[1])
    for LMs in cases_selected:
        df_numeric = LMs.select_dtypes(include=[np.number])
        df = df_numeric
        #print(df_numeric)
        actual = df_numeric[(df_numeric<0)]                # catches negative numbers if any
        expected = pd.DataFrame(index=df.index, columns=df.columns).fillna(np.nan)
        print(actual)
        print(expected)
        ut.assertFrameEqual(actual, expected)
        
# Test attributes
def test_Laminate_attr_max():
    '''Check the max attribute and maximum stresses.'''
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.max_stress
            d = {0:   0.378731,
                 5:   0.012915,
                 10:  0.151492,
                 14: -0.151492,
                 19: -0.012915,
                 24: -0.378731,
            }
            s = pd.Series(d)
            s.name = 'stress_f (MPa/N)'
            expected = s    
            #assert actual.all() == expected.all()
            ut.assertSeriesEqual(actual, expected, check_less_precise=True)    

def test_Laminate_attr_min():
    '''Check the min attribute and minimum stresses.'''
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.min_stress
            d = {4:   0.227238,
                 9:   0.008610,
                 15: -0.008610,
                 20: -0.227238,
                }
            s = pd.Series(d)
            s.name = 'stress_f (MPa/N)'
            expected = s
            #assert actual.all() == expected.all() 
            ut.assertSeriesEqual(actual, expected, check_less_precise=True)

def test_Laminate_attr_extrema():
    case1 = ut.laminator(dft.geos_full, ps=[5])
    case2 = ut.laminator(dft.geos_full, ps=[2])

    for case_full, case_trimmed in zip(case1.values(), case2.values()):
        for LM_full, LM_trimmed in zip(case_full.LMs, case_trimmed.LMs):
            actual = LM_full.extrema
            actual.reset_index(drop=True, inplace=True)
            expected = LM_trimmed.LMFrame
            #print(actual)
            #print(expected)
            ut.assertFrameEqual(actual, expected)    
        
def test_Laminate_attr_isspecial():
    '''Check the is_special attribute works for different ps.'''
    expected = [True, True, True, True, True, True, True, 
                False, False, False, False, False, False, 
                False, False, False, False, False]   
    
    # Uses Defaults().geo_all; will grow if more defaults are added
    for case in cases.values():
        # Make a list for each case by p, then assert 
        actual = [LM.is_special for LM in case.LMs]
        #print(actual)
        #assert actual == expected
        nt.assert_equal(actual, expected) 
        
# Test Comparisons
def test_Laminate_eq1():
    '''Compare 5-ply to self should be True; testing == of LaminateModels'''
    case1 = ut.laminator('400-[200]-800')
    case2 = ut.laminator('400-200-800')
    standard = [LM for case_ in case1.values() for LM in case_.LMs]
    unconventional = [LM for case_ in case2.values() for LM in case_.LMs]
    # Internal converts unconventional string to be equivalent to standard.
    actual = (standard[0] == unconventional[0])
    nt.assert_true(actual)

def test_Laminate_ne1():
    '''Compare 5-ply to even plies should be False; testing != of LaminateModels'''
    case1 = ut.laminator(dft.geos_standard)
    cases1 = ut.laminator(dft.geos_even)
    standard = [LM for case_ in case1.values() for LM in case_.LMs]
    for case in cases1.values():
        for even_LM in case.LMs:
            actual = (even_LM != standard[0])
            print(even_LM)
            print(standard[0])
            print(actual)
            nt.assert_true(actual)

def test_Laminate_compare_sets1():
    '''Check __eq__, __ne__ and sets containing Laminate object instances.'''
    # Tests __hash__
    cases1 = ut.laminator(dft.geo_inputs['5-ply'])
    cases2 = ut.laminator(dft.geo_inputs['1-ply'])
    LM1 = cases1[0].LMs[0]                                     # 400-200-800
    LM2 = cases1[0].LMs[1]                                     # 400-[200]-800            
    LM3 = cases1[0].LMs[2]                                     # 400-[200]-400S
    LM4 = cases2[0].LMs[0]                                     # 0-0-2000 
    
    #assert set([LM1]) == set([LM1])
    #assert set([LM1]) == set([LM2])
    #assert set([LM1]) != set([LM3])
    #assert set([LM1]) != set([LM4])
    
    nt.assert_set_equal(set([LM1, LM2]), set([LM1, LM2]))
    nt.assert_set_equal(set([LM1]), set([LM2]))
    nt.assert_set_equal(set([LM2]), set([LM1]))
    nt.assert_true(set([LM1]) != set([LM3]))
    nt.assert_true(set([LM1]) != set([LM4]))
    nt.assert_equal(len(set([LM1,LM2,LM3,LM4])), 3)            
            
            
'''Make a test where the FeautreInpts are different but df are equal --> fail test.'''
#  assert even_LM.FeatureInput != standard[0].FeatureInput   


'''Unsure how to make the following faster since the constructs are built real-time.'''
'''But these three take up 10 seconds.'''
def test_Laminate_num_middle1():
    '''Check no more than one middle layer Lamina is in a Laminate.'''
    actual = []  
    for Geo in Geos_full2:
        layers = con.Laminate(bdft.get_FeatureInput(Geo, 
                                                    load_params=load_params,
                                                    mat_props = mat_props,
                                                    model='Wilson_LT',)
                                                   )._check_layer_order()
        actual.append(layers.count('M'))
        expected = [1]*len(layers)
    #assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return actual

def test_Laminate_num_outer1():
    '''Check no more than two outer layer Lamina are in a Laminate.'''
    actual = []  
    for Geo in Geos_full2:
        layers = con.Laminate(bdft.get_FeatureInput(Geo, 
                                                    load_params=load_params,
                                                    mat_props = mat_props,
                                                    model='Wilson_LT',)
                                                   )._check_layer_order()
        actual.append(layers.count('O'))
        expected = [1]*len(layers)
    #assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return actual

# Test order
def test_Laminate_laminae_order1():
    '''Use built-in function to check stacking order.'''
    actual = []  
    for Geo in Geos_full:
        # Returns the stacking order each; plus has an internal assert if mismatch found
        actual.append(con.Laminate(
                bdft.get_FeatureInput(Geo, 
                                      load_params=load_params,
                                      mat_props=mat_props,
                                      model='Wilson_LT'))._check_layer_order())
    expected  = [['M'],
                 ['O','O'],
                 ['O','M', 'O'],
                 ['O','I','I','O'],
                 ['O','I','M','I','O'],
                 ['O','I','M','I','O'],
                 ['O','I','M','I','O'],
                 ['O','I','I','M','I','I','O'],
                 ['O','I','I','M','I','I','O'],
                ]
    nt.assert_equal(actual, expected)  
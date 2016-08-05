#------------------------------------------------------------------------------
'''Confirm output of general Laminate structure.'''
# NOTE: Refactoring in 0.4.3c5b led to patching container orders.
import os
import inspect
import logging

import nose.tools as nt
import pandas as pd
import numpy as np

from lamana import input_
from lamana import distributions
from lamana import constructs
from lamana.lt_exceptions import IndeterminateError
from lamana.lt_exceptions import ModelError
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt


bdft = input_.BaseDefaults()
dft = wlt.Defaults()
G = input_.Geometry
constr = constructs.Laminate


# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {
    'R': 12e-3,                                            # specimen radius
    'a': 7.5e-3,                                           # support ring radius
    'p': 4,                                                # points/layer
    'P_a': 1,                                              # applied load
    'r': 2e-4,                                             # radial distance from center loading
}

# # Quick Form
# mat_props = {
#    'HA' : [5.2e10, 0.25],
#    'PSu' : [2.7e9, 0.33],
#}

# # Conversion to Standard Form
# mat_props = bdft._convert_material_parameters(mat_props)

mat_props = {
    'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
    'Poissons': {'HA': 0.25, 'PSu': 0.33}
}

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

# G = input_.Geometry

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
    ##unfolded = [constructs.Stack(Geo).unfolded for Geo in Geos_simple]
    unfolded = [constructs.Stack(bdft.get_FeatureInput(Geo)).unfolded for Geo in Geos_simple]
    actual = unfolded
    expected = [
        # Monolith
        [(0.0, 'outer')[::-1],
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
         (500.0, 'outer')[::-1]],
    ]
    nt.assert_equal(actual, expected)


def test_Stack_decode_2():
    '''Check decoding and unfolding geometries with [inner_i].'''
    ##unfolded = [constructs.Stack(Geo).unfolded for Geo in Geos_inner]
    unfolded = [constructs.Stack(bdft.get_FeatureInput(Geo)).unfolded for Geo in Geos_inner]
    actual = unfolded
    expected = [
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
    ]
    nt.assert_equal(actual, expected)


def test_Stack_decode_3():
    '''Check decoding and unfolding of more geometries.'''
    ##unfolded = [constructs.Stack(Geo).unfolded for Geo in Geos_full]
    unfolded = [constructs.Stack(bdft.get_FeatureInput(Geo)).unfolded for Geo in Geos_full]
    actual = unfolded
    expected = [
        [(0.0, 'outer')[::-1],
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
    ]
    nt.assert_equal(actual, expected)


def test_Stack_decode_4():
    '''Checks decoding and unfolding even more geometries.'''
    ##unfolded = [constructs.Stack(Geo).unfolded for Geo in Geos_full2]
    unfolded = [constructs.Stack(bdft.get_FeatureInput(Geo)).unfolded for Geo in Geos_full2]
    actual = unfolded
    expected = [
        [(0.0, 'outer')[::-1],
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
         (400.0, 'outer')[::-1]]
    ]
    nt.assert_equal(actual, expected)


def test_Stack_decode_5():
    '''Check decoding and unfolding of symmetric geometries.'''
    ##unfolded = [constructs.Stack(Geo).unfolded for Geo in Geos_symmetric]
    unfolded = [constructs.Stack(bdft.get_FeatureInput(Geo)).unfolded for Geo in Geos_symmetric]
    actual = unfolded
    expected = [
        [(0.0, 'outer')[::-1],
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
         (400.0, 'outer')[::-1]]
    ]
    nt.assert_equal(actual, expected)


# Build dicts of stacks
#stack = {layer_ : [thickness, type_ ], ...}
def test_Stack_identify1():
    '''Check building dicts for simple geometry.'''
    ##stacks = [constructs.Stack(Geo).StackTuple for Geo in Geos_simple]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple for Geo in Geos_simple]
    actual = stacks
    expected = [
        ({1: [2000.0, 'middle'][::-1]},
         1, '1-ply', 'Monolith'),
        ({1: [1000.0, 'outer'][::-1],
          2: [1000.0, 'outer'][::-1]},
         2, '2-ply', 'Bilayer'),
        ({1: [600.0, 'outer'][::-1],
          2: [800.0, 'middle'][::-1],
          3: [600.0, 'outer'][::-1]},
         3, '3-ply', 'Trilayer'),
        ({1: [500.0, 'outer'][::-1],
          2: [500.0, 'inner'][::-1],
          3: [500.0, 'inner'][::-1],
          4: [500.0, 'outer'][::-1]},
         4, '4-ply', 'Quadlayer'),
    ]
    nt.assert_equal(actual, expected)


def test_Stack_identify2():
    '''Check building dicts for inner_i geometry.'''
    ##stacks = [constructs.Stack(Geo).StackTuple for Geo in Geos_inner]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple for Geo in Geos_inner]
    actual = stacks
    expected = [
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
    ]
    nt.assert_equal(actual, expected)


def test_Stack_identify3():
    '''Check building dicts for full  geometry.'''
    ##stacks = [constructs.Stack(Geo).StackTuple for Geo in Geos_full]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple for Geo in Geos_full]
    actual = stacks
    expected = [
        ({1: [2000.0, 'middle'][::-1]},
         1, '1-ply', 'Monolith'),
        ({1: [1000.0, 'outer'][::-1],
          2: [1000.0, 'outer'][::-1]},
         2, '2-ply', 'Bilayer'),
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
         7, '7-ply', None)
    ]
    nt.assert_equal(actual, expected)


def test_Stack_identify4():
    '''Check building dicts for full2 geometry.'''
    ##stacks = [constructs.Stack(Geo).StackTuple for Geo in Geos_full2]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple for Geo in Geos_full2]
    actual = stacks
    expected = [
        ({1: [2000.0, 'middle'][::-1]},
         1, '1-ply', 'Monolith'),
        ({1: [1000.0, 'outer'][::-1],
          2: [1000.0, 'outer'][::-1]},
         2, '2-ply', 'Bilayer'),
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
         13, '13-ply', None)
    ]
    nt.assert_equal(actual, expected)


def test_Stack_identify5():
    '''Check identifying for symmetric geometry.'''
    ##stacks = [constructs.Stack(Geo).StackTuple for Geo in Geos_symmetric]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple for Geo in Geos_symmetric]
    actual = stacks
    expected = [
        ({1: ['middle', 2000.0]},
         1, '1-ply', 'Monolith'),
        ({1: ['outer', 600.0],
          2: ['middle', 800.0],
          3: ['outer', 600.0]},
         3, '3-ply', 'Trilayer'),
        ({1: ['outer', 400.0],
          2: ['inner', 200.0],
          3: ['middle', 800.0],
          4: ['inner', 200.0],
          5: ['outer', 400.0]},
         5, '5-ply', 'Standard'),
        ({1: ['outer', 400.0],
          2: ['inner', 100.0],
          3: ['inner', 100.0],
          4: ['middle', 800.0],
          5: ['inner', 100.0],
          6: ['inner', 100.0],
          7: ['outer', 400.0]},
         7, '7-ply', None)
    ]
    nt.assert_equal(actual, expected)


# Test StackTuples
def test_Stack_identify6():
    '''Check StackTuple attribute access; stack.'''
    ##stacks = [constructs.Stack(Geo).StackTuple.order for Geo in Geos_simple]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple.order for Geo in Geos_simple]
    actual = stacks                                        # StackTuple attr
    expected = [
        {1: ['middle', 2000.0]},
        {1: ['outer', 1000.0],
         2: ['outer', 1000.0]},
        {1: ['outer', 600.0],
         2: ['middle', 800.0],
         3: ['outer', 600.0]},
        {1: ['outer', 500.0],
         2: ['inner', 500.0],
         3: ['inner', 500.0],
         4: ['outer', 500.0]},
    ]
    nt.assert_equal(actual, expected)


def test_Stack_identify7():
    '''Check StackTuple attribute access; nplies.'''
    ##stacks = [constructs.Stack(Geo).StackTuple.nplies for Geo in Geos_simple]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple.nplies for Geo in Geos_simple]
    actual = stacks                                        # StackTuple attr
    expected = [1, 2, 3, 4]
    nt.assert_equal(actual, expected)


def test_Stack_identify8():
    '''Check StackTuple attribute access; name.'''
    ##stacks = [constructs.Stack(Geo).StackTuple.name for Geo in Geos_simple]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple.name for Geo in Geos_simple]
    actual = stacks                                        # StackTuple attr
    expected = ['1-ply', '2-ply', '3-ply', '4-ply']
    nt.assert_equal(actual, expected)


def test_Stack_identify9():
    '''Check StackTuple attribute access; alias.'''
    ##stacks = [constructs.Stack(Geo).StackTuple.alias for Geo in Geos_full]
    stacks = [constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple.alias for Geo in Geos_full]
    actual = stacks                                        # StackTuple attr
    expected = [
        'Monolith', 'Bilayer', 'Trilayer', 'Quadlayer', 'Standard',
        'Standard', 'Standard', None, None
    ]
    nt.assert_equal(actual, expected)


# Test adding materials to stacks
def test_Stack_materials1():
    '''Check directly, add_materials for static parameters; builds dicts.'''
    actual = []
    ##mat_props_df = input_.to_df(mat_props)
    ##mat_props_df = distributions.Case.materials_to_df(mat_props)
    ##model = 'Wilson_LT'                                    # unused
    ##custom_matls = []                                      # unused
    for Geo in Geos_full2:
        ##stack_dict = constructs.Stack(Geo).StackTuple.order
        stack_dict = constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple.order

        ##constructs.Stack.add_materials(stack_dict, mat_props_df)
        ##constructs.Stack.add_materials(stack_dict, mat_props)
        constructs.Stack.add_materials(stack_dict, bdft.get_materials(mat_props))
        actual.append(stack_dict)

    expected = [
        {1: ['middle', 2000.0, 'HA']},
        {1: ['outer', 1000.0, 'HA'],
         2: ['outer', 1000.0, 'PSu']},
        {1: ['outer', 600.0, 'HA'],
         2: ['middle', 800.0, 'PSu'],
         3: ['outer', 600.0, 'HA']},
        {1: ['outer', 500.0, 'HA'],
         2: ['inner', 500.0, 'PSu'],
         3: ['inner', 500.0, 'HA'],
         4: ['outer', 500.0, 'PSu']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 200.0, 'PSu'],
         3: ['middle', 800.0, 'HA'],
         4: ['inner', 200.0, 'PSu'],
         5: ['outer', 400.0, 'HA']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 200.0, 'PSu'],
         3: ['middle', 800.0, 'HA'],
         4: ['inner', 200.0, 'PSu'],
         5: ['outer', 400.0, 'HA']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 200.0, 'PSu'],
         3: ['middle', 800.0, 'HA'],
         4: ['inner', 200.0, 'PSu'],
         5: ['outer', 400.0, 'HA']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 100.0, 'PSu'],
         3: ['inner', 100.0, 'HA'],
         4: ['middle', 800.0, 'PSu'],
         5: ['inner', 100.0, 'HA'],
         6: ['inner', 100.0, 'PSu'],
         7: ['outer', 400.0, 'HA']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 100.0, 'PSu'],
         3: ['inner', 100.0, 'HA'],
         4: ['middle', 800.0, 'PSu'],
         5: ['inner', 100.0, 'HA'],
         6: ['inner', 100.0, 'PSu'],
         7: ['outer', 400.0, 'HA']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 100.0, 'PSu'],
         3: ['inner', 100.0, 'HA'],
         4: ['inner', 100.0, 'PSu'],
         5: ['middle', 800.0, 'HA'],
         6: ['inner', 100.0, 'PSu'],
         7: ['inner', 100.0, 'HA'],
         8: ['inner', 100.0, 'PSu'],
         9: ['outer', 400.0, 'HA']},
        {1: ['outer', 400.0, 'HA'],
         2: ['inner', 100.0, 'PSu'],
         3: ['inner', 100.0, 'HA'],
         4: ['inner', 100.0, 'PSu'],
         5: ['inner', 100.0, 'HA'],
         6: ['middle', 800.0, 'PSu'],
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
         7: ['middle', 800.0, 'HA'],
         8: ['inner', 100.0, 'PSu'],
         9: ['inner', 100.0, 'HA'],
         10: ['inner', 100.0, 'PSu'],
         11: ['inner', 100.0, 'HA'],
         12: ['inner', 100.0, 'PSu'],
         13: ['outer', 400.0, 'HA']}
    ]
    #print(actual)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Stack_num_middle1():
    '''Check no more than one middle layer is in a stack.'''
    actual = []
    for Geo in Geos_full2:
        stack_tuple = constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple
        n_middle = [v for k, v in stack_tuple.order.items() if 'middle' in v]
        ##n_middle = [v for k, v in stack_tuple.stack.items() if 'middle' in v]
        actual.append(len(n_middle))
    expected = [1] * len(Geos_full2)
    assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return expected


def test_Stack_num_outer1():
    '''Check no more than two outer layers are in a stack.'''
    actual = []
    for Geo in Geos_full2:
        stack_tuple = constructs.Stack(bdft.get_FeatureInput(Geo)).StackTuple
        n_outer = [v for k, v in stack_tuple.order.items() if 'outer' in v]
        ##n_outer = [v for k, v in stack_tuple.stack.items() if 'outer' in v]
        actual.append(len(n_outer))
    expected = [2] * len(Geos_full2)
    assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return actual

#------------------------------------------------------------------------------
# LAMINATE
#------------------------------------------------------------------------------
# dft = wlt.Defaults()
# G = input_.Geometry
# constr = constructs.Laminate


# Tests for Laminate prints
def test_Laminate_print1():
    '''Check Laminate.__repr__ output.'''
    geo_input = '400-[200]-800'
    #G = input_.Geometry(geo_input)

    #dft = wlt.Defaults())
    # TODO: replace with get_FeatureInput
    FI = dft.FeatureInput
    FI['Geometry'] = G(geo_input)
    #FI['Geometry'] = G

    # TODO: Replace constr with actual name
    actual = constructs.Laminate(FI).__repr__()
    #actual = constructs.Laminate(FI).__repr__()
    expected = '<lamana Laminate object (400.0-[200.0]-800.0), p=5>'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Laminate_print2():
    '''Check Laminate.__repr__ symmetry output.'''
    geo_input = '400-[200]-400S'
    #G = input_.Geometry(geo_input)

    #dft = wlt.Defaults()
    FI = dft.FeatureInput
    FI['Geometry'] = G(geo_input)
    #FI['Geometry'] = G

    actual = constructs.Laminate(FI).__repr__()
    #actual = constructs.Laminate(FI).__repr__()
    expected = '<lamana Laminate object (400.0-[200.0]-400.0S), p=5>'
    #print(actual, expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)

###
# TODO: Rename following functions and generalize LM or match object (L or LM)
# Tests for Checking that DataFrames Make Sense -------------------------------
'''CAUTION: many cases will be loaded.  This may lower performance.'''
'''Decide to extend laminator for all tests or deprecate.'''

# Global Cases
#dft = wlt.Defaults()
case = distributions.laminator(geos=dft.geos_standard)
#cases = distributions.laminator(geos=dft.geos_all, ps=[2,3,4,5], verbose=True)
cases = distributions.laminator(geos=dft.geos_all, ps=[1, 2, 3, 4, 5], verbose=True)
#cases = distributions.laminator(geos=geos_full3, ps=[1,2,3,4,5], verbose=True)


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
            print(LM)
            df = LM.frame
            #print(df)
            if (LM.p % 2 != 0) & (LM.nplies > 1):
                expected = 0
                actual = df.loc[0, 'd(m)']
                #print(actual)
                nt.assert_equal(actual, expected)


def test_Laminate_sanity2():
    '''Check the last d_ row equals the total thickness.'''
    for case in cases.values():
        for LM in case.LMs:
            if LM.p > 1:
                df = LM.frame
                t_total = LM.total
                print(df)
                expected = t_total
                '''Find faster way to get last element.'''
                actual = df['d(m)'][-1::].values[0]        # get last item
                #print(actual)
                nt.assert_equal(actual, expected)


def test_Laminate_sanity3():
    '''Check values are mirrored across the neutral axis for label_, t_, h_.'''
    cols = ['label', 't(um)', 'h(m)']
    for case in cases.values():
        for LM in case.LMs:
            if LM.p > 1:
                tensile = LM.tensile.reset_index(drop=True)
                compressive = LM.compressive[::-1].reset_index(drop=True)
                #print(tensile[cols])
                #print(compressive[cols])
                print(LM.Geometry)
                #print(LM.name)
                print(LM.p)
                #print(LM.LMFrame)
                ut.assertFrameEqual(tensile[cols], compressive[cols])


def test_Laminate_sanity4():
    '''Check values are mirrored across the neutral axis for Z_, z_'''
    cols = ['Z(m)', 'z(m)', 'z(m)*']
    for case in cases.values():
        for LM in case.LMs:
            if LM.p > 1:
                tensile = LM.tensile.reset_index(drop=True)
                compressive = LM.compressive[::-1].reset_index(drop=True)
                #print(tensile[cols])
                #print(-compressive[cols])
                #print(LM.Geometry)
                #print(LM.name)
                #print(LM.p)
                #print(LM.frame)
                ut.assertFrameEqual(tensile[cols], -compressive[cols])


def test_Laminate_sanity5():
    '''Check intf_, k_ equal Nan for Monoliths with p < 2.'''
    cols = ['intf', 'k']
    for case in cases.values():
        for LM in case.LMs:
            if (LM.name == 'Monolith') & (LM.p < 2):
                df = LM.frame
                df_null = pd.DataFrame(index=df.index, columns=df.columns)
                expected = df_null.fillna(np.nan)
                actual = df
                #print(actual[cols])
                #print(expected[cols])
                #print(LM.Geometry)
                #print(LM.name)
                #print(LM.p)
                ut.assertFrameEqual(actual[cols], expected[cols])


def test_Laminate_sanity6():
    '''Check middle d_ is half the total thickness.'''
    for case in cases.values():
        for LM in case.LMs:
            if (LM.nplies % 2 != 0) & (LM.p % 2 != 0) & (LM.p > 3):
                print(LM.Geometry)
                #print(LM.name)
                print(LM.p)
                #print(LM.LMFrame)
                df = LM.frame
                #t_total = df.groupby('layer')['t(um)'].unique().sum()[0] * 1e-6
                #print(t_total)
                #print(LM.total)
                #print(type(LM.total))
                t_mid = df.loc[df['label'] == 'neut. axis', 'd(m)']
                actual = t_mid.iloc[0]
                expected = LM.total / 2
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
            if LM.nplies % 2 == 0:
                #print(LM)
                #print(LM.Geometry)
                df = LM.frame
                # Select middle most indices, should be zero
                halfidx = len(df.index)//2
                #print(halfidx)
                actual = df.loc[halfidx - 1: halfidx, cols].values
                expected = np.zeros((2, 1))
                #print(actual)
                #print(expected)
                np.testing.assert_array_equal(actual, expected)


def test_Laminate_sanity8():
    '''Check DataFrame length equals nplies*p.'''
    for case in cases.values():
        for LM in case.LMs:
            df = LM.frame
            actual = df.shape[0]
            length = LM.nplies * LM.p
            expected = length
            #print(actual)
            #print(expected)
            nt.assert_almost_equals(actual, expected)


def test_Laminate_sanity9_refactored():
    '''Check Monoliths with p=1 only have positive values.

    Notes
    -----
    1. Uses Cases() to extract a subset of selected cases, i.e. Monoliths, p=1.
       (Triggers exceptions that rollback Laminate; actually yields an LFrame).
    2. Cases iterates over values, i.e. separate cases.
    3. Each case is a Monolith of p=1.
    4. actual is a DataFrame of negative numeric values.  NaN if None found
    5. expected is a DataFrame with no negative values, i.e. only NaN.

    '''
    cases_monoliths = distributions.Cases(dft.geo_inputs['1-ply'], ps=[1])
    for case in cases_monoliths:
        for psuedoLM in case.LMs:
            df = psuedoLM.frame
            df_numeric = df.select_dtypes(include=[np.number]) # print number columns
            # test = df_numeric[(df_numeric > 0)]                # catches positive numbers if any
            actual = df_numeric[(df_numeric < 0)]              # catches negative numbers if any
            expected = pd.DataFrame(index=df_numeric.index,
                                    columns=df_numeric.columns).fillna(np.nan)
            #print(df)
            #print(df_numeric)
            #print(actual)
            #print(expected)
            ut.assertFrameEqual(actual, expected)
###

# NOTE: No Longer seems to raise at _make_interval; may not have ever; deprecate
# Test Exception Handling
# @nt.raises(ZeroDivisionError)
# def test_Laminate_internals1():
#     '''Check internal function raises ZeroDivisionError if p = 1 is given to _make_internals.'''
#     # Function needs a DataFrame to work on
#     # Try to feed random DataFrame (LMFrame), random column with p=1
#     # Will rollback to Laminate if p=1
#     case1 = distributions.laminator(dft.geo_inputs['1-ply'], ps=[1])
#     for case_ in case1.values():
#         for LM in case_.LMs:
#             df_random = LM.frame
#             constructs.Laminate._make_internals(df_random, 1, column='k')


# Test properties
# TODO: Fix static expected
# TODO: make cases once, and filter from premade cases to save time
# TODO: Add or move total and p properties to this section from elsewhere
# Test properties
def test_Laminate_prop_frame():
    '''Check returns DataFrame.'''
    geo_input = '400-[200]-400S'
    #FI = bdft.get_FeatureInput(G(geo_input))
    FI = dft.FeatureInput
    FI['Geometry'] = G(geo_input)

    L = constructs.Laminate(FI)
    actual = isinstance(L.frame, pd.DataFrame)
    nt.assert_true(actual)


# TODO: Fix static expected
def test_Laminate_prop_hasdiscont1():
    '''Check the has_discont attribute works for different ps; even ply.'''
    # Disconts exist for p > 2 at interfaces for even and odd plies
    expected_by_p = [False, True, True, True, True]        # False for p < 2
    # Make a case of standards for each p
    cases = distributions.laminator(geos=dft.geos_even, ps=[1, 2, 3, 4, 5])
    # Uses Defaults().geos_standard
    # NOTE: will grow if more defaults are added; need to amend expected
    for case, e in zip(cases.values(), expected_by_p):
        # Make a list of pd.Series for each case by p
        # All cases should be the same per case; return True only if discont found
        # Return True if any disconts are found per cases
        actual = all([LM.has_discont.any() for LM in case.LMs])
        expected = e                                       # expected for all geos per case
        #print(actual)
        nt.assert_equal(actual, expected)


def test_Laminate_prop_hasdiscont2():
    '''Check the has_discont attribute works for different ps; odd ply.'''
    # Disconts exist for p > 2 at interfaces for even and odd plies
    expected_by_p = [True, True, True, True]               # False for p < 2

    # Make a case of standards for each p
    # p = 1 throws IndeterminateError
    # Monoliths do not have disconts
    # TODO: use Cases to test all odds but exclude monoliths
    cases = distributions.laminator(geos=dft.geos_standard, ps=[2, 3, 4, 5])
    # Uses Defaults().geos_standard
    # NOTE: will grow if more defaults are added; need to amend expected
    for case, e in zip(cases.values(), expected_by_p):
        # Make a list of pd.Series for each case by p
        # All cases should be the same per case; return True only if discont found
        # Return True if any disconts are found per cases
        actual = all([LM.has_discont.any() for LM in case.LMs if LM.alias != 'Monolith'])
        expected = e
        #print(actual)
        nt.assert_equal(actual, expected)


def test_Laminate_prop_hasneutaxis1():
    '''Check attribute returns true if neutral axis found; only in odd-plies with odd ps'''
    expected_by_p = [False, True, False, True]
    cases = distributions.laminator(geos=dft.geos_odd, ps=[2, 3, 4, 5])
    for case, e in zip(cases.values(), expected_by_p):
        # any() obviates the ambiguity error from Pandas
        actual = all([LM.has_neutaxis.any() for LM in case.LMs])
        expected = e
        #print(actual)
        nt.assert_equal(actual, expected)


def test_Laminate_prop_hasneutaxis2():
    '''Check attribute returns False if neutral axis not found; only in even-plies.'''
    expected_by_p = [False, False, False, False]
    cases = distributions.laminator(geos=dft.geos_even, ps=[2, 3, 4, 5])
    for case, e in zip(cases.values(), expected_by_p):
        # any() obviates the ambiguity error from Pandas
        actual = all([LM.has_neutaxis.any() for LM in case.LMs])
        expected = e
        #print(actual)
        nt.assert_equal(actual, expected)


def test_Laminate_prop_isspecial():
    '''Check the is_special attribute works for different ps.'''
    expected = [
        True, True, True, True, True, True, True,
        False, False, False, False, False, False,
        False, False, False, False, False
    ]
    # Uses Defaults().geos_all
    # Caution: will grow if more defaults are added; need to amend expected
    for case in cases.values():
        # Make a list for each case by p, then assert
        actual = [LM.is_special for LM in case.LMs]
        #print(actual)
        #assert actual == expected
        nt.assert_equal(actual, expected)


# Test Error Handling
# TODO: Doesn't seem to catch the Exception; needs work
#@nt.raises(IndeterminateError)
#def test_Laminate_indeterminate1():
#    '''Check IndeterminateError is thrown when p=1 odd-ply is made.'''
#    distributions.laminator(geos=dft.geos_odd, ps=[1])


# Test Comparisons
def test_Laminate_eq1():
    '''Compare 5-ply to self should be True; testing == of LaminateModels.'''
    case1 = distributions.laminator('400-[200]-800')
    case2 = distributions.laminator('400-200-800')
    standard = [LM for case_ in case1.values() for LM in case_.LMs]
    unconventional = [LM for case_ in case2.values() for LM in case_.LMs]
    # Internal converts unconventional string to be equivalent to standard.
    actual = (standard[0] == unconventional[0])
    nt.assert_true(actual)


def test_Laminate_eq2():
    '''Check returns NotImplemented if classes are not equal in __eq__.'''
    L = constructs.Laminate(dft.FeatureInput)
    actual = L.__eq__(1)                                   # isinstance(1, Cases()) is False
    expected = NotImplemented
    nt.assert_equal(actual, expected)


# TODO: just use one geo_standard
def test_Laminate_ne1():
    '''Compare 5-ply to even plies should be False; testing != of LaminateModels.'''
    case1 = distributions.laminator(dft.geos_standard)
    cases1 = distributions.laminator(dft.geos_even)
    standard = [LM for case_ in case1.values() for LM in case_.LMs]
    for case in cases1.values():
        for even_LM in case.LMs:
            actual = (even_LM != standard[0])
            print(even_LM)
            print(standard[0])
            print(actual)
            nt.assert_true(actual)


def test_Laminate_ne2():
    '''Check returns NotImplemented if classes are not equal in __ne__.'''
    L = constructs.Laminate(dft.FeatureInput)
    actual = L.__ne__(1)                                   # isinstance(1, Cases()) is False
    expected = NotImplemented
    nt.assert_equal(actual, expected)


def test_Laminate_compare_sets1():
    '''Check __eq__, __ne__ and sets containing Laminate object instances.'''
    # Tests __hash__
    cases1 = distributions.laminator(dft.geo_inputs['5-ply'])
    cases2 = distributions.laminator(dft.geo_inputs['1-ply'])
    LM1 = cases1[0].LMs[0]                                 # 400-200-800
    LM2 = cases1[0].LMs[1]                                 # 400-[200]-800
    LM3 = cases1[0].LMs[2]                                 # 400-[200]-400S
    LM4 = cases2[0].LMs[0]                                 # 0-0-2000

    nt.assert_set_equal(set([LM1, LM2]), set([LM1, LM2]))
    nt.assert_set_equal(set([LM1]), set([LM2]))
    nt.assert_set_equal(set([LM2]), set([LM1]))
    nt.assert_true(set([LM1]) != set([LM3]))
    nt.assert_true(set([LM1]) != set([LM4]))
    nt.assert_equal(len(set([LM1, LM2, LM3, LM4])), 3)


class TestLaminateExportMethods():
    '''Comprise tests for export methods of Laminate; use simple laminate and tempfiles.'''
    case = distributions.laminator('400.0-[200.0]-800.0')[0]
    LM = case.LMs[0]

    def test_Laminate_mtd_to_csv1(self):
        '''Verify uses export function; writes temporary file; cleanup after.'''
        try:
            data_fpath, dash_fpath = self.LM.to_csv(temp=True)
            actual1 = os.path.exists(data_fpath)
            actual2 = os.path.exists(dash_fpath)
            nt.assert_true(actual1)
            nt.assert_true(actual2)
        finally:
            # Cleanup
            os.remove(data_fpath)
            os.remove(dash_fpath)
            logging.info('File has been deleted: {}'.format(data_fpath))
            logging.info('File has been deleted: {}'.format(dash_fpath))

    def test_Laminate_mtd_to_csv2(self):
        '''Verify returns tuple of 2 paths; writes temporary file then deletes.'''
        result = self.LM.to_csv(temp=True, delete=True)
        actual1 = isinstance(result, tuple)
        actual2 = len(result)
        actual3 = isinstance(result[1], str)
        expected = 2
        nt.assert_true(actual1)
        nt.assert_equals(actual2, expected)
        nt.assert_true(actual3)
        logging.info('File has been deleted: {}'.format(result[0]))
        logging.info('File has been deleted: {}'.format(result[1]))

    def test_Laminate_mtd_to_xlsx1(self):
        '''Verify uses export function; writes temporary file; cleanup after.'''
        try:
            (workbook_fpath,) = self.LM.to_xlsx(temp=True)
            actual = os.path.exists(workbook_fpath)
            nt.assert_true(actual)
        finally:
            # Cleanup
            os.remove(workbook_fpath)
            logging.info('File has been deleted: {}'.format(workbook_fpath))

    def test_Laminate_mtd_to_xlsx2(self):
        '''Verify returns tuple of 1 path; writes temporary file then deletes.'''
        # Maintains tuple for consistency
        result = self.LM.to_xlsx(temp=True, delete=True)
        actual1 = isinstance(result, tuple)
        actual2 = len(result)
        actual3 = isinstance(result[0], str)
        expected = 1
        nt.assert_true(actual1)
        nt.assert_equals(actual2, expected)
        nt.assert_true(actual3)
        logging.info('File has been deleted: {}'.format(result))


'''Make a test where the FeautreInpts are different but df are equal --> fail test.'''
#  assert even_LM.FeatureInput != standard[0].FeatureInput


'''Unsure how to make the following faster since the constructs are built real-time.'''
'''But these three take up 10 seconds.'''
def test_Laminate_num_middle1():
    '''Check no more than one middle layer Lamina is in a Laminate.'''
    actual = []
    for Geo in Geos_full2:
        layers = constructs.Laminate(
            bdft.get_FeatureInput(
                Geo,
                load_params=load_params,
                mat_props=mat_props,
                model='Wilson_LT',
            ))._check_layer_order()
        actual.append(layers.count('M'))
        expected = [1] * len(layers)
    #assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return actual


def test_Laminate_num_outer1():
    '''Check no more than two outer layer Lamina are in a Laminate.'''
    actual = []
    for Geo in Geos_full2:
        layers = constructs.Laminate(
            bdft.get_FeatureInput(
                Geo,
                load_params=load_params,
                mat_props=mat_props,
                model='Wilson_LT',
            ))._check_layer_order()
        actual.append(layers.count('O'))
        expected = [1] * len(layers)
    #assert actual <= expected
    nt.assert_less_equal(actual, expected)
    #return actual


# Test order
def test_Laminate_laminae_order1():
    '''Use built-in function to check stacking order.'''
    actual = []
    for Geo in Geos_full:
        # Returns the stacking order each; plus has an internal assert if mismatch found
        actual.append(constructs.Laminate(bdft.get_FeatureInput(
            Geo,
            load_params=load_params,
            mat_props=mat_props,
            model='Wilson_LT'))._check_layer_order()
        )
    expected = [
        ['M'],
        ['O', 'O'],
        ['O', 'M', 'O'],
        ['O', 'I', 'I', 'O'],
        ['O', 'I', 'M', 'I', 'O'],
        ['O', 'I', 'M', 'I', 'O'],
        ['O', 'I', 'M', 'I', 'O'],
        ['O', 'I', 'I', 'M', 'I', 'I', 'O'],
        ['O', 'I', 'I', 'M', 'I', 'I', 'O'],
    ]
    nt.assert_equal(actual, expected)


#------------------------------------------------------------------------------
# LAMINATEMODEL
#------------------------------------------------------------------------------
'''Tests > 1s are here, likely due to calling constructors.'''
# Added in 0.4.12; modified from previous Laminate test
class TestLaminateModel():
    '''Contain LaminateModel related tests.'''

    # TODO: some tests are relying on laminator for multicases; consider replacing
    # to use bare constructs
    # TODO: Fix use of get_FeatureInput instead
    case = distributions.laminator(geos=dft.geos_standard)
    cases = distributions.laminator(geos=dft.geos_all, ps=[2,3,4,5], verbose=True)
    ##cases = distributions.laminator(geos=dft.geos_all, ps=[1, 2, 3, 4, 5], verbose=True)

    # Tests for LaminateModel prints
    def test_LaminateModel_print1(self):
        '''Check Laminate.__repr__ output.'''
        geo_input = '400-[200]-800'
        #FI = self.bdft.get_FeatureInput(G(geo_input))
        FI = dft.FeatureInput
        FI['Geometry'] = G(geo_input)

        actual = constructs.LaminateModel(FI).__repr__()
        expected = '<lamana LaminateModel object (400.0-[200.0]-800.0), p=5>'
        nt.assert_equal(actual, expected)

    def test_LaminateModel_print2(self):
        '''Check Laminate.__repr__ symmetry output.'''
        geo_input = '400-[200]-400S'
        #FI = self.bdft.get_FeatureInput(G(geo_input))
        FI = dft.FeatureInput
        FI['Geometry'] = G(geo_input)

        actual = constructs.LaminateModel(FI).__repr__()
        expected = '<lamana LaminateModel object (400.0-[200.0]-400.0S), p=5>'
        nt.assert_equal(actual, expected)

    # Test properties
    def test_LaminateModel_prop_frame(self):
        '''Check returns DataFrame.'''
        geo_input = '400-[200]-400S'
        #FI = self.bdft.get_FeatureInput(G(geo_input))
        FI = dft.FeatureInput
        FI['Geometry'] = G(geo_input)

        LM = constructs.LaminateModel(FI)
        actual = isinstance(LM.frame, pd.DataFrame)
        nt.assert_true(actual)

    def test_LaminateModel_prop_extrema(self):
        case1 = distributions.laminator(dft.geos_full, ps=[5])
        case2 = distributions.laminator(dft.geos_full, ps=[2])

        for case_full, case_trimmed in zip(case1.values(), case2.values()):
            for LM_full, LM_trimmed in zip(case_full.LMs, case_trimmed.LMs):
                actual = LM_full.extrema
                actual.reset_index(drop=True, inplace=True)
                expected = LM_trimmed.LMFrame
                #print(actual)
                #print(expected)
                ut.assertFrameEqual(actual, expected)

    def test_LaminateModel_prop_max(self):
        '''Check the max attribute and maximum stresses.'''
        for case_ in self.case.values():
            for LM in case_.LMs:
                actual = LM.max_stress
                d = {
                    0: 0.378731,
                    5: 0.012915,
                    10: 0.151492,
                    14: -0.151492,
                    19: -0.012915,
                    24: -0.378731,
                }
                s = pd.Series(d)
                s.name = 'stress_f (MPa/N)'
                expected = s
                #assert actual.all() == expected.all()
                ut.assertSeriesEqual(actual, expected, check_less_precise=True)

    def test_LaminateModel_prop_min1(self):
        '''Check the min attribute and minimum stresses.'''
        for case_ in self.case.values():
            for LM in case_.LMs:
                actual = LM.min_stress
                d = {
                    4: 0.227238,
                    9: 0.008610,
                    15: -0.008610,
                    20: -0.227238,
                }
                s = pd.Series(d)
                s.name = 'stress_f (MPa/N)'
                expected = s
                #assert actual.all() == expected.all()
                ut.assertSeriesEqual(actual, expected, check_less_precise=True)

    def test_LaminateModel_prop_min2(self):
        '''Check the min attribute and minimum stresses returns None if no disconts.'''
        # Monoliths do not have disconts; will use to trigger the return
        for case in self.cases.values():
            actual = [LM.min_stress for LM in case.LMs if LM.alias == 'Monolith']
            expected = [None] * len(actual)
            nt.assert_equal(actual, expected)


class TestDecoupledLaminateModel():
    '''Contain test from the Decouple Branch.'''
    # 0.4.12
    FeatureInput = {
        'Geometry': input_.Geometry('400.0-[200.0]-800.0'),
        'Materials': ['HA', 'PSu'],
        'Model': 'Wilson_LT',
        'Parameters': {'P_a': 1, 'R': 0.012, 'a': 0.0075, 'p': 5, 'r': 0.0002},
        'Properties': {'Modulus': {'HA': 52000000000.0, 'PSu': 2700000000.0},
        'Poissons': {'HA': 0.25, 'PSu': 0.33}}
    }

    S = constructs.Stack(FeatureInput)
    L = constructs.Laminate(FeatureInput)
    LM = constructs.LaminateModel(FeatureInput)

    S_attrs = [name for name, obj in inspect.getmembers(S) if not name.startswith('__')]
    L_attrs = [name for name, obj in inspect.getmembers(L) if not name.startswith('__')]
    LM_attrs = [name for name, obj in inspect.getmembers(LM) if not name.startswith('__')]

    @nt.raises(ModelError)
    def test_LaminateModel_INDET_error1(self):
        '''Verify error is raised if p=1; INDET is detected.  LaminateModel not updated.'''
        FeatureInput = self.FeatureInput.copy()
        FeatureInput['Parameters']['p'] = 1
        actual = constructs.LaminateModel(FeatureInput)

#     @nt.raises(OSError)
#     def test_LaminateModel_write_error(self):
#         # shift working dir
#         # try to write
#         # prevent export being written in the wrong place
#         pass

    def test_LaminateModel_attr_inheritence1(self):
        '''Verify LaminateModel attrs > Laminate attrs > Stack attrs.'''
        actual1 = len(self.LM_attrs) > len(self.L_attrs)
        actual2 = len(self.L_attrs) > len(self.S_attrs)
        nt.assert_true(actual1)
        nt.assert_true(actual2)

    def test_LaminateModel_attr_inheritence2(self):
        '''Verify confirm inherited attrs are subsets.'''
        actual1 = set(self.S_attrs).issubset(self.L_attrs)
        actual2 = set(self.L_attrs).issubset(self.LM_attrs)
        nt.assert_true(actual1)
        nt.assert_true(actual2)

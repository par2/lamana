#------------------------------------------------------------------------------
'''Confirm accurate execution of building cases.'''

import os
import copy
import logging
import itertools as it

import nose.tools as nt
import pandas as pd

from lamana import input_
from lamana import distributions
from lamana import constructs
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt                      # for post Laminate, i.e. Cases only

# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {
    'R': 12e-3,                                            # specimen radius
    'a': 7.5e-3,                                           # support ring radius
    'p': 4,                                                # points/layer
    'P_a': 1,                                              # applied load
    'r': 2e-4,                                             # radial distance from center loading
}

mat_props = {
    'HA': [5.2e10, 0.25],
    'PSu': [2.7e9, 0.33],
}
mat_props2 = {
    'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9, 'dummy': 1.0e9},
    'Poissons': {'HA': 0.25, 'PSu': 0.33, 'dummy': 0.5}
}

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

bdft = input_.BaseDefaults()
case1 = distributions.Case(load_params, mat_props)
case2 = distributions.Case(load_params, mat_props)
case3 = distributions.Case(load_params, mat_props2)

# Material Order
# Homogenous
expected1 = [
    ['HA'],
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
expected2 = [
    ['PSu'],
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
expected3 = [
    ['PSu'],
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
expected4 = [
    ['PSu'],
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


class TestCaseTypes():
    '''Verify the resulting type when called Case is a LaminateModel (or Laminate).'''

    case0 = distributions.Case(load_params, mat_props)
    case0.apply(['400-200-800'])

    def test_Case_type_LaminateModel1(self):                # added 0.4.12-dev0
        '''Verify the default output Case object is a LaminateModel.'''
        actual = isinstance(self.case0.LMs[0], constructs.LaminateModel)
        nt.assert_true(actual)

    # TODO: Add tests for type verification for Laminate

    # TODO: Add test for rollback here


# Case Arguments -------------------------------------------------------------
#  TODO: Convert, organize tests  to LPEP 001.015
@nt.raises(TypeError)
def test_Case_arg_empty1():
    '''If no parameters passed to Case(), raise TypeError.'''
    case0 = distributions.Case()


@nt.raises(TypeError)
def test_Case_arg_empty2():
    '''Check raise Exception if not passed load_params; first test.'''
    case0 = distributions.Case(mat_props)


@nt.raises(TypeError)
def test_Case_arg_empty3():
    '''Check raise Exception if not passed mat_props.'''
    case0 = distributions.Case(load_params)


@nt.raises(ValueError)
def test_Case_mth_apply_arg_empty1():
    '''Check raise Exception if not passed a geometries.'''
    case0 = distributions.Case(load_params, mat_props)
    actual = case0.apply()


# Case Attributes -------------------------------------------------------------
def test_Case_attr_parameters1():
    '''Confirm dict inputs (static data).'''
    actual = case1.load_params
    expected = {'P_a': 1, 'R': 0.012, 'a': 0.0075, 'p': 4, 'r': 2e-4}
    nt.assert_equal(actual, expected)

# TODO: Test Series equality of load_params


# Using a sample of geometries
def test_Case_attr_material_order0():
    '''Check property setter; materials changes the _material attribute.'''
    case2.materials = ['PSu', 'HA']
    actual = case2._materials
    expected = case2.materials
    nt.assert_equal(actual, expected)


def test_Case_attr_materials_order1():
    '''Check homogenous laminate gives same material.'''
    case2.materials = ['HA']                               # set order
    case2.apply(bdft.geos_sample)
    for snap, e in zip(case2.snapshots, expected1):        # truncates to expected list
        actual = snap['matl'].tolist()
        #print(actual)
        nt.assert_equal(actual, e)


def test_Case_attr_materials_order2():
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


def test_Case_attr_materials_order3():
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


def test_Case_attr_materials_order4():
    '''Check multi-phase laminate, matl > 2, cycles through list.'''
    case3.materials = ['PSu', 'HA', 'dummy']               # set order
    case3.apply(bdft.geos_sample)
    for snap, e in zip(case3.snapshots, expected4):        # truncates to expected list
        actual = snap['matl'].tolist()
        #print(actual)
        nt.assert_equal(actual, e)


@nt.raises(NameError)
def test_Case_attr_materials_order5():
    '''Check error is thrown if materials are not found inmat_props.'''
    case2.materials = ['PSu', 'HA', 'dummy']               # set order
    case2.apply(bdft.geos_sample)
    for snap, e in zip(case2.snapshots, expected2):        # truncates to expected list
        actual = snap['matl'].tolist()
        nt.assert_equal(actual, e)


def test_Case_attr_properties1():
    '''Confirm dict conversion to Dataframe (static data) and values.'''
    d = {
        'Modulus': pd.Series([52e9, 2.7e9], index=['HA', 'PSu']),
        'Poissons': pd.Series([0.25, 0.33], index=['HA', 'PSu'])
    }
    expected = all(pd.DataFrame(d))
    actual = all(case1.properties)
    nt.assert_equal(actual, expected)


def test_Case_attr_properties2():
    '''Check the order of the properties DataFrame when materials is reset.'''
    expected = ['PSu', 'HA']
    case2.materials = expected                             # set order
    case2.apply(bdft.geos_standard)
    actual = case2.properties.index.tolist()               # truncates to expected list
    #print(actual)
    nt.assert_equal(actual, expected)


# Case Special Methods --------------------------------------------------------
# NOTE: Shift in paradigms, first use of test class to contain variables.
class TestCaseComparisons():
    '''Check __eq__ and __ne__ of Case objects. BETA.'''

    # Instantiate cases for comparison
    # NOTE: Keep pertinent instantiations contained in a single scope
    # NOTE: Modifications - add instantiations, simply add self to variable calls.
    dft = wlt.Defaults()

    case1a = distributions.Case(dft.load_params, dft.mat_props)
    case1b = distributions.Case(dft.load_params, dft.mat_props)
    case1c = distributions.Case(dft.load_params, dft.mat_props)
    case1d = distributions.Case(dft.load_params, dft.mat_props)
    case1e = distributions.Case(dft.load_params, dft.mat_props)
    case1a.apply(dft.geos_all)
    case1b.apply(dft.geos_all)
    case1c.apply(dft.geo_inputs['all'])
    case1d.apply(dft.geos_most)
    case1e.apply(dft.geos_special)

    def test_Case_spmthd_eq_1(self):
        '''Check __eq__ between hashable Cases object instances.'''
        # Compare Cases with single standards
        nt.assert_equal(self.case1a, self.case1b)
        nt.assert_equal(self.case1a, self.case1c)
        nt.assert_equal(self.case1b, self.case1a)
        nt.assert_equal(self.case1c, self.case1a)

    def test_Case_spmthd_eq_2(self):
        '''Check __eq__ between hashable Cases object instances.'''
        # Compare Cases with single standards
        nt.assert_true(self.case1a == self.case1b)
        nt.assert_true(self.case1a == self.case1c)
        nt.assert_true(self.case1b == self.case1a)
        nt.assert_true(self.case1c == self.case1a)

    def test_Case_spmthd_eq_3(self):
        '''Check __eq__ between unequal hashable Geometry object instances.'''
        nt.assert_false(self.case1a == self.case1d)
        nt.assert_false(self.case1a == self.case1e)
        nt.assert_false(self.case1d == self.case1a)
        nt.assert_false(self.case1e == self.case1a)

    def test_Case_spmthd_eq_4(self):
        '''Check returns NotImplemented if classes are not equal in __eq__.'''
        # See Also original implementation in test_constructs.py
        actual = self.case1a.__eq__(1)                     # isinstance(1, Cases()) is False
        expected = NotImplemented
        nt.assert_equal(actual, expected)

    def test_Case_spmthd_ne_1(self):
        '''Check __ne__ between hashable Geometry object instances.'''
        nt.assert_false(self.case1a != self.case1b)
        nt.assert_false(self.case1a != self.case1c)
        nt.assert_false(self.case1b != self.case1a)
        nt.assert_false(self.case1c != self.case1a)

    def test_Case_spmthd_ne_2(self):
        '''Check __ne__ between unequal hashable Geometry object instances.'''
        nt.assert_true(self.case1a != self.case1d)
        nt.assert_true(self.case1a != self.case1e)
        nt.assert_true(self.case1d != self.case1a)
        nt.assert_true(self.case1e != self.case1a)

    def test_Case_spmthd_ne3(self):
        '''Check returns NotImplemented if classes are not equal in __ne__.'''
        actual = self.case1a.__ne__(1)                     # isinstance(1, Cases()) is False
        expected = NotImplemented
        nt.assert_equal(actual, expected)


# Case Methods ----------------------------------------------------------------
# TODO: Change; too brittle
# Test Case().apply() properties
# The following use the same geos
case1.apply(geos_full)


def test_Case_mthd_apply_middle1():
    '''Check output for middle layer.'''
    #case1.apply(geos_full)
    actual = case1.middle
    expected = [2000.0, 0.0, 800.0, 0.0, 800.0, 400.0, 800.0, 800.0, 400.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_inner1():
    '''Check output for inner layer.'''
    #case1.apply(geos_full)
    actual = case1.inner
    expected = [
        [0.0], [0.0], [0.0], [500.0], [200.0], [200.0], [200.0], [100.0, 100.0],
        [100.0, 100.0]
    ]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_outer1():
    '''Check output for inner layer.'''
    #case1.apply(geos_full)
    actual = case1.outer
    expected = [0.0, 1000.0, 600.0, 500.0, 400.0, 400.0, 400.0, 400.0, 400.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_index1():
    '''Check list indexing of the last index.'''
    #case1.apply(geos_full)
    actual = case1.inner[-1]
    expected = [100.0, 100.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_index2():
    '''Check list indexing of the last element.'''
    #case1.apply(geos_full)
    actual = case1.inner[-1][-1]
    expected = 100.0
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_iterate1():
    '''Check iterating indexed list; first element of every inner_i.'''
    #case1.apply(geos_full)
    actual = [first[0] for first in case1.inner]
    expected = [0.0, 0.0, 0.0, 500.0, 200.0, 200.0, 200.0, 100.0, 100.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_iterate2():
    '''Check iterating indexed list; operate on last element of every inner_i.'''
    #case1.apply(geos_full)
    actual = [inner_i[-1] / 2.0 for inner_i in case1.total_inner_i]
    expected = [0.0, 0.0, 0.0, 500.0, 200.0, 200.0, 200.0, 100.0, 100.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_total1():
    '''Calculate total thicknesses (all).'''
    actual = case1.total
    expected = [2000.0, 2000.0, 2000.0, 2000.0, 2000.0,
                2000.0, 2000.0, 2000.0, 2000.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_total2():
    '''Calculate total middle layer thicknesses; all.'''
    actual = case1.total_middle
    expected = [2000.0, 0.0, 800.0, 0.0, 800.0, 800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_total3():
    '''Calculate total inner layer thicknesses; all.'''
    actual = case1.total_inner
    expected = [0.0, 0.0, 0.0, 1000.0, 400.0, 400.0, 400.0, 400.0, 400.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_total4():
    '''Calculate total of each inner_i layer thicknesses; all.'''
    actual = case1.total_inner_i
    expected = [[0.0], [0.0], [0.0], [1000.0], [400.0],
                [400.0], [400.0], [200.0, 200.0], [200.0, 200.0]]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_total5():
    '''Calculate total outer layer thicknesses; all.'''
    actual = case1.total_outer
    expected = [0.0, 2000.0, 1200.0, 1000.0, 800.0, 800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_slice1():
    '''Check list slicing of total thicknesses.'''
    #case1.apply(geos_full)
    actual = case1.total_outer[4:-1]
    expected = [800.0, 800.0, 800.0, 800.0]
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_unique1():
    '''Check getting a unique set of LaminateModels when unique=True.'''
    actual = distributions.Case(dft.load_params, dft.mat_props)
    actual.apply(['400-[200]-800'])
    expected = distributions.Case(dft.load_params, dft.mat_props)
    expected.apply(['400-200-800', '400-[200]-800'], unique=True)
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_unique2():
    '''Check getting a unique set of LaminateModels when unique=False.'''
    actual = distributions.Case(dft.load_params, dft.mat_props)
    actual.apply(['400-[200]-800', '400-[200]-800'])
    expected = distributions.Case(dft.load_params, dft.mat_props)
    expected.apply(['400-200-800', '400-[200]-800'], unique=False)
    nt.assert_equal(actual, expected)


@nt.raises(AssertionError)
def test_Case_mthd_apply_unique3():
    '''Check exception if comparing inaccurately LaminateModels when unique is False.'''
    actual = distributions.Case(dft.load_params, dft.mat_props)
    actual.apply(['400-[200]-800'])                   # wrong actual
    expected = distributions.Case(dft.load_params, dft.mat_props)
    expected.apply(['400-200-800', '400-[200]-800'], unique=False)
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_unique4():
    '''Check unique word skips iterating same geo strings; gives only one.'''
    standards = ['400-200-800', '400-[200]-800',
                 '400-200-800', '400-[200]-800',
                 '400-200-800', '400-[200]-800',
                 '400-200-800', '400-[200]-800']
    case1 = distributions.Case(dft.load_params, dft.mat_props)
    case2 = distributions.Case(dft.load_params, dft.mat_props)
    actual = case1.apply(standards, unique=True)
    expected = case2.apply(['400-[200]-800'])
    nt.assert_equal(actual, expected)


# Case refactor 0.4.5a1
def test_Case_mthd_apply_reapply():
    '''Check same result is returned by calling apply more than once.'''
    case1 = distributions.Case(dft.load_params, dft.mat_props)
    case1.apply(['400-[200]-800', '400-[200]-800', '100-200-1400'])
    case1.total_outer[1:-1]
    case1.apply(['400-[200]-800', '400-[200]-800', '100-200-1400'])
    case1.total_outer[1:-1]
    case1.apply(['400-[200]-800', '400-[200]-800', '100-200-1400'])
    actual = case1.total_outer
    expected = [800.0, 800.0, 200.0]
    nt.assert_equal(actual, expected)


# Laminate Structure
# Test LaminateModels
def test_Case_prop_snapshots1():
    '''Test the native DataFrame elements and dtypes. Resorts columns.  Uses pandas equals test.'''
    case1.apply(geos_full)
    cols = ['layer', 'matl', 'type', 't(um)']
    d = {
        'layer': [1, 2, 3, 4, 5, 6, 7],
        'matl': ['HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA'],
        'type': ['outer', 'inner', 'inner', 'middle', 'inner', 'inner', 'outer'],
        't(um)': [400.0, 100.0, 100.0, 800.0, 100.0, 100.0, 400.0]
    }

    actual = case1.snapshots[8]
    expected = pd.DataFrame(d)
#     bool_test = actual[cols].sort(axis=1).equals(expected.sort(axis=1))
#     #nt.assert_equal(bool_test, True)
#     nt.assert_true(bool_test)
    ut.assertFrameEqual(actual[cols], expected[cols])


def test_Case_mthd_apply_LaminateModels1():
    '''Test the native DataFrame elements and dtypes. Resorts columns.
    Uses pandas equals() test.  p is even.'''
    case1.apply(geos_full)
    d = {
        'layer': [1, 1, 1, 1,
                  2, 2, 2, 2,
                  3, 3, 3, 3,
                  4, 4, 4, 4,
                  5, 5, 5, 5,
                  6, 6, 6, 6,
                  7, 7, 7, 7],
        'matl': ['HA', 'HA', 'HA', 'HA',
                 'PSu', 'PSu', 'PSu', 'PSu',
                 'HA', 'HA', 'HA', 'HA',
                 'PSu', 'PSu', 'PSu', 'PSu',
                 'HA', 'HA', 'HA', 'HA',
                 'PSu', 'PSu', 'PSu', 'PSu',
                 'HA', 'HA', 'HA', 'HA'],
        'type': ['outer', 'outer', 'outer', 'outer',
                 'inner', 'inner', 'inner', 'inner',
                 'inner', 'inner', 'inner', 'inner',
                 'middle', 'middle', 'middle', 'middle',
                 'inner', 'inner', 'inner', 'inner',
                 'inner', 'inner', 'inner', 'inner',
                 'outer', 'outer', 'outer', 'outer'],
        't(um)': [400.0, 400.0, 400.0, 400.0,
                  100.0, 100.0, 100.0, 100.0,
                  100.0, 100.0, 100.0, 100.0,
                  800.0, 800.0, 800.0, 800.0,
                  100.0, 100.0, 100.0, 100.0,
                  100.0, 100.0, 100.0, 100.0,
                  400.0, 400.0, 400.0, 400.0]
    }
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


# Case Properties -------------------------------------------------------------
# TODO: Move
def test_Case_prop_size1():
    '''Check size property gives correct number for length of Case object.'''
    case_ = distributions.Case(dft.load_params, dft.mat_props)
    case_.apply(['400-[200]-800', '400-[100,100]-800', '400-[400]-400'])
    actual = case_.size
    expected = 3
    nt.assert_equal(actual, expected)
###


# TODO: Cleanup; move
# DataFrames ------------------------------------------------------------------
# Test p
'''Building expected DataFrames for tests can be tedious.  The following
functions help to build DataFrames for any p, i.e. the number
of replicated rows within each layer.'''


# NOTE: Replace keyword default with sentinel value
##def replicate_values(dict_, dict_keys=[], multiplier=1):
def replicate_values(dict_, dict_keys=None, multiplier=1):
    '''Read starter dict values and returns a dict with p replicated values.

    Parameters
    ----------
    dict_ : dict_
        Primitive information for laminates; list values.
    dict_keys : list, default None
        Order of keys.
    multiplier : int
        Number of time to repeat items in values.

    Examples
    --------
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
    if dict_keys is None:
        dict_keys = []

    # Repeats items in a list p times; hacker trick
    result = [{key: [val for val in value for _ in [value] * multiplier]}
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

d1 = {
    'layer': [1],
    'matl': ['HA'],
    'type': ['middle'],
    't(um)': [2000.0]
}

d2 = {
    'layer': [1, 2],
    'matl': ['HA',
             'PSu'],
    'type': ['outer',
             'outer'],
    't(um)': [1000.0,
              1000.0]
}
d3 = {
    'layer': [1, 2, 3],
    'matl': ['HA',
             'PSu',
             'HA'],
    'type': ['outer',
             'middle',
             'outer'],
    't(um)': [600.0,
              800.0,
              600.0]
}

d4 = {
    'layer': [1, 2, 3, 4],
    'matl': ['HA',
             'PSu',
             'HA',
             'PSu'],
    'type': ['outer',
             'inner',
             'inner',
             'outer'],
    't(um)': [500.0,
              500.0,
              500.0,
              500.0]
}

d5 = {
    'layer': [1, 2, 3, 4, 5],
    'matl': ['HA',
             'PSu',
             'HA',
             'PSu',
             'HA'],
    'type': ['outer',
             'inner',
             'middle',
             'inner',
             'outer'],
    't(um)': [400.0,
              200.0,
              800.0,
              200.0,
              400.0]
}
d8 = {
    'layer': [1, 2, 3, 4, 5, 6, 7],
    'matl': ['HA',
             'PSu',
             'HA',
             'PSu',
             'HA',
             'PSu',
             'HA'],
    'type': ['outer',
             'inner',
             'inner',
             'middle',
             'inner',
             'inner',
             'outer'],
    't(um)': [400.0,
              100.0,
              100.0,
              800.0,
              100.0,
              100.0,
              400.0]
}


#------------------------------------------------------------------------------
def test_Case_mthd_apply_LaminateModels_frames_p1():
    '''Check built DataFrames have correct p for each Lamina.

    Using two functions to build DataFrames: make_dfs() and replicate_values().
    This only tests four columns  ['layer', 'matl', 'type', 't(um)'].
    Be sure to test single, odd and even p, i.e. p = [1, 3, 4].

        1. Access DataFrames from laminate using frames
        2. Build dicts and expected DataFrames for a range of ps
        3. Equate the DataFrames and assert the truth of elements.

    UPDATE: the following functions should not be used.  makes_dfs is recommended
    for future tests.
    '''
    def make_actual_dfs(geos, p=1):
        '''Returns a list of DataFrames using the API '''
        load_params['p'] = p
        #print(load_params)
        case = distributions.Case(load_params, mat_props)
        case.apply(geos)
        #print(case.frames)
        return case.frames

    def make_expected_dfs(starter_dicts, keys, p=1):
        '''Return a list of custom DataFrames with p number rows.'''
        dfs = []
        for points in range(1, p + 1):                     # skips 0 (empty df)
            for dict_ in make_dfs(starter_dicts, dict_keys=keys, p=p):
                dfs.append(pd.DataFrame(dict_))
            return dfs

    # Starting inputs
    geos_custom = [g1, g2, g3, g4, g5, g8]
    dicts = [d1, d2, d3, d4, d5, d8]
    keys = ['layer', 'matl', 'type', 't(um)']
    load_params = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 4,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    mat_props = {
        'HA': [5.2e10, 0.25],
        'PSu': [2.7e9, 0.33],
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
def test_Case_mthd_apply_LaminateModels_side_p1():
    '''Check None is assigned in the middle for LaminateModels with odd rows.'''
    load_params = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 3,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.Case(load_params, mat_props)
    case.apply(geos_full2)
    dfs = case.frames
    #print(dfs)

    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index) // 2
        #print(half_the_stack)
        if 'None' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])  # None at the middle of odd rows
            #print(df['side'])
        if len(df.index) % 2 != 0:
            expected.append('None')
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_LaminateModels_side_p2():
    '''Check None is not in the DataFrame having even rows.'''
    load_params = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 8,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.Case(load_params, mat_props)
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


def test_Case_mthd_apply_LaminateModels_INDET1():
    '''Test INDET in the middle row for p = 1, odd laminates.'''
    load_params = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 1,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.Case(load_params, mat_props)
    case.apply(geos_full2)
    dfs = case.frames

    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index) // 2
        #print(half_the_stack)
        if 'INDET' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])
            #print(df['side'])
        if len(df.index) % 2 != 0:
            expected.append('INDET')
    #print(df)
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_LaminateModels_INDET2():
    '''Test INDET in the middle rows for p = 1, odd laminates.'''
    load_params = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 1,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.Case(load_params, mat_props)
    case.apply(geos_full2)
    dfs = case.frames

    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index) // 2
        #print(half_the_stack)
        if 'INDET' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])
            #print(df['side'])
        if len(df.index) % 2 != 0:
            expected.append('INDET')
    #print(df)
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


def test_Case_mthd_apply_LaminateModels_None1():
    '''Check None is assigned in the middle for LaminateModels with odd rows.'''
    load_params = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 3,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.Case(load_params, mat_props)
    case.apply(geos_full2)
    dfs = case.frames
    #print(dfs)

    actual = []
    expected = []
    for df in dfs:
        #print(df)
        half_the_stack = len(df.index) // 2
        #print(half_the_stack)
        if 'None' in df['side'].values:
            actual.append(df.loc[half_the_stack]['side'])
            #print(df['side'])
        if len(df.index) % 2 != 0:
            expected.append('None')
    #print(actual)
    #print(expected)
    #assert actual == expected
    nt.assert_equal(actual, expected)


class TestCaseExportMethods():
    '''Comprise tests for export methods of Case; use simple laminate and tempfiles.'''
    case = distributions.Case(load_params, mat_props)
    case.apply(['400-[200]-800', '400-[400]-400', '400-[100,100]-800'])

    # TODO: Consider adding a wrapper that checks the number of files is the same
    # before and after each test is run, else give a warning.  This to check no
    # stray files remain.
    def test_Case_mtd_to_csv1(self):
        '''Verify number of files written; use tempfiles.'''
        try:
            list_of_tupled_paths = self.case.to_csv(temp=True)
            actual1 = len(list_of_tupled_paths)
            actual2 = len([dash_fpath
                           for data_fpath, dash_fpath in list_of_tupled_paths])
            expected1 = 3                                  # tuples
            expected2 = 3                                  # dashboards
            nt.assert_equals(actual1, expected1)
            nt.assert_equals(actual2, expected2)
        finally:
            for data_fpath, dash_fpath in list_of_tupled_paths:
                os.remove(data_fpath)
                os.remove(dash_fpath)
                logging.info('File has been deleted: {}'.format(data_fpath))
                logging.info('File has been deleted: {}'.format(dash_fpath))

    def test_Case_mtd_to_csv2(self):
        '''Verify type of to_csv.'''
        try:
            result = self.case.to_csv(temp=True)
            actual1 = isinstance(result, list)
            actual2 = isinstance(result[0], tuple)
            nt.assert_true(actual1)
            nt.assert_true(actual2)
        finally:
            for data_fpath, dash_fpath in result:
                os.remove(data_fpath)
                os.remove(dash_fpath)
                logging.info('File has been deleted: {}'.format(data_fpath))
                logging.info('File has been deleted: {}'.format(dash_fpath))

    def test_Case_mtd_to_csv3(self):
        '''Verify files are removed if the `delete` keyword is True.'''
        list_of_tupled_paths = self.case.to_csv(temp=True, delete=True)
        actual1 = any([os.path.exists(data_fpath) for data_fpath, _ in list_of_tupled_paths])
        actual2 = any([os.path.exists(dash_fpath) for _, dash_fpath in list_of_tupled_paths])
        nt.assert_false(actual1)
        nt.assert_false(actual2)

    def test_Case_mtd_to_xlsx1(self):
        '''Verify returns 2 sheets per LamainateModel in the same file; half dashboards.'''
        try:
            workbook_fpath = self.case.to_xlsx(temp=True)
            excel_file = pd.ExcelFile(workbook_fpath)
            actual1 = len(excel_file.sheet_names)
            actual2 = len([fname for fname in excel_file.sheet_names
                          if fname.startswith('Dash')])
            expected1 = 6
            expected2 = actual1 / 2.
            nt.assert_equals(actual1, expected1)
            nt.assert_equals(actual2, expected2)
        finally:
            os.remove(workbook_fpath)
            logging.info('File has been deleted: {}'.format(workbook_fpath))

    def test_Case_mtd_to_xlsx2(self):
        '''Verify type of to_xlsx.'''
        try:
            result = self.case.to_xlsx(temp=True)
            actual = isinstance(result, str)
            nt.assert_true(actual)
        finally:
            os.remove(result)
            logging.info('File has been deleted: {}'.format(result))

    def test_Case_mtd_to_xlsx3(self):
        '''Verify files are removed if the `delete` keyword is True.'''
        workbook_fpath = self.case.to_xlsx(temp=True, delete=True)
        actual = os.path.exists(workbook_fpath)
        nt.assert_false(actual)

#------------------------------------------------------------------------------
# CASES
#------------------------------------------------------------------------------
# Setup -----------------------------------------------------------------------

dft = wlt.Defaults()
# TODO: Why deepcopy?  Why not dft.load_params everywhere?
# Looks like to change load_params without affecting default dft.load_params
load_params = copy.deepcopy(dft.load_params)
#load_params = dft.load_params


# Manual and Auto Cases for Attribute Tests
cases1a = distributions.Cases(dft.geo_inputs['5-ply'], ps=[2, 3, 4])
cases1b = distributions.Cases(dft.geo_inputs['5-ply'], ps=[2, 3, 4])
#cases1a = Cases(dft.geo_inputs['5-ply'], ps=[2,3,4])       # assumes Defaults
#cases1b = Cases(dft.geo_inputs['5-ply'], ps=[2,3,4])       # assumes Defaults
load_params['p'] = 2
# TODO: Rename; this is a case not cases
cases1c = distributions.Case(load_params, dft.mat_props)
cases1c.apply(dft.geo_inputs['5-ply'])


# Manual Cases for Selection Tests
cases2a = distributions.Cases(dft.geos_special, ps=[2, 3, 4])
#cases2a = Cases(dft.geos_special, ps=[2,3,4])
load_params['p'] = 2
# TODO: Rename following.  These are Case objects, not Cases
cases2b2 = distributions.Case(load_params, dft.mat_props)
cases2b2.apply(dft.geos_special)
load_params['p'] = 3
cases2b3 = distributions.Case(load_params, dft.mat_props)
cases2b3.apply(dft.geos_special)
load_params['p'] = 4
cases2b4 = distributions.Case(load_params, dft.mat_props)
cases2b4.apply(dft.geos_special)


# Manual for mixed geometry string inputs
mix = dft.geos_most + dft.geos_standard                   # 400-[200]-800 common to both
cases3a = distributions.Cases(mix, unique=True)
#cases3a = Cases(mix, unique=True)
load_params['p'] = 5
cases3b5 = distributions.Case(load_params, dft.mat_props)
cases3b5.apply(mix)


# Manual for standard Cases for comparisons and others
cases4a = distributions.Cases(['400-[200]-800'])
cases4b = distributions.Cases(['400-[200]-800'])
cases4c = distributions.Cases(['400-200-800'])
cases4d = distributions.Cases(['1000-[0]-0'])
cases4e = distributions.Cases(['400-[150,50]-800'])

# Manual fixed length for slicing
cases5a = distributions.Cases(['400-[200]-800', '400-[100,100]-400', '400-[400]-400'])


# TESTS -----------------------------------------------------------------------
# Cases Special Methods -------------------------------------------------------

@nt.raises(NotImplementedError)
def test_Cases_spmthd_set1():
    '''Check __setitem__ is not implemented.'''
    # Setting to Cases() would be difficult due to the custom dict type; reinstantiation is encouraged.
    cases1a[2] = 'test'


def test_Cases_spmthd_get1():
    '''Check __getitem__ of all cases contained in cases.'''
    actual1 = cases1a.__getitem__(0)
    actual2 = cases1a.get(0)
    actual3 = cases1a[0]
    expected = cases1b[0]
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)
    nt.assert_equal(actual3, expected)


def test_Cases_spmthd_get2():
    '''Check __getitem__ handles negative indicies.'''
    full_range = [case for case in cases5a]
    actual1 = cases5a[-1]                                  # negative index
    actual2 = cases5a[-2]                                  # negative index
    expected1 = full_range[-1]
    expected2 = full_range[-2]
    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)


def test_Cases_spmthd_get3():
    '''Check __getitem__ of Cases using slice notation.'''
    #'''Check __getslice__ of Cases object; can use slice notation.'''
    # NOTE: most implementation is actually in __getitem__
    actual1 = cases5a[0:2]                                 # range of dict keys
    actual2 = cases5a[0:3]                                 # full range of dict keys
    actual3 = cases5a[:]                                   # full range
    actual4 = cases5a[1:]                                  # start:None
    actual5 = cases5a[:2]                                  # None:stop
    actual6 = cases5a[:-1]                                 # None:negative index
    actual7 = cases5a[:-2]                                 # None:negative index
    # TODO: Following are negative steps; NotImplemented (0.4.11.dev0)
    #actual8 = cases5a[0:-1:-2]                             # start:stop:step
    #actual9 = cases5a[::-1]                                # reverse

    full_range = [case for case in cases5a]
    expected1 = full_range[0:2]
    expected2 = full_range[0:3]
    expected3 = full_range[:]
    expected4 = full_range[1:]
    expected5 = full_range[:2]
    expected6 = full_range[:-1]
    expected7 = full_range[:-2]

    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)
    nt.assert_equal(actual4, expected4)
    nt.assert_equal(actual5, expected5)
    nt.assert_equal(actual6, expected6)
    nt.assert_equal(actual7, expected7)


@nt.raises(KeyError)
def test_Cases_spmthd_get4():
    '''Check __getitem__ of non-item in cases.'''
    actual1 = cases1a[300]
    expected = 'dummy'
    nt.assert_equal(actual1, expected)


def test_Cases_spmthd_del1():
    '''Check __del__ of all cases contained in cases.'''
    cases = cases1b
    del cases[1]
    actual1 = len(cases)
    ps = {case.p for case in cases1a}
    ncases = len(dft.geo_inputs['5-ply']) * len(ps)
    expected = ncases - 1
    nt.assert_equal(actual1, expected)


##def test_Cases_spmthd_iter1():
##    '''Check Cases() iterates by values (not keys).'''
##    actual = [caselet for caselet in cases1a]
##    expected = [caselet for caselet in cases1a.values()]
##    nt.assert_equal(actual, expected)


def test_Cases_spmthd_len1():
    '''Check __len__ of all cases contained in cases.'''
    actual1 = cases1a.__len__()
    actual2 = len(cases1a)
    ps = {case.p for case in cases1a}
    ncases = len(dft.geo_inputs['5-ply']) * len(ps)
    expected = ncases
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


# Instance comparisons; See Also test_input for Geometry comparisons
def test_Cases_spmthd_eq_1():
    '''Check __eq__ between hashable Cases object instances.'''
    # Compare Cases with single standards
    nt.assert_equal(cases4a, cases4b)
    nt.assert_equal(cases4a, cases4c)
    nt.assert_equal(cases4b, cases4a)
    nt.assert_equal(cases4c, cases4a)


def test_Cases_spmthd_eq_2():
    '''Check __eq__ between hashable Cases object instances.'''
    # Compare Cases with single standards
    nt.assert_true(cases4a == cases4b)
    nt.assert_true(cases4a == cases4c)
    nt.assert_true(cases4b == cases4a)
    nt.assert_true(cases4c == cases4a)


def test_Cases_spmthd_eq_3():
    '''Check __eq__ between unequal hashable Geometry object instances.'''
    nt.assert_false(cases4a == cases4d)
    nt.assert_false(cases4a == cases4e)
    nt.assert_false(cases4d == cases4a)
    nt.assert_false(cases4e == cases4a)


def test_Cases_spmthd_eq_4():
    '''Check returns NotImplemented if classes are not equal in __eq__.'''
    # See Also original implementation in test_constructs.py
    actual = cases4a.__eq__(1)                             # isinstance(1, Cases()) is False
    expected = NotImplemented
    nt.assert_equal(actual, expected)


def test_Cases_spmthd_ne_1():
    '''Check __ne__ between hashable Geometry object instances.'''
    nt.assert_false(cases4a != cases4b)
    nt.assert_false(cases4a != cases4c)
    nt.assert_false(cases4b != cases4a)
    nt.assert_false(cases4c != cases4a)


def test_Cases_spmthd_ne_2():
    '''Check __ne__ between unequal hashable Geometry object instances.'''
    nt.assert_true(cases4a != cases4d)
    nt.assert_true(cases4a != cases4e)
    nt.assert_true(cases4d != cases4a)
    nt.assert_true(cases4e != cases4a)


def test_Cases_spmthd_ne_3():
    '''Check returns NotImplemented if classes are not equal in __ne__.'''
    actual = cases4a.__ne__(1)                             # isinstance(1, Cases()) is False
    expected = NotImplemented
    nt.assert_equal(actual, expected)


# String representations
def test_Cases_spmthd_str1():
    '''Check Cases.__str__ output.'''
    geo_strings = ['400-[200]-800', '400-[200]-400S']
    actual = distributions.Cases(geo_strings).__str__()
    expected = ("{0: <<class 'lamana.distributions.Case'> p=5, size=1>,"
                " 1: <<class 'lamana.distributions.Case'> p=5, size=1>}")
    nt.assert_equal(actual, expected)


def test_Cases_spmthd_repr1():
    '''Check Cases.__repr__ output.'''
    geo_strings = ['400-[200]-800', '400-[200]-400S']
    representation = distributions.Cases(geo_strings).__repr__()
    # Unable replicate the address of the first entry
    # e.g. '<lamana.distributions.Cases object at 0x0000000007D65860>'
    # Thus trimming the actual repr
    expected = (" {0: <<class 'lamana.distributions.Case'> p=5, size=1>,"
                " 1: <<class 'lamana.distributions.Case'> p=5, size=1>}")
    trimmed = representation.split(',')
    actual = ','.join(trimmed[1:])
    nt.assert_equal(actual, expected)


# Cases Methods ---------------------------------------------------------------
def test_Cases_mthd_plot():
    '''Check plot implementation.'''
    # TODO: Try checking return is an ax instance
    pass

# DEPRECATE: 0.4.11
# def test_Cases_mthd_tocsv():
#     '''Check utils.write_csv is called, file is written to default directory.
#
#     Notes
#     -----
#     Add files to export, then removes them.  Adapted from test_tools_write1().
#     Instantiate a Cases object, iterate, call `to_csv` that writes the file.
#     The read those temporary files.
#
#     See Also
#     --------
#     - utils.tools.write_csv(): main writer for csv files.
#     - test_tools_write1(): writes, tests and cleans up temporary files.
#
#     '''
#     try:
#         # TODO: Add standard case to the module namespace to reduce building.
#         cases = distributions.Cases(['400-200-800'])
#         # Write files to default output dir
#         # CAUTION: assumes the order of case.to_csv is the same as Cases.LMs
#         expected_dfs = cases.frames
#         filepaths = cases.to_csv(prefix='temp')
#         for filepath, expected in zip(filepaths, expected_dfs):
#             # Read a file, get DataFrames
#             actual = pd.read_csv(filepath, index_col=0)
#             ut.assertFrameEqual(actual, expected)
#     finally:
#         # Remove temporary files
#         for filepath in filepaths:
#             os.remove(filepath)


# TODO: Move to prop section; brittle, moving causes failures; not apparent why; suspect load_params namespace collision
def test_Cases_prop_LMs1():
    '''Check viewing inside cases gives correct list.'''
    actual1 = cases1a.LMs
    # Manual cases
    load_params['p'] = 2
    cases1c2 = distributions.Case(load_params, dft.mat_props)
    cases1c2.apply(dft.geo_inputs['5-ply'])
    load_params['p'] = 3
    cases1c3 = distributions.Case(load_params, dft.mat_props)
    cases1c3.apply(dft.geo_inputs['5-ply'])
    load_params['p'] = 4
    cases1c4 = distributions.Case(load_params, dft.mat_props)
    cases1c4.apply(dft.geo_inputs['5-ply'])
    expected = cases1c2.LMs + cases1c3.LMs + cases1c4.LMs
    #print(cases1a2)
    #print(cases1a3)
    #print(cases1a4)
    #print(expected)
    nt.assert_equal(actual1, expected)


def test_Cases_mthd_select1():
    '''Check output of select method; single nplies only.'''
    actual = cases2a.select(nplies=4)
    expected = {LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                                      cases2b4.LMs) if LM.nplies == 4}
    nt.assert_set_equal(actual, expected)


def test_Cases_mthd_select2():
    '''Check output of select method; single ps only.'''
    actual = cases2a.select(ps=3)
    # Using a set expression to filter normal Case objects
    expected = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if LM.p == 3
    }
    nt.assert_set_equal(actual, expected)


def test_Cases_mthd_select3():
    '''Check output of select method; nplies only.'''
    actual = cases2a.select(nplies=[2, 4])
    expected = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if LM.nplies in (2, 4)
    }
    nt.assert_set_equal(actual, expected)


def test_Cases_mthd_select4():
    '''Check output of select method; ps only.'''
    actual = cases2a.select(ps=[2, 4])
    expected = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if LM.p in (2, 4)
    }
    nt.assert_set_equal(actual, expected)


# Cases `select` Cross-Selections
def test_Cases_mthd_select_crossselect1():
    '''Check (union) output of select method; single nplies and ps.'''
    actual1 = cases2a.select(nplies=4, ps=3)
    actual2 = cases2a.select(nplies=4, ps=3, how='union')
    expected = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if (LM.nplies == 4) | (LM.p == 3)
    }
    nt.assert_set_equal(actual1, expected)
    nt.assert_set_equal(actual2, expected)


def test_Cases_mthd_select_crossselect2():
    '''Check (intersection) output of select method; single nplies and ps.'''
    actual = cases2a.select(nplies=4, ps=3, how='intersection')
    expected1 = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if (LM.nplies == 4) & (LM.p == 3)
    }
    expected2 = {cases2b3.LMs[-1]}
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)


def test_Cases_mthd_select_crossselect3():
    '''Check (difference) output of select method; single nplies and ps.'''
    actual = cases2a.select(nplies=4, ps=3, how='difference')
    expected1 = cases2a.select(ps=3) - cases2a.select(nplies=4)
    expected2 = set(cases2b3.LMs[:-1])
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)


def test_Cases_mthd_select_crossselect4():
    '''Check (symmetric difference) output of select method; single nplies and ps.'''
    actual = cases2a.select(nplies=4, ps=3, how='symmetric difference')
    expected1 = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if (LM.nplies == 4) ^ (LM.p == 3)
    }
    list_p3 = list(cases2b3.LMs[:-1])                      # copy list
    list_p3.append(cases2b2.LMs[-1])
    list_p3.append(cases2b4.LMs[-1])
    expected2 = set(list_p3)
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)


def test_Cases_mthd_select_crossselect5():
    '''Check (union) output of select method; multiple nplies and ps.'''
    actual1 = cases2a.select(nplies=[2, 4], ps=[3, 4])
    actual2 = cases2a.select(nplies=[2, 4], ps=[3, 4], how='union')
    expected = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
        cases2b4.LMs) if (LM.nplies in (2, 4)) | (LM.p in (3, 4))
    }
    nt.assert_set_equal(actual1, expected)
    nt.assert_set_equal(actual2, expected)


def test_Cases_mthd_select_crossselect6():
    '''Check (intersection) output of select method; multiple nplies and ps.'''
    actual = cases2a.select(nplies=[2, 4], ps=[3, 4], how='intersection')
    expected1 = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if (LM.nplies in (2, 4)) & (LM.p in (3, 4))
    }
    nt.assert_set_equal(actual, expected1)


def test_Cases_mthd_select_crossselect7():
    '''Check (difference) output of select method; multiple nplies and single ps.'''
    # Subtracts nplies from ps.
    actual = cases2a.select(nplies=[2, 4], ps=3, how='difference')
    expected1 = cases2a.select(ps=3) - cases2a.select(nplies=[2, 4])
    expected2 = set(cases2b3.LMs[::2])
    nt.assert_set_equal(actual, expected1)
    nt.assert_set_equal(actual, expected2)


def test_Cases_mthd_select_crossselect8():
    '''Check (symmetric difference) output of select method; single nplies, multi ps.'''
    actual = cases2a.select(nplies=4, ps=[3, 4], how='symmetric difference')
    expected1 = {
        LM for LM in it.chain(cases2b2.LMs, cases2b3.LMs,
                              cases2b4.LMs) if (LM.nplies == 4) ^ (LM.p in (3, 4))
    }
    nt.assert_set_equal(actual, expected1)


# Cases Properties ------------------------------------------------------------

def test_Cases_prop_frames():
    '''Check frames method outputs DataFrames.  See other detailed Case().frames tests.'''
    dfs = cases1a.frames

    for df in dfs:
        actual = isinstance(df, pd.DataFrame)
        nt.assert_true(actual)


# Cases Caselets --------------------------------------------------------------
# TODO: Move to setup; looks like tests for caselet types; not containers
# This section is dedicated to Cases() tests primarily from 0.4.4b3
str_caselets = ['350-400-500', '400-200-800', '400-[200]-800']
list_caselets = [
    ['400-400-400', '400-[400]-400'], ['200-100-1400', '100-200-1400'],
    ['400-400-400', '400-200-800', '350-400-500'], ['350-400-500']
]
case_1 = distributions.Case(dft.load_params, dft.mat_props)
case_2 = distributions.Case(dft.load_params, dft.mat_props)
case_3 = distributions.Case(dft.load_params, dft.mat_props)
case_1.apply(['400-200-800', '400-[200]-800'])
case_2.apply(['350-400-500', '400-200-800'])
case_3.apply(['350-400-500', '400-200-800', '400-400-400'])
case_caselets = [case_1, case_2, case_3]
invalid_caselets = [1, 1, 1]


####
# TODO: Rename/Move.  Caselets are an attribute here, no?  test_Cases_attr_caselets#()
def test_Cases_arg_caselets1():
    '''Check cases from caselets of geometry strings.'''
    cases = distributions.Cases(str_caselets)
    #cases = Cases(str_caselets)
    actual = cases
    dict_expected = {}
    for i, caselet in enumerate(str_caselets):
        case = distributions.Case(dft.load_params, dft.mat_props)
        case.apply([caselet])
        dict_expected[i] = case
    expected = dict_expected
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)


def test_Cases_arg_caselets2():
    '''Check cases from caselets of lists of geometry strings.'''
    cases = distributions.Cases(list_caselets)
    #cases = Cases(list_caselets)
    actual = cases
    dict_expected = {}
    for i, caselet in enumerate(list_caselets):
        #print(caselet)
        case = distributions.Case(dft.load_params, dft.mat_props)
        case.apply(caselet)
        dict_expected[i] = case
    expected = dict_expected
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)


def test_Cases_arg_caselets3():
    '''Check cases from caselets of cases.'''
    cases = distributions.Cases(case_caselets)
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


@nt.raises(TypeError)
def test_Cases_arg_caselets4():
    '''Check cases raise error if caselets not a str, list or case. '''
    cases = distributions.Cases(invalid_caselets)


def test_Cases_arg_caselets_ps1():
    '''Check strs from caselets form for each ps.'''
    cases = distributions.Cases(str_caselets, ps=[4, 5])
    #cases = Cases(str_caselets, ps=[4,5])
    ##actual = cases                                         # unused
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    actual_ps = []
    for case in cases:
        actual_ps.append(case.p)
    actual1 = set(actual_ps)
    actual2 = len(actual_ps)
    actual3 = len(cases)
    expected1 = {4, 5}
    expected2 = 6
    expected3 = 6
    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)


#cases = Cases(list_caselets, ps=[2,3,4,5,7,9])
def test_Cases_arg_caselets_ps2():
    '''Check cases from string caselets for each ps.'''
    cases = distributions.Cases(list_caselets, ps=[4, 5])
    #cases = Cases(list_caselets, ps=[4,5])
    ##actual = cases                                         # unused
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    actual_ps = []
    for case in cases:
        actual_ps.append(case.p)
    actual1 = set(actual_ps)
    actual2 = len(actual_ps)
    actual3 = len(cases)
    expected1 = {4, 5}
    expected2 = 8
    expected3 = 8
    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)


def test_Cases_arg_caselets_ps3():
    '''Check cases from list caselets for each ps.'''
    cases = distributions.Cases(case_caselets, ps=[2, 3, 4, 5, 7, 9])
    #cases = Cases(case_caselets, ps=[2,3,4,5,7,9])
    ##actual = cases                                         # unused
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    actual_ps = []
    for case in cases:
        actual_ps.append(case.p)
    actual1 = set(actual_ps)
    actual2 = len(actual_ps)
    actual3 = len(cases)
    expected1 = {2, 3, 4, 5, 7, 9}
    expected2 = 18
    expected3 = 18
    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_equal(actual3, expected3)


@nt.raises(TypeError)
def test_Cases_arg_caselets_ps4():
    '''Check cases from list caselets raises Exceptions if p is non-integer.'''
    cases = distributions.Cases(case_caselets, ps=[2, 3, 'dummy', 5, 7, 9])


# Cases default assignments
##def test_Cases_import1():
##    '''Check passes if Defaults are not present in user-defined model.'''
##    cases = distributions.Cases(['400-[200]-800'], model='')
##    pass


# TODO: Unsure how to design elegantly w/o fake models modules lacking Defaults; tabled
##@nt.raises(ImportError)
##def test_Cases_import2():
##    '''Check raises ImportError if load_params can't import from defaults.'''
##    cases = distributions.Cases(case_caselets, load_params=None, model='')


##@nt.raises(ImportError)
##def test_Cases_import3():
##    '''Check raises ImportError if mat_params can't import from defaults.'''
##    cases = distributions.Cases(case_caselets, load_params=dft.load_params, model='')


# Cases Keywords --------------------------------------------------------------
def test_Cases_kw_combine1():
    '''Check caselets of geometry strings combine into a single case.'''
    cases = distributions.Cases(str_caselets, combine=True)
    #cases = Cases(str_caselets, combine=True)
    actual = cases
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(str_caselets)
    expected = {0: case}
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)


def test_Cases_kw_combine2():
    '''Check caselets of listed geometry strings combine into a single case.'''
    cases = distributions.Cases(list_caselets, combine=True)
    #cases = Cases(list_caselets, combine=True)
    actual = cases
    list_combined = ['100.0-[200.0]-1400.0', '400.0-[400.0]-400.0',
                     '350.0-[400.0]-500.0', '400.0-[200.0]-800.0',
                     '200.0-[100.0]-1400.0']
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(list_combined)
    expected = {0: case}
    print(actual.LMs, expected[0].LMs)
    # Any use of set() changes order; this case _get_unique makes these dissimlar
    nt.assert_set_equal(set(actual.LMs), set(expected[0].LMs))


def test_Cases_kw_combine3():
    '''Check caselets of cases combine into a single case.'''
    cases = distributions.Cases(case_caselets, combine=True)
    #cases = Cases(case_caselets, combine=True)
    actual = cases
    list_combined = [
        '400.0-[400.0]-400.0',
        '400.0-[200.0]-800.0',
        '350.0-[400.0]-500.0'
    ]
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(list_combined)
    expected = {0: case}
    print(actual.LMs, expected[0].LMs)
    # Any use of set() changes order; this case _get_unique makes these dissimlar
    nt.assert_set_equal(set(actual.LMs), set(expected[0].LMs))


@nt.raises(TypeError)
def test_Cases_kw_combine4():
    '''Check empty caselet throw error.'''
    cases = distributions.Cases([], combine=True)
    #cases = Cases([], combine=True)
    actual = cases
    list_combined = [
        '400.0-[400.0]-400.0',
        '400.0-[200.0]-800.0',
        '350.0-[400.0]-500.0',
    ]
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(list_combined)
    expected = {0: case}
    #print(actual, expected)
    # Since Cases is not a true dict, we iterate values
    for a, e in zip(actual, expected.values()):
        nt.assert_equal(a, e)


def test_Cases_kw_unique1():
    '''Check unique keyword of string caselets; ignores singles since already unique.'''
    cases = distributions.Cases(str_caselets, unique=True)
    #cases = Cases(str_caselets, unique=True)
    actual = set(cases.LMs)
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['350-400-500', '400-200-800', '400-200-800'])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected)


def test_Cases_kw_unique2():
    '''Check unique keyword of string caselets gives unique cases.'''
    cases = distributions.Cases(list_caselets, unique=True)
    #cases = Cases(list_caselets, unique=True)
    actual = set(cases.LMs)
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['400-[400]-400', '200-100-1400', '100-200-1400',
                '400-200-800', '350-400-500'])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected)


def test_Cases_kw_unique3():
    '''Check unique keyword of string caselets gives unique cases.'''
    cases = distributions.Cases(case_caselets, unique=True)
    #cases = Cases(case_caselets, unique=True)
    actual = set(cases.LMs)
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['400-[200]-800', '350-400-500', '400-400-400'])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected)


def test_Cases_kw_unique4():
    '''Check unique/combine keyword of string caselets gives unique cases; unifies singles.'''
    cases = distributions.Cases(str_caselets, combine=True, unique=True)
    #cases = Cases(str_caselets, combine=True, unique=True)
    actual = set(cases.LMs)
    case = distributions.Case(dft.load_params, dft.mat_props)
    case.apply(['350-400-500', '400-200-800'])
    expected = set(case.LMs)
    #print(actual, expected)
    nt.assert_set_equal(actual, expected)


# -----------------------------------------------------------------------------
#  Functions
# -----------------------------------------------------------------------------
# Laminator -------------------------------------------------------------------
class TestLaminator:

    dft = wlt.Defaults()

    def test_laminator_consistency1(self):
        '''Check laminator yields same LMFrame as classic case building.'''
        case = distributions.laminator(geos=self.dft.geos_all, ps=[5])
        for case_ in case.values():
            case1 = case_
        case2 = distributions.Case(self.dft.load_params, self.dft.mat_props)
        case2.apply(self.dft.geos_all)
        for actual, expected in zip(case1.LMs, case2.LMs):
            try:
                ut.assertFrameEqual(actual.LMFrame, expected.LMFrame)
            except(AssertionError):
                print('Actual DataFrame:', actual)
                print('Expected DataFrame:', expected)

    @nt.raises(Exception)
    def test_laminator_type1(self):
        '''Check raises Exception if geos is not a list.'''
        actual = distributions.laminator(geos={'400-200-800'})

    def test_laminator_type2(self):
        '''Check defaults to 400-200-800 nothing is passed in.'''
        case1 = distributions.laminator(geos=['400-200-800'])
        LM = case1[0]
        actual = LM.frames[0]
        case2 = distributions.Case(self.dft.load_params, self.dft.mat_props)
        case2.apply(['400-200-800'])
        expected = case2.frames[0]
        ut.assertFrameEqual(actual, expected)

    def test_laminator_type3(self):
        '''Check defaults triggered if nothing is passed in.'''
        case1 = distributions.laminator()
        LM = case1[0]
        actual = LM.frames[0]
        case2 = distributions.Case(self.dft.load_params, self.dft.mat_props)
        case2.apply(['400-200-800'])
        expected = case2.frames[0]
        ut.assertFrameEqual(actual, expected)

    # TODO: Move to input_
    def test_laminator_gencon1(self):
        '''Check returns a geometry string in General Convention; converts 'S'.'''
        case = distributions.laminator(['400-0-400S'])
        for case_ in case.values():
            for LM in case_.LMs:
                actual = input_.get_special_geometry(LM.LMFrame)
                ##expected = '400-[0]-800'                       # pre to_gen_convention()
                expected = '400.0-[0.0]-800.0'
                nt.assert_equal(actual, expected)

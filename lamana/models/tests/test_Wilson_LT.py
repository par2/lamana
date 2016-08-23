#------------------------------------------------------------------------------
# Tests for specific model: Wilson_LT

# Tests require exception handling to pass, either here or in Laminate
# Commented nt.raise --> handled in Laminate._update_calculations().
# Although program will run, tracebacks will print if exceptions were raised.

import pandas as pd
import nose.tools as nt

# from ... import input_
# from ... import distributions
# #from ...models import Wilson_LT as wlt
# from ...models import Wilson_LT as wlt
# from ...utils import tools as ut

from lamana import input_
from lamana import distributions
from lamana.models import Wilson_LT as wlt
from lamana.utils import tools as ut

# Global Cases
bdft = input_.BaseDefaults()
dft = wlt.Defaults()
case = distributions.laminator(geos=dft.geos_standard)
cases = distributions.laminator(geos=dft.geos_all, ps=[2, 3, 4, 5], verbose=True)

# TESTS -----------------------------------------------------------------------
# Tests that check the LMFrame rollsback to LFrame if exceptions are made.


# Models ----------------------------------------------------------------------
# NOTE: the test for errors are commented out because errors are caught
# in constructs and prevent breaking
@nt.raises(ZeroDivisionError)
def test_models_WisonLT_r1():
    '''Check singularity in log of moment eqn when r = 0; ZeroDivisionError.'''
    zero_r = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 5,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 0,                                            # radial distance from center loading
    }
    case = distributions.laminator(geos=dft.geos_standard, load_params=zero_r)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.LMFrame
            # Implementation unfinished; only used to trigger error


@nt.raises(ValueError)
def test_models_WisonLT_r2():
    '''Check singularity in log of moment eqn when r < 0; ValueError.'''
    neg_r = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5e-3,                                       # support ring radius
        'p': 5,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': -2e-3,                                        # radial distance from center loading
    }
    case = distributions.laminator(geos=dft.geos_standard, load_params=neg_r)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.LMFrame
            # Implementation unfinished; only used to trigger error


@nt.raises(ValueError, ZeroDivisionError)
def test_models_WisonLT_a1():
    '''Check the singularity in log of moment eqn when support radius, a = 0; ValueError.'''
    zero_a = {
        'R': 12e-3,                                        # specimen radius
        'a': 0,                                            # support ring radius
        'p': 5,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.laminator(geos=dft.geos_standard, load_params=zero_a)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.LMFrame
            # Implementation unfinished; only used to trigger error


@nt.raises(ValueError)
def test_models_WisonLT_a2():
    '''Check the singularity in log of moment eqn when support radius, a < 0; ValueError.'''
    neg_a = {
        'R': 12e-3,                                        # specimen radius
        'a': -7.5e-3,                                      # support ring radius
        'p': 5,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.laminator(geos=dft.geos_standard, load_params=neg_a)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.LMFrame
            #print(LM.LMFrame)
            # Implementation unfinished; only used to trigger error


@nt.raises(ValueError)
def test_models_WisonLT_a3():
    '''Raise exception if support radius, a, is larger than the sample radius, R.

    See Also
    --------
    - test_models_WisonLT_diameter1()

    '''
    big_a = {
        'R': 12e-3,                                        # specimen radius
        'a': 7.5,                                          # support ring radius
        'p': 5,                                            # points/layer
        'P_a': 1,                                          # applied load
        'r': 2e-4,                                         # radial distance from center loading
    }
    case = distributions.laminator(geos=dft.geos_standard, load_params=big_a)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.FeatureInput['Parameters']['a']
    expected = LM.FeatureInput['Parameters']['R']
    #assert actual < expected
    nt.assert_less(actual, expected)


# The following triggers an indeterminate error.  It is handled internally however.
# This example stands to remind such errors exist.
# @nt.raises(IndeterminateError)
# def test_models_WisonLT_INDET1():
#     '''Check exception for p=1 when INDET is found; do not calculate stress.'''
#     case = distributions.laminator(geos=['400-[200]-800'], ps=[1])
#     for i, LMs in case.items():
#         for LM in LMs:
#             actual = LM.LFrame
#             #print(LM.LMFrame)
#             # Implementation unfinished; only used to trigger error


def test_models_WisonLT_diameter1():
    '''Check the support radius, a, is smaller than the sample radius, R.'''
    case = distributions.laminator(geos=dft.geos_standard)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.FeatureInput['Parameters']['a']
    expected = LM.FeatureInput['Parameters']['R']
    #assert actual < expected
    nt.assert_less(actual, expected)


# First time using generators and processing laminates, expected values and asserts.
def test_models_WisonLT_stress1():
    '''Check max stresses equal for same geometry of different ps for standard.'''
    #actual = [LM.max_stress.reset_index(drop=True) for i, LMs in case.items() for LM in LMs]
    #print(actual)
    actuals = (LM.max_stress.reset_index(drop=True) for case_ in case.values() for LM in case_.LMs)
    ##actuals = (LM.max_stress.reset_index(drop=True) for i, LMs in case_multi_ps.items() for LM in LMs)
    d = {
        0: 0.378731,
        1: 0.012915,
        2: 0.151492,
        3: -0.151492,
        4: -0.012915,
        5: -0.378731,
    }
    expected = pd.Series(d)
    for actual in actuals:
        #print(actual)
        #print(expected)
        ut.assertSeriesEqual(actual, expected,
                             check_less_precise=True, check_names=False)


def test_models_WisonLT_stress2():
    '''Make sure maximum stress is found in .max_stress for different points (p).'''
    for case in cases.values():
        for LM in case.LMs:
            #print(LM.max_stress)
            #print(LM.LMFrame['stress_f (MPa/N)'])
            actual = LM.max_stress.max()
            df = LM.LMFrame
            ##col_name = df.columns.str.contains('stress_f')
            cols = [columns for columns in df.columns if 'stress_f' in columns]
            expected = df[cols].values.max()
            #print(actual)
            #print(expected)
            #print(cols)
            nt.assert_equals(actual, expected)


# Defaults --------------------------------------------------------------------
def test_WilsonLT_Defaults_attrs1():
    '''Confirm default geo_all equivalence in derived classes with base.'''
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
    default_attr1 = bdft.geos_all                          # Base attribute
    default_attr2 = dft.geos_all                           # Sub-class attribute
    expected = geos_all
    #print(set(default_dict))
    #print(set(expected)
    # Allows extension in BaseDefaults().geo_inputs
    actual1 = (set(default_attr1) >= set(expected))
    actual2 = (set(default_attr2) >= set(expected))
    #print(actual1)
    # TODO: is this supposed to be assert_true?
    nt.assert_true(actual1, expected)
    nt.assert_true(actual2, expected)

# TODO: Fix Geometry object comparisons. Add approp. tests.


def test_WilsonLT_Defaults_load_params1():
    '''Confirm default load_param values.'''
    actual = dft.load_params
    expected = {
        'R': 12e-3,                                  # specimen radius
        'a': 7.5e-3,                                 # support ring radius
        'p': 5,                                      # points/layer
        'P_a': 1,                                    # applied load
        'r': 2e-4,                                   # radial distance from center loading
    }
    nt.assert_equal(actual, expected)


def test_WilsonLT_Defaults_load_params2():
    '''Confirm defaults geometric parameters for Wilson_LT are constant.'''
    actual = dft.load_params
    expected = dft.load_params
    nt.assert_equal(actual, expected)


def test_WilsonLT_Defaults_mat_props1():
    '''Confirm default material parameters (Standard) for Wilson_LT are constant.'''
    actual = dft.mat_props
#     expected = {'HA' : [5.2e10, 0.25],
#                 'PSu' : [2.7e9, 0.33],
#                 }
    expected = {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
                'Poissons': {'HA': 0.25, 'PSu': 0.33}}
    nt.assert_equal(actual, expected)


def test_wilsonLT_Defaults_FeatureInput1():
    '''Confirm default FeatureInput values.'''
    G = input_.Geometry
    load_params = {
        'R': 12e-3,                                    # specimen radius
        'a': 7.5e-3,                                   # support ring radius
        'p': 5,                                        # points/layer
        'P_a': 1,                                      # applied load
        'r': 2e-4,                                     # radial distance from center loading
    }

#     mat_props = {'HA' : [5.2e10, 0.25],
#                  'PSu' : [2.7e9, 0.33],
#                  }

    mat_props = {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
                 'Poissons': {'HA': 0.25, 'PSu': 0.33}}

    '''Find way to compare materials DataFrames and Geo_objects .'''
    actual = dft.FeatureInput
    expected = {
        'Geometry': G('400-[200]-800'),
        'Parameters': load_params,
        'Properties': mat_props,
        'Materials': ['HA', 'PSu'],
        'Model': 'Wilson_LT',
        'Globals': None
    }
    ##del actual['Geometry']
    ##del actual['Materials']
    nt.assert_equal(actual, expected)

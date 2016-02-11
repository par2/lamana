#------------------------------------------------------------------------------
'''Test for consistency of utils.'''

import nose.tools as nt

import lamana as la
##from lamana.input_ import BaseDefaults
#from lamana.utils.tools import BaseDefaults
from lamana.models import Wilson_LT as wlt
from lamana.utils import tools as ut

##bdft = BaseDefaults()                              # from base class
dft = wlt.Defaults()                               # from inherited class in models; user


# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {
    'R': 12e-3,                                   # specimen radius
    'a': 7.5e-3,                                  # support ring radius
    'p': 5,                                       # points/layer
    'P_a': 1,                                     # applied load
    'r': 2e-4,                                    # radial distance from center loading
}

mat_props = {
    'HA': [5.2e10, 0.25],
    'PSu': [2.7e9, 0.33],
}

# TESTS -----------------------------------------------------------------------

# Defaults --------------------------------------------------------------------
# Minor checks for subclasses
def test_Defaults_load_params1():
    '''Confirm defaults geometric parameters for Wilson_LT are constant.'''
    actual = dft.load_params
    expected = load_params
    nt.assert_equal(actual, expected)

def test_Defaultsmat_props1():
    '''Confirm default material parameters (Standard) for Wilson_LT are constant.'''
    actual = dft.mat_props
    expected = {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
                'Poissons': {'HA': 0.25, 'PSu': 0.33}}
    nt.assert_equal(actual, expected)

# Laminator -------------------------------------------------------------------
def test_laminator_consistency1():
    '''Check laminator yields same LMFrame as classic case building.'''
    case = ut.laminator(geos=dft.geos_all, ps=[5])
    for case_ in case.values():
        case1 = case_
    case2 = la.distributions.Case(load_params, mat_props)
    case2.apply(dft.geos_all)
    #print(case1)
    #print(case2)
    for actual, expected in zip(case1.LMs, case2.LMs):
    #for actual, expected in zip(case1, case2.LMs):
        #print(actual)
        #print(expected)
        ut.assertFrameEqual(actual.LMFrame, expected.LMFrame)

#------------------------------------------------------------------------------
'''Confirm output of general models.'''

import nose.tools as nt

import lamana as la
from lamana.theories import BaseModel
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt

# Global Cases
dft = wlt.Defaults()
case = ut.laminator(geos=dft.geos_standard)
cases = ut.laminator(geos=dft.geos_all, ps=[2, 3, 4, 5], verbose=True)


# TESTS -----------------------------------------------------------------------
class TestBaseModel():
    '''Contain tests related to BaseModel and it's sub-classes.'''
    class Parent(BaseModel):
        def _use_model_():
            pass
        pass

    class Child(Parent):
        def _use_model_():
            pass
        pass

    parent = Parent()
    child = Child()

    @nt.raises(TypeError)
    def test_theories_BaseModel_error1():
        '''Verify TypeError raised if hook method not implemented; see abstractmethod.'''
        class Model(BaseModel):
            pass

    def test_theories_BaseModel_attr1(self):
        '''Check BaseModel attributes are initialized as None.'''
        actual1 = self.parent.model_name
        actual2 = self.parent.LaminateModel
        actual3 = self.parent.FeatureInput
        actual4 = self.child.model_name
        actual5 = self.child.LaminateModel
        actual6 = self.child.FeatureInput
        expected = None

        nt.assert_equal(actual1, expected)
        nt.assert_equal(actual2, expected)
        nt.assert_equal(actual3, expected)
        nt.assert_equal(actual4, expected)
        nt.assert_equal(actual5, expected)
        nt.assert_equal(actual6, expected)

    def test_theories_BaseModel_print1(self):
        '''Check BaseModel.__repr__ output.'''
        actual1 = 'Model' in self.parent.__repr__()
        actual2 = 'Model' in self.child.__repr__()
        nt.assert_true(actual1)
        nt.assert_true(actual2)

    def test_theories_BaseModel_subclass1(self):
        '''Verify subclassing of BaseModel.'''
        actual1 = issubclass(self.Parent, BaseModel)
        actual2 = issubclass(self.Child, self.Parent)
        actual3 = issubclass(self.Child, BaseModel)
        actual4 = isinstance(self.parent, BaseModel)
        actual5 = isinstance(self.child, self.Parent)
        actual6 = isinstance(self.child, BaseModel)
        nt.assert_true(actual1)
        nt.assert_true(actual2)
        nt.assert_true(actual3)
        nt.assert_true(actual4)
        nt.assert_true(actual5)
        nt.assert_true(actual6)


# -----------------------------------------------------------------------------
def test_theories_FeatureInput_globals1():
    '''Check globals are correct in updated FeatureInput for 400-[200]-800 post-theories.'''
    case = ut.laminator(geos=dft.geos_standard)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.FeatureInput                       # updated FeatureInput
            expected = {
                'Geometry': LM.Geometry,
                'Parameters': {
                    'P_a': 1,
                    'R': 0.012,
                    'a': 0.0075,
                    'p': 5,
                    'r': 2e-4
                },
                'Properties': LM.mat_props,
                'Materials': LM.materials,
                'Model': 'Wilson_LT',
                'Globals': {
                    'D_11T': 31.664191802890315,
                    'D_12T': 7.9406108505093584,
                    'D_11p': 0.033700807714524279,
                    'D_12n': -0.0084513446948124519,
                    'M_r': 0.15666895161350616,
                    'M_t': 0.216290324549788,
                    'K_r': 0.0034519261262397653,
                    'K_t:': 0.0059650953251038216,
                    'v_eq ': 0.25077573114575868},
                }
            #print(actual)
            #print(expected)
            #assert actual == expected
            '''Refactor dict comparison'''
            ##del actual['Materials']
            ##del expected['Materials']
            nt.assert_equal(actual, expected)


def test_theories_FeatureInput_globels2():
    '''Globals stay None if p=1, post LMFrame processing.'''
    # TODO: Opportunity to use a select method for p spefically.
    case = ut.laminator(geos=dft.geos_standard, ps=[1])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.FeatureInput['Globals']
            expected = None
            #print(LM.FeatureInput)
            nt.assert_equal(actual, expected)


def test_theories_FeatureInput_consistency1():
    '''Check FeatureInput from classic case building is consistent with
    utils tools automatic case building, post-theories.'''
    case1 = la.distributions.Case(dft.load_params, dft.mat_props)
    case1.apply(dft.geos_standard)                         # classic case build
    case2 = ut.laminator(geos=dft.geos_standard)           # auto case build
    LM = case1.LMs[0]
    ##del LM.FeatureInput['Geometry']                        # comp. unsupported 0.4.3d
    ##del LM.FeatureInput['Materials']
    expected = LM.FeatureInput

    for case_ in case2.values():
        for LM in case_.LMs:
            ##del LM.FeatureInput['Geometry']
            ##del LM.FeatureInput['Materials']
            actual = LM.FeatureInput                       # updated FeatureInput
        #print(actual)
        #print(expected)
        nt.assert_equal(actual, expected)


def test_theories_FeatureInput_differ():
    '''Check last FeatureInput Geometry in a case differfrom random others.'''
    case = ut.laminator(dft.geos_full)
    LM = [LM for case_ in case.values() for LM in case_.LMs]
    actual1 = LM[4].FeatureInput['Geometry']
    actual2 = LM[2].FeatureInput['Geometry']
    expected1 = la.input_.Geometry('400-[200]-800')
    expected2 = la.input_.Geometry('600-[0]-800')
    last_item = LM[-1].FeatureInput['Geometry']

    nt.assert_equal(actual1, expected1)
    nt.assert_equal(actual2, expected2)
    nt.assert_not_equal(actual1, last_item)
    nt.assert_not_equal(actual2, last_item)


@nt.raises(ZeroDivisionError)
def test_theories_Exception_default1():
    '''Check LMFrame is set by LFrame if exception raised.'''
    # Force an exception in Wilson_LT; r must be non-zero
    zero_r = {
        'R': 12e-3,                                       # specimen radius
        'a': 7.5e-3,                                      # support ring radius
        'p': 5,                                           # points/layer
        'P_a': 1,                                         # applied load
        'r': 0,                                           # radial distance from center loading
    }
    case = ut.laminator(geos=dft.geos_standard, load_params=zero_r)
    for case_ in case.values():
        for LM in case_.LMs:
            actual = LM.LMFrame
            expected = LM.LFrame
            #print(actual)                                 # should get LFrame
            ut.assertFrameEqual(actual, expected)


def test_theories_matl_order1():
    '''Check the material stack order is correct in LMFrame.'''
    # Amend geometry inputs even and dissimilar
    dft.geos_full.append(dft.geos_even[0])
    case = ut.laminator(geos=dft.geos_full)
    expected_mix = [
        ['HA'],
        ['HA', 'PSu'],
        ['HA', 'PSu', 'HA'],
        ['HA', 'PSu', 'HA', 'PSu'],
        ['HA', 'PSu', 'HA', 'PSu', 'HA'],
        ['HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu'],
        ['HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA'],
        ['HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA', 'PSu', 'HA'],
        # even ----------------------------------------------------------------
        ['HA', 'PSu']                                      # simple to preserve test
    ]
    for case_ in case.values():
        for LM, expected in zip(case_.LMs, expected_mix):
            grouped = LM.LMFrame.groupby('layer')['matl']
            actual = grouped.unique().tolist()
            #print(actual)
            #assert actual == expected
            nt.assert_equal(actual, expected)

'''Make smart test for for matl order2 with variables dissimilars and other geos.'''


# Conversion Tests ------------------------------------------------------------
# These tests verify the update of Laminate to LaminateModel.
# The `handshake` function is used to accomplish this.
# Since 0.4.11, the LFrame and LMFrame objects are housed in the `Laminate` class
# TODO:These objects must be decoupled to properly test this conversion.
class TestHandshake:
    '''Verify handshake function opeartes correctly.

    This class uses "fixtures" with sample models to test importing.
    Find the location in the following `Case.apply` methods.

    Modify the fixture as needed to test different imports.

    '''
    @nt.raises(ImportError)
    def test_theories_handshake_error1(self):
        '''Verify no model raises error.'''
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply(dft.geos_standard, model='no_model')

    def test_theories_handshake_hookclass1(self):
        '''Use fixture to import test hook method; if sucessful, get a Case.'''
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply(dft.geos_standard, model='fixtures.fixture_model_class')
        nt.assert_is_instance(case, la.distributions.Case)

    def test_theories_handshake_hookfunc1(self):
        '''Use fixture to import test hook function; if succesful, get a Case.'''
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply(dft.geos_standard, model='fixtures.fixture_model_func')
        nt.assert_is_instance(case, la.distributions.Case)

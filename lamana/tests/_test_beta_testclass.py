#------------------------------------------------------------------------------
'''Confirm accurate execution of building cases.'''

import os
import copy

import itertools as it

import nose.tools as nt
import pandas as pd

import lamana as la
from lamana.input_ import BaseDefaults
from lamana.utils import tools as ut
from lamana.models import Wilson_LT as wlt                 # for post Laminate, i.e. Cases only

#------------------------------------------------------------------------------


class TestCaseComparisons():
    '''Check __eq__ and __ne__ of Case objects. BETA.'''

    # Instantiate cases for comparison
    # NOTE: Keep pertinent instantiations contained in a single scope
    # NOTE: Modifications - add instantiations, simply add self to variable calls.
    dft = wlt.Defaults()

    case1a = la.distributions.Case(dft.load_params, dft.mat_props)
    case1b = la.distributions.Case(dft.load_params, dft.mat_props)
    case1c = la.distributions.Case(dft.load_params, dft.mat_props)
    case1d = la.distributions.Case(dft.load_params, dft.mat_props)
    case1e = la.distributions.Case(dft.load_params, dft.mat_props)
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

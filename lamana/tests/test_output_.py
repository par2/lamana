#------------------------------------------------------------------------------
'''Confirm output of general models.'''

import nose.tools as nt

import lamana as la
from lamana.utils import tools as ut

# Setup -----------------------------------------------------------------------
load_params = {
    'R': 12e-3,                                            # specimen radius
    'a': 7.5e-3,                                           # support ring radius
    'r': 2e-4,                                             # radial distance from center loading
    'P_a': 1,                                              # applied load
    'p': 2,                                                # points/layer
}

# Quick Form: a dict of lists
mat_props = {
    'HA': [5.2e10, 0.25],
    'PSu': [2.7e9, 0.33],
}


# TESTS -----------------------------------------------------------------------
# These tests are primitive.  They check that plots are made without errors.
# Details of the plotting fidelity must be checked by other means.


def test_plot_nobreak():
    '''Check that basic plotting API works without errors.'''
    # Build dicts of loading parameters and and material properties
    # Select geometries
    single_geo = ['400-200-800']

    case = la.distributions.Case(load_params, mat_props)   # instantiate a User Input Case Object through distributions
    case.apply(single_geo)
    ##actual = case.plot
    ##actual = case.plot()
    # plt.close()                                          # hangs

    # TODO: need to add kw in distrplot to turn off plot window
    # Shut down plt.show()

    #nt.assertTrue(isinstance(actual, mpl.axes))
    pass


# Could cover tests for _distribplot, _multiplot and _cycle_depth
def test_distribplot():
    '''Check this private function makes an axes of single geometry.'''
    case = la.distributions.Case(load_params, mat_props)   # instantiate a User Input Case Object through distributions
    case.apply(['400-200-800'])
    #actual = la.output_._distribplot(case.LMs)
    # TODO: now how to check for plot?
    # Can't suppress pyplot window
    pass


def test_multiplot():
    '''Check this private function makes an axes of multiple geometries.'''
    const_total = ['350-400-500', '400-200-800']
    cases = la.distributions.Cases(
        const_total, load_params=load_params, mat_props=mat_props,
        model='Wilson_LT', ps=[2, 3]
    )
    #actual = la.output_._multiplot(cases)
    # TODO: now how to check for plot?
    # Can't suppress pyplot window
    pass

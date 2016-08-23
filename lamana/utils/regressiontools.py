#------------------------------------------------------------------------------
'''Handy tools for monitoring regression.

Unlike utils.tools, core modules are imported here.  This module in not imported
by core modules.  In short, this module has tools to verify source using source.
Some tools include:

- comparing tested resulted to source output
- validating string parsing results

'''

from lamana import input_
from lamana.utils import tools as ut


def compare_to_source(source, test, mthdname, Geo_keys=None,
                      ps=list(range(1, 11)), ignore=None, verbose=False):
    '''Print OK if test and source DataFrames are equal for all ps.'''

    def validate_edge_cases(source_cls, test_cls, methodname, p=5,
                            Geo_keys=None, ignore=None, verbose=False):
        '''Return a bool for comparaing DataFrames from a custom test class and source.

        Simulates `laminator` tests for even, odd, mono-, bi and trilayer per p.
        Pass in keys of the Geo_objects dict to select desired Geometries to test.

        Parameters
        ----------
        source_cls : class
            Usually a class object from source code to compare results against.
        test_cls : class
            Beta object (in notebook) to compare sources results.
        methodname : str
            Name of the method called from the test class that returns a DataFrame.
         p : int
            Default number of DataFrame rows.
        Geo_keys : list of str, deault None
            Keys to select from the Geo_objects dictionary.
        ignore : list of str, default None
            Column names to ignore in the source DataFrame.
        verbose: bool, default False
            Toggle verbose mode.

        See Also
        --------
        - la.input_.BaseDefaults.Geo_objects: dict of common Geometry objects
        - BRCH: Performance.ipynb: beta code

        Notes
        -----
        When first building a program, tests usually involve comparing your "actual"
        modified code against "expected" results.  In this case, the actual result
        comes from a test/refactored class from beta in notebooks, and the expected
        result comes from source, known to work.

        Unlike `laminator`, this test obviates building `Case` objects from source
        by default.  Rather a custom test class must be provided to compare directly
        against a class from source code.

        In addition, this function intends to test edge cases, not the full sweet
        for `Geo_objects` prior to implementation.

        Examples
        --------
        >>> # Given a refactored class for comparing LFrames
        >>> ...
        >>> validate_edge_cases(
        ...    la.constructs.Laminate, TestBuild, '_build_LFrame',
        ...    ps=list(range(1, 6)), Geo_keys=['all'], ignore=['z(m)*']
        ... )
        # Pass
        >>> validate_edge_cases(TestLaminate, la.constructs.Laminate, '_build_LFrame')
        Inside the test block ...
        # Caught error and print DataFrame output


        '''
        bdft = input_.BaseDefaults()
        # dft = wlt.Defaults()                               # prevent circular import

        Geos = []
        for key in Geo_keys:
            Geos.extend(bdft.Geo_objects[key])
            # Geos.extend(dft.Geo_objects[key])

        for Geo in Geos:
            FeatureInput = {
                'Geometry': Geo,
                'Materials': ['HA', 'PSu'],
                'Model': 'Wilson_LT',
                'Parameters': {'P_a': 1, 'R': 0.012, 'a': 0.0075, 'p': 5, 'r': 0.0002},
                'Properties': {'Modulus': {'HA': 52000000000.0, 'PSu': 2700000000.0},
                'Poissons': {'HA': 0.25, 'PSu': 0.33}}
            }
            FeatureInput['Parameters']['p'] = p
            if verbose: print('  Laminate {}, p: {}'. format(Geo, p))

            # Compared classes
            L_like = source_cls(FeatureInput)
            default_df = L_like.frame
            if ignore:
                default_df = default_df.drop(ignore, axis=1)

            tc = test_cls(FeatureInput)
            #test_df = tc._build_LFrame()
            test_df = getattr(tc, methodname).__call__()

            try:
                ut.assertFrameEqual(default_df, test_df)
            # Capture the failed DataFrame output
            except(AssertionError) as e:
                print('Inside test block...')
                print(test_df)
                raise e

    # -------------------------------------------------------------------------
    if Geo_keys is None:
        Geo_keys = ['5-ply', '4-ply', '1-ply', '2-ply', '3-ply']
    for i, p in enumerate(ps):
        if verbose: print('Group: {}, p: {}'.format((i + 1), p))
        validate_edge_cases(source, test, mthdname, p, Geo_keys=Geo_keys,
                            ignore=ignore, verbose=verbose)
    print("Comparsions completed for {} Geo objects, ps: {}".format(Geo_keys, ps))
    print('OK')
    return None





## =============================================================================
# CITED CODE ------------------------------------------------------------------
# =============================================================================
# Code is modified from existing examples and cited in reference.py

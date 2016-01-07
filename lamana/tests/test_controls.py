#------------------------------------------------------------------------------
# Tests for DataFrame various cases.  Uses external csv control files

import os

import numpy as np
##import pandas as pd
##import nose.tools as nt

import lamana as la
import lamana.utils.tools as ut
##from lamana import constructs as con
from lamana.models import Wilson_LT as wlt

dft = wlt.Defaults()


# SETUP -----------------------------------------------------------------------
def fix_discontinuities(laminate, inner_i):
    '''Replace t_ Nan values at discontinuities with adjacent value for inner_i.

    Accounts for the following found in controls directory:
    - missing t(um) and d(mm) columns
    - discontinuities in multi and special plies
    - and more ...

    '''
    df = laminate.copy()

    # Tensile side
    discTensidx = df.loc[
        (df['label'] == 'discont.') & (df['type'] == 'inner')
        & (df['side'] == 'Tens.'), 't(um)'
    ].index.tolist()
    # Compressive side
    discCompidx = df.loc[
        (df['label'] == 'discont.') & (df['type'] == 'inner')
        & (df['side'] == 'Comp.'), 't(um)'
    ].index.tolist()
    #print(discTensidx)
    #print(df)
    #print(inner_i)
    for i, inner in enumerate(inner_i):
        #print(i, inner, inner_i)
        df.loc[discTensidx[i], 't(um)'] = inner

    for i, inner_r in enumerate(reversed(inner_i)):
        #print(inner_r)
        df.loc[discCompidx[i], 't(um)'] = inner_r
    return df


def extract_dataframe(df):
    '''Parse corrected DataFrame from a csv file; legacy, automated or custom.'''
    df_expected = df.copy()

    # Mild cleanup
    if 'd(mm)' in df_expected.columns:
        df_expected['d(m)'] = df_expected['d(mm)'] / 1000.
        del df_expected['d(mm)']

    if 't(um)' not in df_expected.columns:                 # for custom controls from legacy scripts
        df_expected['t(um)'] = df_expected['h(m)'] / 1e-6
        # Assign Nan to layer thickness of the discontinuity row
        df_expected.loc[
            df_expected['label'] == 'discont.', 't(um)'
        ] = np.nan
        # Twice the h in the middle
        df_expected.loc[
            df_expected['type'] == 'middle', 't(um)'] = df_expected.loc[
            df_expected['type'] == 'middle', 'h(m)'
        ].multiply(2) / 1e-6

    # Parse data mainly for the Case
    nplies = len(df_expected['layer'].unique())
    p = df_expected.groupby('layer').size().iloc[0]
    t_total = df_expected.iloc[-1]['d(m)']                 # (in m)

    # Get a geometry string to feed the API
    if nplies < 5:
        geometry = ut.get_special_geometry(df_expected)
    elif nplies >= 5:
        geometry = ut.get_multi_geometry(df_expected)
    elif nplies < 1:
        raise Exception('Number of plies < 1.  No plies detected.')
    #print(geometry)

    # Plugin holes; overwrite placeholder Nans at discontinuities
    # Primarily for custom controls
    geo = geometry.split('-')
    #print(geo)
    outer = float(geo[0])
    if '[' in geo[1]:
        inners = geo[1][1:-1].split(',')
        '''Why is float needed here and not int?'''
        '''Getting 200L error for float.'''
        #print(inners)
        inner_i = [float(t) for t in inners]
    else:
        inner_i = float(geo[1])
    #print(inner_i)
    df_expected.loc[
        (df_expected['label'] == 'discont.') & (df_expected['type'] == 'outer'),
        't(um)'] = outer
    if ('discont.' in df_expected['label'].values) and ('inner' in df_expected['type'].values):
        df_expected = fix_discontinuities(df_expected, inner_i)

    return df_expected, geometry, nplies, p, t_total


# TESTS -----------------------------------------------------------------------
# Test Columns
def test_apply_LaminateModels_cols_dimensions1():
    '''Test actual against expected DataFrames in .cvs files found in
    tests/controls_LT; IDs and dimensional columns.

    '''
    # Prepare file path.
    # Depends which directory nosetests is rum
    #path = os.getcwd()                                     # use for the test in the correct path
    path = os.path.join(os.getcwd(), 'lamana', 'tests', 'controls_LT')   # for builds
    #path = path + r'\lamana\tests\controls_LT'             # for Main Script. Comment out in tests
    #path = path + r'\tests\controls_LT'                    # for test
    #path = os.path.join(os.getcwd(), 'tests', 'controls_LT')          # for test
    #path = path + r'\controls_LT'                          # for test

    # Read all files in the path (REF 013)
    for file in ut.read_csv_dir(path):
        #df_expected = file
        df = file
        #print(df_expected)

        df_expected, geometry, nplies, p, t_total = extract_dataframe(df)

        # Build actual Case using distributions API
        dft.load_params['p'] = p
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply([geometry])
        df = case.frames[0]

        # Compare the dimensional columns only
        '''Bypassing z(m), z(m)*, intf and k for now'''
        '''UPDATE: k add back in 0.4.4b'''
        ###
        cols = ['layer', 'side', 'type', 'matl',
        #        'label', 't(um)', 'h(m)', 'd(m)', 'intf', 'k', 'Z(m)', 'z(m)']
        #        'label', 't(um)', 'h(m)', 'd(m)', 'intf', 'k', 'Z(m)', ]
        #        'label', 't(um)', 'h(m)', 'd(m)', 'intf', 'Z(m)', ]      # removed; k redefined in 0.4.3c4d
        #        'label', 't(um)', 'h(m)', 'd(m)', 'intf']
        'label', 't(um)', 'h(m)', 'd(m)', 'intf', 'k']
        print('A .csv file is being processed with the following dimensional properties:')
        print(' Number of plies: {} \n p: {} \n total \
               t (m): {} \n geometry: {} \n'.format(nplies, p, t_total, geometry))

        actual = df[cols]
        expected = df_expected[cols]
        #print ('expected (file) \n', expected)
        #print('actual (API) \n', actual)
        #print(expected.dtypes)
        #print(actual.dtypes)
        print('\n')
        ut.assertFrameEqual(actual, expected)


def test_apply_LaminateModels_cols_models1():
    '''Test .cvs files found in tests/controls_LT with API DataFrames.
    Comparing models columns only.

    Due to a different algorithms for calculating internal values,
    rows yielding maximum and minimum stress are the most reliable comparisons.

    Tests for internal points can varying depending on choice of z(m).
    So they will be excluded from this test.
    '''
    '''Wait for skipcols kwarg in read_csv in pandas 0.17'''

    def remove_units(cols):
        '''Return a dict of stress column labels with units removed.'''
        #cols = cols.tolist()
        dict_ = {}
        for idx, colname in enumerate(cols):
            if 'stress' in colname:
                tokens = colname.split(' ')                # works even w/o units
                unitless_name = tokens[0]
                #print(name)
                dict_[colname] = unitless_name
        return dict_

    # Prepare file path.
    # Depends which directory nosetests is rum
    #path = os.getcwd()                                     # use for the test in the correct path
    path = os.path.join(os.getcwd(), 'lamana', 'tests', 'controls_LT') # for builds
    #path = path + r'\lamana\tests\controls_LT'             # for Main Script. Comment out in tests
    #path = path + r'\tests\controls_LT'                    # for test
    #path = os.path.join(os.getcwd(), 'tests', 'controls_LT')          # for test
    #path = path + r'\controls_LT'                          # for test

    # Read all files in the path (REF 013)
    for file in ut.read_csv_dir(path):
        #df_expected = file
        df = file
        #print(df_expected)

        df_expected, geometry, nplies, p, t_total = extract_dataframe(df)

        # Build actual Case using distributions API
        dft.load_params['p'] = p
        case = la.distributions.Case(dft.load_params, dft.mat_props)
        case.apply([geometry])
        df = case.frames[0]

        # Compare only model-related columns; skip API columns
        IDs = ['layer', 'side', 'type', 'matl', 't(um)']   # except label_
        Dimensionals = ['h(m)', 'd(m)', 'intf', 'k', 'Z(m)', 'z(m)', 'z(m)*']
        #bypassed = ['z(m)', 'z(m)*', 'intf', 'k']
        skippedcols = IDs + Dimensionals
        actual_remainingcols = df.columns.difference(skippedcols)
        expected_remainingcols = df_expected.columns.difference(skippedcols)

        # Get model columns only and strip units from stress columns
        df_models = df[actual_remainingcols].copy()
        df_expected = df_expected[expected_remainingcols].copy()
        df_models.rename(columns=remove_units(actual_remainingcols), inplace=True)
        df_expected.rename(columns=remove_units(expected_remainingcols), inplace=True)
        #print(df_expected)

        print('A .csv file is being processed with the following dimensional properties:')
        print(' Number of plies: {} \n p: {} \n total \
               t (m): {} \n geometry: {} \n'.format(nplies, p, t_total, geometry))

        # Use all rows (including internals, optional)
        #actual = df_models
        #expected = df_expected[expected_remainingcols]

        # Only use max stress rows (interfacial)
        actual1 = df_models.loc[df_models['label'] == 'interface']
        expected1 = df_expected.loc[df_expected['label'] == 'interface']
        #expected1 = df_expected[expected_remainingcols].loc[df_expected['label'] == 'interface']

        # Only use min stress rows (discontunities)
        if p > 1:
            actual2 = df_models.loc[df_models['label'] == 'discont.']
            expected2 = df_expected.loc[df_expected['label'] == 'discont.']
            #expected2 = df_expected[expected_remainingcols].loc[df_expected['label'] == 'discont.']

        #print ('expected (file) \n', expected1)
        #print('actual (API) \n', actual1)
        #print ('expected (file) \n', expected2)
        #print('actual (API) \n', actual2)
        #print(type(expected1))
        #print(type(actual1))
        #print(expected1.dtypes)
        #print(actual1.dtypes)
        print('\n')
        ut.assertFrameEqual(actual1, expected1, check_dtype=False)  # max stress rows
        if p > 1:                                                   # min stress rows
            ut.assertFrameEqual(actual2, expected2, check_dtype=False)

        # Internal rows depend on the `z_` algorithm.  They are not compared to prevent breakage.

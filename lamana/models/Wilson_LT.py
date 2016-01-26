#------------------------------------------------------------------------------
'''A sample class-style, custom model using a modified laminate theory.'''
# Users can define classes for custom laminate theory models.
# Additionally, users can define custom defaults.

import math
import collections as ct

import pandas as pd

from lamana.input_ import BaseDefaults
from lamana.theories import BaseModel
from lamana.lt_exceptions import IndeterminateError


class Model(BaseModel):
    '''A modified laminate theory for circular biaxial flexure disks,
    loaded with a flat piston punch on 3-ball support having two distinct
    materials (polymer and ceramic).'''

    '''Accept extra args and kwds here'''
    def __init__(self):
        self.Laminate = None
        self.FeatureInput = None
        self.LaminateModel = None

    # TODO: eventually abstract into BaseModel and deprecate direct coding
    def _use_model_(self, Laminate, adjusted_z=False):
        '''Return updated DataFrame and FeatureInput Return None if exceptions raised.

        Parameters
        ----------
        df : DataFrame
            LaminateModel with IDs and Dimensional Variables.
        FeatureInut : dict
            Geometry, laminate parameters and more.  Updates Globals dict for
            parameters in the dashboard output.
        adjusted_z: bool; default=False
            If True, uses z(m)* values instead; different assumption for internal calc.

        Raises
        ------
        ZeroDivisionError
            If zero `r` or `a` in the log term are zero.
        ValueError
            If negative numbers are in the log term or the support radius exceeds
            the sample radius.

        Returns
        -------
        tuple
            The updated calculations and parameters stored in a tuple
            `(LaminateModel, FeatureInput)``.

        '''
        self.Laminate = Laminate
        df = Laminate.LFrame.copy()
        FeatureInput = Laminate.FeatureInput

        # Author-defined Exception Handling
        if (FeatureInput['Parameters']['r'] == 0):
            raise ZeroDivisionError('r=0 is invalid for the log term in the moment eqn.')
        elif (FeatureInput['Parameters']['a'] == 0):
            raise ZeroDivisionError('a=0 is invalid for the log term in the moment eqn.')
        elif (FeatureInput['Parameters']['r'] < 0) | (FeatureInput['Parameters']['a'] < 0):
            raise ValueError('Negative numbers are invalid for the log term '
                             'in moment eqn.')
        elif FeatureInput['Parameters']['a'] > FeatureInput['Parameters']['R']:
            raise ValueError('Support radius is larger than sample radius.')
        elif df['side'].str.contains('INDET').any():
            print('INDET value found.  Rolling back...')
            raise IndeterminateError('INDET value found. Unable to accurately calculate stress.')
            #raise AssertionError('Indeterminate value found.  Unable to accurately calculate stress.')

        # Calling functions to calculate Qs and Ds
        df.loc[:, 'Q_11'] = self.calc_stiffness(df, FeatureInput['Properties']).q_11
        df.loc[:, 'Q_12'] = self.calc_stiffness(df, FeatureInput['Properties']).q_12
        df.loc[:, 'D_11'] = self.calc_bending(df, adj_z=adjusted_z).d_11
        df.loc[:, 'D_12'] = self.calc_bending(df, adj_z=adjusted_z).d_12

        # Global Variable Update
        if (FeatureInput['Parameters']['p'] == 1) & (Laminate.nplies%2 == 0):
            D_11T = sum(df['D_11'])
            D_12T = sum(df['D_12'])
        else:
            D_11T = sum(df.loc[df['label'] == 'interface', 'D_11']) # total D11
            D_12T = sum(df.loc[df['label'] == 'interface', 'D_12'])
        #print(FeatureInput['Geometric']['p'])

        D_11p = (1./((D_11T**2 - D_12T**2)) * D_11T)         #
        D_12n = -(1./((D_11T**2 - D_12T**2))  *D_12T)        #
        v_eq = D_12T/D_11T                                   # equiv. Poisson's ratio
        M_r = self.calc_moment(df, FeatureInput['Parameters'], v_eq).m_r
        M_t = self.calc_moment(df, FeatureInput['Parameters'], v_eq).m_t
        K_r = (D_11p*M_r) + (D_12n*M_t)                    # curvatures
        K_t = (D_12n*M_r) + (D_11p*M_t)

        # Update FeatureInput
        global_params = {
            'D_11T': D_11T,
            'D_12T': D_12T,
            'D_11p': D_11p,
            'D_12n': D_12n,
            'v_eq ': v_eq,
            'M_r': M_r,
            'M_t': M_t,
            'K_r': K_r,
            'K_t:': K_t,
        }

        FeatureInput['Globals'] = global_params
        self.FeatureInput = FeatureInput                   # update with Globals
        #print(FeatureInput)

        # Calculate Strains and Stresses and Update DataFrame
        df.loc[:,'strain_r'] = K_r * df.loc[:, 'Z(m)']
        df.loc[:,'strain_t'] = K_t * df.loc[:, 'Z(m)']
        df.loc[:, 'stress_r (Pa/N)'] = (df.loc[:, 'strain_r'] * df.loc[:, 'Q_11']
                                ) + (df.loc[:, 'strain_t'] * df.loc[:, 'Q_12'])
        df.loc[:,'stress_t (Pa/N)'] = (df.loc[:, 'strain_t'] * df.loc[:, 'Q_11']
                             ) + (df.loc[:, 'strain_r'] * df.loc[:, 'Q_12'])
        df.loc[:,'stress_f (MPa/N)'] = df.loc[:, 'stress_t (Pa/N)']/1e6

        del df['Modulus']
        del df['Poissons']

        self.LaminateModel = df

        return (df, FeatureInput)

    #------------------------------------------------------------------------------
    '''Prefer staticmethods here.  Add formulas to doc strings.'''
    def calc_stiffness(self, df, mat_props):
        '''Return tuple of Series of (Q11, Q12) floats per lamina.'''
        # Iterate to Apply Modulus and Poisson's to correct Material
        '''Prefer cleaner ways to parse materials from mat_props'''
        df_mat_props = pd.DataFrame(mat_props)             # df easier to munge
        df_mat_props.index.name = 'materials'
        for material in df_mat_props.index:
        #for material in mat_props.index:
            mat_idx = df['matl'] == material
            df.loc[mat_idx, 'Modulus'] = df_mat_props.loc[material, 'Modulus']
            df.loc[mat_idx, 'Poissons'] = df_mat_props.loc[material, 'Poissons']
            E = df['Modulus']                              # series of moduli
            v = df['Poissons']
        stiffness = ct.namedtuple('stiffness', ['q_11', 'q_12'])
        q_11 = E/(1-(v**2))
        q_12 = (v*E)/(1-(v**2))
        return stiffness(q_11, q_12)

    def calc_bending(self, df, adj_z=False):
        '''Return tuple of Series of (D11, D12) floats.'''
        q_11 = df['Q_11']
        q_12 = df['Q_12']
        h = df['h(m)']
        if not adj_z:
            z = df['z(m)']
        else:
            z = df['z(m)*']
        bending = ct.namedtuple('bending', ['d_11', 'd_12'])
        d_11 = ((q_11*(h**3))/12.) + (q_11*h*(z**2))
        d_12 = ((q_12*(h**3))/12.) + (q_12*h*(z**2))
        return bending(d_11, d_12)

    def calc_moment(self, df, load_params, v_eq):
        '''Return tuple of moments (radial and tangential); floats.
        See Timishenko-Woinowsky: Eq. 91; default'''
        P_a = load_params['P_a']
        a = load_params['a']
        r = load_params['r']
        moments = ct.namedtuple('moments', ['m_r', 'm_t'])
        m_r = ((P_a/(4*math.pi)) * ((1+v_eq)*math.log10(a/r)))
        m_t = ((P_a/(4*math.pi)) * (((1+v_eq)*math.log10(a/r))+(1-v_eq)))
        return moments(m_r, m_t)


class Defaults(BaseDefaults):
    '''Return parameters for building distributions cases.  Useful for consistent
    testing.

    Dimensional defaults are inherited from utils.BaseDefaults().
    Material-specific parameters are defined here by he user.

    - Default geometric parameters
    - Default material properties
    - Default FeatureInput

    Examples
    --------
    >>> dft = Defaults()
    >>> dft.load_params
    {'R' : 12e-3, 'a' : 7.5e-3, 'p' : 1, 'P_a' : 1, 'r' : 2e-4,}

    >>> dft.mat_props
    {'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
    'Poissons': {'HA': 0.25, 'PSu': 0.33}}

    >>> dft.FeatureInput
     {'Geometry' : '400-[200]-800',
      'Geometric' : {'R' : 12e-3, 'a' : 7.5e-3, 'p' : 1, 'P_a' : 1, 'r' : 2e-4,},
      'Materials' : {'HA' : [5.2e10, 0.25], 'PSu' : [2.7e9, 0.33],},
      'Custom' : None,
      'Model' : Wilson_LT}

    Returns
    -------
    class
        Updated attributes inherited from  the `BaseDefaults` class.

    '''
    def __init__(self):
        BaseDefaults.__init__(self)
        '''DEV: Add defaults first.  Then adjust attributes.'''
        # DEFAULTS ------------------------------------------------------------
        # Build dicts of geometric and material parameters
        self.load_params = {
            'R': 12e-3,                                    # specimen radius
            'a': 7.5e-3,                                   # support ring radius
            'p': 5,                                        # points/layer
            'P_a': 1,                                      # applied load
            'r': 2e-4,                                     # radial distance from center loading
        }

        self.mat_props = {
            'Modulus': {'HA': 5.2e10, 'PSu': 2.7e9},
            'Poissons': {'HA': 0.25, 'PSu': 0.33}
        }

        # ATTRIBUTES ----------------------------------------------------------
        # FeatureInput
        self.FeatureInput = self.get_FeatureInput(
            self.Geo_objects['standard'][0],
            load_params=self.load_params,
            mat_props=self.mat_props,
            ##custom_matls=None,
            model='Wilson_LT',
            global_vars=None
        )

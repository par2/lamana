#------------------------------------------------------------------------------
# Class-style model

import math
import collections as ct

##import pandas as pd

from lamana.theories import BaseModel


class WilsonLT(BaseModel):
    '''A custom CLT model.

    A modified laminate theory for circular biaxial flexure disks,
    loaded with a flat piston punch on 3-ball support having two distinct
    materials (polymer and ceramic).

    '''
    def __init__(self):
        self.Laminate = None
        self.FeatureInput = None
        self.LaminateModel = None

    def _use_model_(self, Laminate, adjusted_z=False):
        '''Return a tuple of an updated DataFrame and FeatureInput.

        1. Add LT calculations as new columns to the Laminate DataFrame.
        2. Add ubiquitous variables to a Global key in the FeatureInput.

        Parameters
        ----------
        Laminate : Laminate object
            The Laminate object prior to applying model calculations.  The
            DataFrame has geometric calculations only (LFrame).  Laminate
            attributes are available.
        adjusted_z: bool; default False, optional
            If True, use z(m)* values instead; different assumption for internal calc.

        Returns
        -------
        tuple
            The updated calculations and parameters stored in a tuple
            `(LaminateModel, FeatureInput)``.

            df : DataFrame
                LaminateModel with IDs and Dimensional Variables.
            FeatureInut : dict
                Geometry, laminate parameters and more.  Updates Globals dict for
                parameters in the dashboard output.

        '''
        self.Laminate = Laminate
        df = Laminate.LFrame.copy()
        FeatureInput = Laminate.FeatureInput

        # Author-defined Exception Handling
        if (FeatureInput['Parameters']['r'] == 0):
            raise ZeroDivisionError('r=0 is invalid for the log term in the moment eqn.')
        elif (FeatureInput['Parameters']['a'] == 0):
            raise ZeroDivisionError('a=0 is invalid for the log term in the moment eqn.')

        # Calling functions to calculate Qs and Ds
        df.loc[:,'Q_11'] = self.calc_stiffness(df, FeatureInput['Materials']).q_11
        df.loc[:,'Q_12'] = self.calc_stiffness(df, FeatureInput['Materials']).q_12
        df.loc[:,'D_11'] = self.calc_bending(df, adj_z=adjusted_z).d_11
        df.loc[:,'D_12'] = self.calc_bending(df, adj_z=adjusted_z).d_12

        # Global Variable Update
        if FeatureInput['Geometric']['p'] == 1:
            D_11T = sum(df['D_11'])
            D_12T = sum(df['D_12'])
        else:
            D_11T = sum(df.loc[df['label'] == 'interface', 'D_11'])   # total D11
            D_12T = sum(df.loc[df['label'] == 'interface', 'D_12'])
        #print(FeatureInput['Geometric']['p'])

        D_11p = (1. / ((D_11T**2 - D_12T**2)) * D_11T)
        D_12n = -(1. / ((D_11T**2 - D_12T**2)) * D_12T)
        v_eq = D_12T / D_11T                                         # equiv. poisson's ratio
        M_r = self.calc_moment(df, FeatureInput['Geometric'], v_eq).m_r
        M_t = self.calc_moment(df, FeatureInput['Geometric'], v_eq).m_t
        K_r = (D_11p * M_r) + (D_12n * M_t)                          # curvatures
        K_t = (D_12n * M_r) + (D_11p * M_t)

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
        self.FeatureInput = FeatureInput                          # update with Globals
        #print(FeatureInput)

        # Calculate Strains and Stresses then Update DataFrame
        df.loc[:, 'strain_r'] = K_r * df.loc[:, 'Z(m)']
        df.loc[:, 'strain_t'] = K_t * df.loc[:, 'Z(m)']
        df.loc[:, 'stress_r (Pa/N)'] = (
            df.loc[:, 'strain_r'] * df.loc[:, 'Q_11']) + (
            df.loc[:, 'strain_t'] * df.loc[:, 'Q_12']
        )
        df.loc[:, 'stress_t (Pa/N)'] = (
            df.loc[:, 'strain_t'] * df.loc[:, 'Q_11']) + (
            df.loc[:, 'strain_r'] * df.loc[:, 'Q_12']
        )
        df.loc[:, 'stress_f (MPa/N)'] = df.loc[:, 'stress_t (Pa/N)'] / 1e6

        del df['Modulus']
        del df['Poissons']
        self.LaminateModel = df

        return (df, FeatureInput)

    # LT Methods --------------------------------------------------------------
    def calc_stiffness(self, df, mat_params):
        '''Return tuple of Series of (Q11, Q12) floats per lamina.'''
        # Iterate to Apply Modulus and Poisson's to correct Material
        for material in mat_params.index:
            mat_idx = df['matl'] == material

            df.loc[mat_idx, 'Modulus'] = mat_params.loc[material, 'Modulus']
            df.loc[mat_idx, 'Poissons'] = mat_params.loc[material, 'Poissons']
            E = df['Modulus']                                      # series of moduli
            v = df['Poissons']
        stiffness = ct.namedtuple('stiffness', ['q_11', 'q_12'])
        q_11 = E / (1 - (v**2))
        q_12 = (v * E) / (1 - (v**2))
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
        d_11 = ((q_11 * (h**3)) / 12.) + (q_11*h * (z**2))
        d_12 = ((q_12 * (h**3)) / 12.) + (q_12*h * (z**2))
        return bending(d_11, d_12)

    def calc_moment(self, df, geo_params, v_eq):
        '''Return tuple of moments (radial and tangential); floats.
        See Timishenko-Woinowsky: Eq. 91; default'''
        P_a = geo_params['P_a']
        a = geo_params['a']
        r = geo_params['r']
        moments = ct.namedtuple('moments', ['m_r', 'm_t'])
        m_r = ((P_a / (4*math.pi)) * ((1 + v_eq)*math.log10(a/r)))
        m_t = ((P_a / (4*math.pi)) * (((1 + v_eq)*math.log10(a/r)) + (1 - v_eq)))
        return moments(m_r, m_t)

# -----------------------------------------------------------------------------
'''A module that builds core objects, such as stacks and laminates.'''
# Stack() : an dict of the order laminate layers.
# Laminate() : pandas objects including laminate dimensions and calculations


import traceback
import itertools as it
import collections as ct

import pandas as pd
import numpy as np

from lamana import theories
from lamana.utils import tools as ut
from lamana.lt_exceptions import IndeterminateError

# =============================================================================
# STACK -----------------------------------------------------------------------
# =============================================================================
# Classes related to stack creation, layer ordering.  Precursor to Snapshot.


class Stack(object):
    '''Build a StackTuple object containing stack-related methods.

    We need to go from a 3 item Geometry object to n-sized stack of labeled
    layers.  Two operations are performed:

    1. Decode the Geometry object into a list of lamina thicknesses and
       types "unfolded" (or mirrored) across the physical neutral axis.
    2. Identify the unfolded geometry to build a StackTuple - a namedtuple
       containing a dict of the stacking order, the number or plies, the
       official stack name and alias.

    Parameters
    ----------
    FeatureInput : dict or Geometry object
        Use `Geometry` key to extract the `GeometryTuple` (converted geometry string)
        Can directly accept a Geometry object.

    Methods
    -------
    decode_geometry(Geometry)
        Yield a generator, iterating forward and backward over the Geometry object.
    identify_geometry(decoded)
        Return a namedtuple; lists are converted to dicts.
    add_materials(stack, materials)
        Return a dict; materials can be later added to a stack dict.
    stack_to_df(stack)
        Return a DataFrame, converting the stack.

    Returns
    -------
    namedtuple
        A StackTuple (dict, int, str, str); contains order, nplies, name, alias.

    See Also
    --------
    collections.namedtuple : special tuple in the Python Standard Library.

    '''
    def __init__(self, FeatureInput):
        try:
            # If passed 'Geometry' is actually a dict (FeatureInput)
            self.Geometry = FeatureInput['Geometry']
        except(TypeError):
            '''TEST geometry object'''
            self.Geometry = FeatureInput                   # if a Geometry object
        decoded = self.decode_geometry(self.Geometry)
        self.unfolded = list(decoded)                      # used in tests
        '''Recalled because generator exhausts decoded.  Improve.'''
        decoded = self.decode_geometry(self.Geometry)
        self.StackTuple = self.identify_geometry(decoded)  # namedtuple of (stack, nplies, name, alias)

    def decode_geometry(self, Geometry):
        '''Return a generator that decodes the Geometry object.

        Interprets the stacking order and yields a tuple of the lamina type
        (ltype) and thickness.

        A `Geometry` object has a .geometry attribute returning a namedtuple of
        laminae thicknesses labeled:

        - ['outer', 'inner', 'middle', 'symmetric']        # symmetry convention
        - ['outer', 'inner', 'middle']                     # general conventions

        This function makes a generator that checks for symmetry, then iterates
        forward and backward over the Geometry tuple ("unfolding" the tuple).
        If the Symmetric Convention is detected, the tuples are converted
        to General Convention by popping the 'symmetric' list element.

        Performance profiling:

        >>> %timeit decode_geometry(G)                        (with lists) : 10.3 us
        >>> %timeit decode_geometry(G)                        (with generators): 529 ns
        >>> %timeit decode_geometry(G)                        (with generators; 2nd refactor): 1.4 us
        >>> %timeit [layer_ for layer_ in decode_geometry(G)] (generators to lists): 57.1 us
        >>> %timeit [layer_ for layer_ in decode_geometry(G)] (generators to lists; 2nd refactor): 107 us

        Examples
        --------
        >>> G = la.input_.Geometry('400-[200]-800')
        >>> G
        Geometry object('400-[200]-800')

        >>> decoded = decode_geometry(G)
        >>> decoded
        <generator object>

        >>> [tupled for tupled in decode_geometry(G)]
        [('outer', 400.0),
         ('inner', 200.0),
         ('middle', 800.0),
         ('inner', 200.0),
         ('outer', 400.0)]

        '''
        def get_decoded():                                 # procedure
            '''Iterate forward and backward for each type of layer.'''
            # Forward: outer, inner_i, middle ...
            for ltype, thickness in listify_layer(Geometry):
                #yield from process_layer(ltype, thickness)
                '''DEV: Converted for Python 2.7; see latter for Py 3.x'''
                for layer_ in process_layer(ltype, thickness):
                    yield layer_

            # Reverse: ... inner_i, outer
            for ltype, thickness in reversed(listify_layer(Geometry)[:-1]):
                #yield from process_layer(ltype, thickness, reverse=True)
                # NOTE: DEV: Converted for Python 2.7; see latter for Py 3.x
                for layer_ in process_layer(ltype, thickness, reverse=True):
                    yield layer_

        def listify_layer(Geometry):                       # pure function 1
            '''Return a converted Geometry namedtuple to a list of tuples; pops symmetric entry'''
            layers = list(Geometry.geometry._asdict().items())
            if Geometry.is_symmetric:                      # clean up last element; see namedtuple of symmetric Geometry
                layers.pop()
                '''Add to verbose mode.'''
                #print('Symmetry detected in Geometry object.  Conforming to General Convention...')
            return layers

        def process_layer(ltype, thickness, reverse=False):        # pure function 2
            '''Return items from inner_i thickness list and "unfold" Geometry stack.
            Reverse inner_i list if set True.'''
            if isinstance(thickness, list) & (reverse is False):     # parse inner_i list for forward iteration
                for inner in thickness:
                    yield (ltype, inner)
            elif isinstance(thickness, list) & (reverse is True):    # reverse inner_i list for reverse iteration
                for inner in reversed(thickness):
                    yield (ltype, inner)
            elif ltype == 'middle' and Geometry.is_symmetric:
                yield (ltype, thickness * 2)
            else:
                yield (ltype, thickness)

        return get_decoded()

    def identify_geometry(self, decoded):
        '''Return a namedtuple containing preliminary stack information.

        This function iterates a generator of decoded geometry information.
        Specifically, this information is the lamina type (ltype) and thickness.
        A stack is built from this info by exclusion principle: only include
        non-zero thick laminae to the stack.  The number of plies (nplies),
        name and alias (if special) are then determined.

        Parameters
        ----------
        decoded : generator of tuples
            Decoded Geometry object, containing tuples of thickness & `layer_` type.
            Stacking order is preserved; result of `Stack.decode_geometry()`.

        Returns
        -------
        namedtuple
            A StackTuple (dict, int, str, str):
            - order: (dict) of the `layer_` number as keys and decoded geometry values
            - nplies: (int) number of plies
            - name: (str) name of laminate
            - alias: (str) common name

        Notes
        -----
        Performance profiling:

        >>> geo_input = '400-200-800
        >>> G = la.input_.Geometry(geo_input)
        >>> decoded = decode_geometry(G)
        >>> %timeit identify_geometry(decoded)                (with lists): 950 us
        >>> %timeit identify_geometry(decoded)                (with generators): 935 us  ?

        Examples
        --------
        >>> geo_input = ('400-[200]-800')
        >>> G = la.input_.Geometry(geo_input)
        >>> identify_geometry(decode_geometry(G))
        StackTuple(order=defaultdict(<class 'list'>,
        {1: ['outer', 400.0], 2: ['inner', 200.0],
         3: ['middle', 800.0], 4: ['inner', 200.0],
         5: ['outer', 400.0]}),
         nplies=5, name='5-ply', alias='Standard')

        '''
        # Dict of Aliases for Special Geometries
        alias_dict = {
            1: 'Monolith',
            2: 'Bilayer',
            3: 'Trilayer',
            4: 'Quadlayer',
            5: 'Standard',
        }

        StackTuple = ct.namedtuple('StackTuple', ['order', 'nplies', 'name', 'alias'])
        order = ct.defaultdict(list)                       # subs empty {}

        '''Is there a way to replace this nested counter with something pythonic?'''
        layer_ = 0                                         # nested counter
        for (ltype, thickness) in decoded:
            #print(ltype, thickness)
            # Exclude Zero layers from the Stack
            if thickness != 0.0:
                layer_ += 1                                # updates only for non-zero thickness laminae
                order[layer_].append(ltype)                # adds tuple elements into the defaultdicts list
                order[layer_].append(thickness)            # ...
        nplies = layer_                                    # updates, but last layer_ is retained in nplies
        name = '{0}{1}'.format(nplies, '-ply')
        if nplies in alias_dict.keys():
            alias = alias_dict[nplies]
        else:
            alias = None
        return StackTuple(order, nplies, name, alias)

    @classmethod
    def add_materials(cls, stack, materials):
        '''Return a defaultdict of the stack with extended material values.

        Uses a cycler which alternates while iterating the materials list,
        keeping count.  Once the counter reaches the number of plies,
        the loop breaks.

        Parameters
        ----------
        stack : dict
            Layer numbers as keys and layer type/thickness as values.
            Material are appended to list values.
        materials : list
            User input materials either parsed by default in distributions
            module or overridden by the user.

        Examples
        --------
        >>> import lamana as la
        >>> from lamana.models import Wilson_LT as wlt
        >>> dft = wlt.Defaults()

        >>> # Get a stack dict
        >>> stack_object = la.constructs.Stack(dft.FeatureInput)
        >>> stack_dict = stack_object.StackTuple.order
        >>> stack_dict
        defaultdict(<class 'list'>,
        {1: ['outer', 400.0], 2: ['inner', 200.0],
         3: ['middle', 800.0], 4: ['inner', 200.0],
         5: ['outer', 400.0]})

        >>> # Extend the stack dict by adding materials to the list values
        >>> stack = la.constructs.Stack(dft.FeatureInput)
        >>> stack_extended = stack_object.add_materials(stack_dict, ['HA', 'PSu'])
        >>> stack_extended
        defaultdict(<class 'list'>,
        {1: ['outer', 400.0, 'HA'], 2: ['inner', 200.0, 'PSu'],
         3: ['middle', 800.0, 'HA'], 4: ['inner', 200.0, 'PSu'],
         5: ['outer', 400.0, 'HA']})

        '''
        '''Move this handling and df conversion/extraction to get_FeatureInput'''
        ##n_materials = len(materials)
        nplies = len(stack)
        #print('stack materials ', materials)

        # Cycler : alternate while iterating a list and add to a dict
        for ind, material in enumerate(it.cycle(materials), 1):
            #print('material index:', ind)
            #print('materials:', material)
            clean_values = []
            clean_values.extend(stack[ind])                # take extant stack
            clean_values.append(material)                  # add new value
            stack[ind] = clean_values

            if ind == nplies:
                '''Add to verbose mode.'''
                #print('Stack materials have been updated.')
                return stack

    @classmethod
    def stack_to_df(cls, stack):
        '''Return a DataFrame of converted stacks with materials (list of dicts).'''
        df = pd.DataFrame(stack).T
        df.reset_index(level=0, inplace=True)              # reset index; make new column
        df.columns = ['layer', 'type', 't(um)', 'matl']    # rename columns
        recolumned = ['layer', 'matl', 'type', 't(um)']
        df = ut.set_column_sequence(df, recolumned)        # uses ext. f(x)
        df[['t(um)']] = df[['t(um)']].astype(float)        # reset numeric dtypes
        return df

# =============================================================================
# LAMINATES -------------------------------------------------------------------
# =============================================================================
# Create LaminateModel objects


class Laminate(Stack):
    '''Create a `LaminateModel` object.  Stores several representations.

    Laminate first inherits from the `Stack` class.  A `FeatureInput` is passed in
    from a certain "Feature" module and exchanged between constructs and theories
    modules.

    Native objects:

    - `Snapshot` : stack of unique layers (1, 2, ..., n), single rows and ID columns.
    - `LFrame` : snapshot with multiple rows including Dimensional Data.
    - `LMFrame` : `LFrame` w/Dimensional and Data variables via `theories.Model` data.

    Finally this class build a `LamainateModel` object, which merges the LaminateModel
    date with the Model data defined by an author in a separate `models` module;
    models are related to classical laminate theory variables, i.e. `Q11`, `Q12`,
    `D11`, `D12`, ..., `stress`, `strain`, etc.

    The listed Parameters are "ID Variables".  The Other Parameters are "Dimensional
    Variables".  There are special variables related to columns in DataFrames,
    suffixed with trailing underscores.

    Parameters
    ----------
    layer_ : int
        Enumerates layers from bottom, tensile side up.
    side_ : str
        Side of the stress state; tensile (bottom) or compressive (top).
    type_ : str
        Type of layer; outer, inner or middle.
    matl_ : str
        Type of material.
    t_ : float
        Total thickness per layer.

    Other Parameters
    ----------------
    label_ : str
        Type of point; interfacial, internal or discontinuity.
    h_ : float
        Lamina thickness for all lamina except middle layers (half thickness).
    d_ : float
        Distance from the bottom layer; and shakes with calculations in
        `theories.Model` and used in testing. Units (m).
    intf_ : int
        Enumerates an interfaces from tensile side up.
    k_ : float
        Relative height; includes fractional height of kth layer.
    Z_ : float
        Distance from the neutral axis to an interface (or sub-interface p).
    z_ : float
        Distance from the neutral axis to the lamina midplane (or sub-midplane_p).

    Attributes
    ----------
    p
    total
    max_stress
    min_stress
    extrema
    summary
    is_special
    has_discont
    has_neutaxis
    FeatureInput : dict
        Passed-in, user-defined object from Case.
    Geometry : Geometry object
        Converted Geometry string.
    load_params : dict; default None
        A dict of common loading parameters, sample and support radii, etc.
    mat_props : dict; default None
        A dict of materials and properties, i.e. elastic modulus and Poisson's ratio.
    materials : DataFrame
        Converted mat_props to pandas object; used for quick display.
    parameters : Series
        Converted load_params to pandas object; used for quick display.
    model : str
        Specified custom, laminate theory model.
    {stack_order, nplies, name, alias} : list, str, str, str
        StackTuple attributes.
    {Snapshot, LFrame, LMFrame} : DataFrame
        Laminate object.
    {Middle, Inner_i, Outer} : DataFrame
        Isolated layer types
    {compressive, tensile} : DataFrame
        Isolated layer stress sides.

    Raises
    ------
    AttributeError
        If custom attributes could not be set to the `LaminateModel`.

    Examples
    --------
    >>> from lamana.models import Wilson_LT as wlt
    >>> import lamana as la
    >>> dft = wlt.Defaults()
    >>> FeatureInput = dft.FeatureInput
    >>> FeatureInput['Geometry'] = la.input_.Geometry('400-[200]-800')
    >>> la.constructs.Laminate(FeatureInput)
    <lamana LaminateModel object (400.0-[200.0]-800.0)>

    See Also
    --------
    theories.Model : handles user defined Laminate Theory models
    models : directory containing package models

    '''
    # TODO: pass kwargs in
    def __init__(self, FeatureInput):
        super(Laminate, self).__init__(FeatureInput)

        # Parse FeatureInput
        self.FeatureInput = FeatureInput.copy()            # for preserving FI in each Case

        self.Geometry = FeatureInput['Geometry']
        self.load_params = FeatureInput['Parameters']
        self.mat_props = FeatureInput['Properties']
        self.materials = FeatureInput['Materials']
        self.model = FeatureInput['Model']
        #print('constructs material attr:', self.materials)

        # Parse Stack Object
        st = Stack(FeatureInput)
        self.stack_order = st.StackTuple.order
        self.nplies = st.StackTuple.nplies
        self.name = st.StackTuple.name
        self.alias = st.StackTuple.alias                   # new in 0.4.3c5a

        # Laminate Objects
        self.Snapshot = []                                 # df object; stack
        self.LFrame = []                                   # df of IDs; formerly Laminate_
        #self.Model = theories.Model()                      # Model object
        ##self.Model = None
        self.LMFrame = []                                  # df object; modded stack

        self._type_cache = []
        ##self._dict_trim = {}                              # holder of pandas-less __dict__

        #-----------------------------------------------------------------------
        # LaminateModel Instance Updates                   # the heart of Laminate()
        self._build_snapshot()
        self._build_laminate()                             # Phase 1
        self._update_columns()                             # Phase 2 & 3

        # LaminateModel Attributes
        # Assumes DataFrames are safelt made by latter instance updates
        self.Middle = self.LMFrame[self.LMFrame['type'] == 'middle']
        self.Inner_i = self.LMFrame[self.LMFrame['type'] == 'inner']
        self.Outer = self.LMFrame[self.LMFrame['type'] == 'outer']
        self.compressive = self.LMFrame[self.LMFrame['side'] == 'Comp.']
        self.tensile = self.LMFrame[self.LMFrame['side'] == 'Tens.']

##        if type(self.LMFrame) != list:
##            self.Middle = self.LMFrame[self.LMFrame['type'] == 'middle']
##            self.Inner_i = self.LMFrame[self.LMFrame['type'] == 'inner']
##            self.Outer = self.LMFrame[self.LMFrame['type'] == 'outer']
##            self.compressive = self.LMFrame[self.LMFrame['side'] == 'Comp.']
##            self.tensile = self.LMFrame[self.LMFrame['side'] == 'Tens.']
##        else:
##            raise AttributeError("Unable to set attributes to LMFrame.")

    def __repr__(self):
        return '<lamana LaminateModel object ({}), p={}>'.format(self.Geometry.__str__(),
                                                                 self.p)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # Auto check attrs if assigned to DataFrames/Series, then add to list
            blacklisted = [attr for attr in self.__dict__ if
                isinstance(getattr(self, attr), (pd.DataFrame, pd.Series))]

            # Check DataFrames and Series
            for attrname in blacklisted:
                ndf_eq = ut.ndframe_equal(getattr(self, attrname),
                                          getattr(other, attrname))

            # Ignore pandas objects; check rest of __dict__ and build trimmed dicts
            # Important to blacklist the trimmed dict from looping in __dict__
            blacklisted.append('_dict_trim')          # prevent infinite loop
            self._dict_trim = {
                key: value
                for key, value in self.__dict__.items()
                if key not in blacklisted}
            other._dict_trim = {
                key: value
                for key, value in other.__dict__.items()
                if key not in blacklisted}
            return ndf_eq and self._dict_trim == other._dict_trim    # order is important
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        '''Allow set comparisons.

        The only required property is that objects which compare equal
        have the same hash value (REF 035).  self.__dict__ is unhashable
        due to the inner list.  So a copy is made called _geometry_hash
        of GeometryTuple with tupled inner instead.'''
        return hash((self.Geometry, self.p))

    def _build_snapshot(self):
        '''Build a quick, skeletal view of the stack (Snapshot).

        Assign materials and stress states to self.stack_order.
        '''
        stack_extended = Stack.add_materials(self.stack_order, self.materials)
        #print(stack_extended)
        self.Snapshot = Stack.stack_to_df(stack_extended)
        self.Snapshot = Laminate._set_stresses(self.Snapshot)

    # PHASE 1
    def _build_laminate(self):
        '''Build a primitive laminate from a stack.

        Build in three steps:

        1. Adopt the Snapshot and extend it with more rows.
        2. Define Lamina layers by types and multiple rows.
        3. Glue lamina together to make one DataFrame.

        '''
        df_snap = self.Snapshot.copy()
        p = self.FeatureInput['Parameters']['p']

        # Replicate Multiple Rows by p
        df = pd.concat([df_snap] * p)
        # `sort` is deprecated; works in pandas 0.16.2; last worked in lamana 0.4.9
        # replaced `sort` with `sort_index` for pandas 0.17.1; backwards compatible
        df.sort_index(axis=0, inplace=True)
        ##df.sort(axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = Laminate._set_stresses(df)
        #print(df)

        # Build Laminate with Classes
        layers = df.groupby('layer')
        self._type_cache = layers['type'].unique()
        self._type_cache.apply(str)                        # converts to str class, not str alone

        self.LFrame = df                                   # retains copy of partial Laminate (IDs & Dimensionals)

    def _update_columns(self):
        '''Update LFrame with columns of Dimensional and Data values.'''

        # PHASE 2
        def _update_dimensions(LFrame):
            '''Update Laminate DataFrame with new dimensional columns.

            This function takes a primitive LFrame (converted Stack) and adds
            columns: `label`, `h(m)`, `d(m)`, `intf`, `k`, `Z(m)`, `z(m)`, `z(m)*`

            A number of pandas-like implementations are performed to achieve this.
            So the coding has a different approach and feel.

            Parameters
            ----------
            LFrame : DataFrame
                A primitive Laminate DateFrame containing ID columns.

            '''
            # For Implementation
            nplies = self.nplies
            p = self.p
            t_total = self.total
            #print('nplies: {}, p: {}, t_total (m): {}'.format(nplies, p, t_total))

            df = LFrame.copy()

            # WRANGLINGS --------------------------------------------------------------
            # Indexers ----------------------------------------------------------------
            # Many dimensional values are determined by index positions.

            # Revised Indexer
            df['idx'] = df.index                                       # temp. index column for idxmin & idxmax
            interface_tens = df[df['side'] == 'Tens.'].groupby('layer')['idx'].idxmin()
            discontinuity_tens = df[(df['side'] == 'Tens.')
                & (df['type'] != 'middle')].groupby('layer')['idx'].idxmax()
            discontinuity_comp = df[(df['side'] == 'Comp.')
                & (df['type'] != 'middle')].groupby('layer')['idx'].idxmin()
            interface_comp = df[df['side'] == 'Comp.'].groupby('layer')['idx'].idxmax()
            interface_idx = pd.concat([interface_tens, interface_comp])
            discont_idx = pd.concat([discontinuity_tens, discontinuity_comp])
            #print(discontinuity_tens.values)
            if nplies > 1:
                pseudomid = [discontinuity_tens.values[-1],
                             discontinuity_comp.values[0]]               # get disconts indices near neutral axis; for even plies
            mid_idx = len(df.index) // 2
            #print('middle index: ', mid_idx)

            # Indexer dict of outside and inside Indices
            idxs = {
                'interfaces': interface_idx.values.tolist(),             # for interfaces
                'disconts': discont_idx.values.tolist(),                 # for disconts.
                'middle': mid_idx,                                       # for neut. axis
                'intfTens': interface_tens.values.tolist(),              # for side_ interfaces
                'intfComp': interface_comp.values.tolist(),
                'unboundIntfT': interface_tens.values.tolist()[1:],
                'unboundIntfC': interface_comp.values.tolist()[:-1],
                'disTens': discontinuity_tens.values.tolist(),           # for disconts
                'disComp': discontinuity_comp.values.tolist(),
            }

            # Masks -------------------------------------------------------------------
            # Interface Mask
            s = df['idx'].copy()
            s[:] = False                                                 # convert series to bool values
            s.loc[idxs['interfaces']] = True
            mask = s                                                     # boolean mask for interfaces

            # COLUMNS -----------------------------------------------------------------
            # label_ ------------------------------------------------------------------
            # Gives name for point types
            df['label'] = np.where(mask, 'interface', 'internal')        # yes!; applies values if interface, else internal
            if p != 1:
                df.loc[idxs['disconts'], 'label'] = 'discont.'           # yes!; post-fix for disconts.
            if (p % 2 != 0) & ('middle' in df['type'].values):
                df.loc[idxs['middle'], 'label'] = 'neut. axis'
            internal_idx = df[df['label'] == 'internal'].index.tolist()  # additional indexer
            # '''Add neut. axis in the middle'''

            # h_ ----------------------------------------------------------------------
            # Gives the thickness (in m) and height w.r.t to the neut. axis (for middle)
            df['h(m)'] = df['t(um)'] * 1e-6
            df.loc[df['type'] == 'middle', 'h(m)'] = df['t(um)'] * 1e-6 / 2.
            if p != 1:                                                   # at disconts.
                df.loc[idxs['disTens'], 'h(m)'] = df['h(m)'].shift(-1)
                df.loc[idxs['disComp'], 'h(m)'] = df['h(m)'].shift(1)

            # d_ ----------------------------------------------------------------------
            # Gives the height for interfaces, neutral axes, disconts and internal points
            # Assign Laminate Surfaces and Neutral Axis to odd p, odd nply laminates
            df.loc[0, 'd(m)'] = 0                                        # first
            df.loc[idxs['middle'], 'd(m)'] = t_total / 2.                # middle
            df.iloc[-1, df.columns.get_loc('d(m)')] = t_total            # last

            # Assign Interfaces
            # Uses cumsum() for selected interfaces thickness to get d
            innerhTens = df.loc[df['label'] == 'interface',
                'h(m)'].shift(1)[idxs['unboundIntfT']]                   # shift h down, select inner interfaces
            df.loc[idxs['unboundIntfT'], 'd(m)'] = 0 + np.cumsum(innerhTens)
            #print(np.cumsum(innerhTens))
            innerhComp = df.loc[df['label'] == 'interface',
                'h(m)'].shift(-1)[idxs['unboundIntfC']]                  # shift h up, select inner interfaces
            df.loc[idxs['unboundIntfC'],
                'd(m)'] = t_total - np.cumsum(innerhComp[::-1])[::-1]
            #print(t_total - np.cumsum(innerhComp[::-1])[::-1])          # inverted cumsum()

            # Assign Other Points
            if p > 1:                                                    # at disconts.
                df.loc[idxs['disTens'], 'd(m)'] = df['d(m)'].shift(-1)
                df.loc[idxs['disComp'], 'd(m)'] = df['d(m)'].shift(1)
            if p > 2:
                df = Laminate._make_internals(df, p, column='d(m)')      # at internals
                ##df = _make_internals(df, p, column='d(m)')               # at internals

            # intf_ -------------------------------------------------------------------
            # Enumerates proximal interfaces; n layer, but n+1 interfaces
            df['intf'] = df.loc[:, 'layer']
            df.loc[df['side'] == 'Comp.', 'intf'] += 1

            if (p % 2 != 0) & (nplies % 2 != 0):
                '''Need an INDET for numeric dtype.  Default to Nan for now'''
                ##df.loc[df['label'] == 'neut. axis', 'intf'] = 'INDET'
                df.loc[idxs['middle'], 'intf'] = np.nan                  # using indep. indexer vs. label_

            # Reset the dtype to float
            df[['intf']] = df[['intf']].astype(np.float64)

            # k_ ----------------------------------------------------------------------
            # Normally the layer number, but now tracks the ith fractional level per layer
            # See definition in (Staab 197), k is is the region between k and k-1 level
            # Like intf_, k_ is aware of neutral axis

            # k_ == intf_ (proximal interface)
            df.loc[df['label'] == 'interface',
                'k'] = df.loc[df['label'] == 'interface', 'intf']        # at interfaces
                ##'k'] = df.loc[df['label'] == 'interface', 'intf']-1      # at interfaces

#             if (p != 1) & (nplies%2 == 0):
#                 df.loc[pseudomid, 'k'] = (nplies/2.)+1                   # hack for even mids
#                 #df.loc[pseudomid, 'k'] = nplies/2.                       # replace middle values

            # Interfaces and discontinuities share the same k_
            if p > 1:                                                    # at disconts.
                df.loc[idxs['disTens'], 'k'] = df['k'].shift(-1)
                df.loc[idxs['disComp'], 'k'] = df['k'].shift(1)

                # Even plies have adjacent discontinuities at the neutral axis
                if nplies % 2 == 0:
                    df.loc[pseudomid, 'k'] = (nplies / 2.) + 1           # hack for even mids
                    ##df.loc[pseudomid, 'k'] = nplies / 2.                 # replace middle values

            # Auto calculate internal divisions
            if p > 2:                                                    # at internals
                df = Laminate._make_internals(df, p, column='k')
                ##df = _make_internals(df, p, column='k')
            '''Need an INDET. for numeric dtype.  Default to Nan for now'''
            #df.loc[df['label'] == 'neut. axis', 'k'] = 'INDET'
            #df.loc[df['label'] == 'neut. axis', 'k'] = np.nan

            # Odd plies have nuetral axes
            if (p % 2 != 0) & (nplies % 2 != 0):                         # using indep. indexer vs. label_
                df.loc[idxs['middle'], 'k'] = (df['k'].max() + df['k'].min()) / 2.
                ##df.loc[idxs['middle'], 'k'] = (df['k'].max()-df['k'].min())/2
                ##df.loc[idxs['middle'], 'k'] = np.nan                   # using indep. indexer vs. label_

            # Z_ ----------------------------------------------------------------------
            # Distance from ith level to the neutral access
            middle = t_total / 2.
            df['Z(m)'] = middle - df['d(m)']
            if (nplies == 1) & (p == 1):                                 # d_ = t_total here, so must amend
                df['Z(m)'] = t_total / 2.

            # z_ ----------------------------------------------------------------------
            # Distance from ith Z-midplane level to the neutral access
            # Two flavors are implemented for linearly and log-distributed z_ (z(m) and z(m)*)
            t_mid = df.loc[df['label'] == 'interface', 'h(m)'] / 2.       # for midplane calc.
            df.loc[(df['label'] == 'interface') & (df['side'] == 'Tens.'),
                'z(m)'] = df.loc[df['label'] == 'interface',
                'Z(m)'] - t_mid                                          # at interfaces
            df.loc[(df['label'] == 'interface') & (df['side'] == 'Comp.'),
                'z(m)'] = df.loc[df['label'] == 'interface',
                'Z(m)'] + t_mid                                          # at interfaces
            if nplies % 2 == 0:
                df.loc[pseudomid, 'z(m)'] = 0                            # replace middle values
            if p > 1:                                                    # at disconts.
                df.loc[idxs['disTens'], 'z(m)'] = df['z(m)'].shift(-1)
                df.loc[idxs['disComp'], 'z(m)'] = df['z(m)'].shift(1)
            if p > 2:
                # Equi-partitioned, Linear Intervals (legacy code); z(m)
                df = Laminate._make_internals(df, p, column='z(m)')
                ##df = _make_internals(df, p, column='z(m)')
            if p % 2 != 0:
                ##df.loc[df['label'] == 'neut. axis', 'z(m)'] = 0
                df.loc[idxs['middle'], 'z(m)'] = 0                       # using indep. indexer vs. label_

            ####
            # Non-equi-partitioned Intervals; "Travelling" Midplanes; z(m)*
            '''Possibly offer user options to use either method'''
            lastT = df[(df['side'] == 'Tens.') & (df['type'] != 'middle')].groupby('layer')['Z(m)'].last()
            lastC = df[(df['side'] == 'Comp.') & (df['type'] != 'middle')].groupby('layer')['Z(m)'].first()

            last = pd.concat([lastT, lastC])
            last.name = 'lasts'
            joined = df.join(last, on='layer')
            joined['z_intervals'] = (joined['Z(m)'] - joined['lasts']) / 2.
            #print(joined)
            #print(last)
            df['z(m)*'] = joined['Z(m)'] - joined['z_intervals']
            df.loc[df['type'] == 'middle', 'z(m)*'] = df['Z(m)'] / 2.
            if (p == 1) & (nplies == 1):
                df.loc[0, 'z(m)*'] = 0
            ####
            del df['idx']

            sort_columns = ['layer', 'side', 'type', 'matl', 'label', 't(um)',
                            'h(m)', 'd(m)', 'intf', 'k', 'Z(m)', 'z(m)', 'z(m)*']
            self.LFrame = ut.set_column_sequence(df, sort_columns)

        # PHASE 3
        '''Remove LFrame and FeatureInput'''
        def _update_calculations():
            '''Update `LaminateModel` DataFrame and `FeatureInput`.

            - populates stress data calculations from the selected model.
            - may add Globals dict to `FeatureInput`.

            Tries to update `LaminateModel`. If an exception is raised
            (on the model side), no update is made, and the Laminate
            (without Data columns) is set as the default `LFrame`.

            '''

            # TODO: Need to handle general INDET detection.  Roll-back to `LFrame` if detected.
            # TODO: No way to pass in kwargs to handshake;
            try:
                self.LMFrame, self.FeatureInput = theories.handshake(self,
                                                                     adjusted_z=False)

            except(IndeterminateError) as e:
                '''Improve selecting exact Exceptions.'''
                ##if err in (AttributeError, ValueError, ZeroDivisionError):
                print('The model raised an exception. LaminateModel not updated. LMFrame defaulting to LFrame.')
                print(traceback.format_exc())
                self.LMFrame = self.LFrame.copy()

        '''The args are a bit awkward; replace with empty or comment dependencies'''
        _update_dimensions(self.LFrame)
        _update_calculations()

    # Methods+ ----------------------------------------------------------------
    # These methods support Phase 1
    def _check_layer_order(self):
        '''Cross-check stacking order with layers of the snapshot object.
        Returns an abbreviated list of layer orders.

        Notes
        -----
        Since 0.4.3c4d, `_type_cache` type list is replaced with ndarray.

        Examples
        --------
        >>> case = la.distributions.Case(load_params, mat_props)
        >>> laminate = case.apply(('400-200-800'))
        >>> laminate._check_layer_order()
        ['O','I','M','I','O']

        '''
        stack_types = [row for row in self.Snapshot['type']]       # control
        #print(stack_types)
        abbrev = [letters[0][0].upper()                            # use if type_cache is ndarray
                  for letters in self._type_cache]                 # easier to see
        assert self._type_cache.tolist() == stack_types, \
            'Lamina mismatch with stack types, \
                  \n {} instead of \n {}'.format(self._type_cache, stack_types)
        return abbrev

    '''Find way replace staticmethods with class methods.'''
    @classmethod
    def _set_stresses(cls, df):                                       # == side_()
        '''Return updated DataFrame with stresses per side_ of neutral axis.'''
        #print('Assigning stress states to sides for a given stack.')
        cols = ['layer', 'side', 'matl', 'type', 't(um)']
        n_rows = len(df.index)
        half_the_stack = n_rows // 2
        #print(half_the_stack)
        n_middles = df['type'].str.contains(r'middle').sum()
        #print(n_middles)

        # Default
        df.loc[:, 'side'] = 'None'
        side_loc = df.columns.get_loc('side')
        # Middle for Snapshot
        if n_middles == 1:
            df.iloc[half_the_stack, side_loc] = 'INDET'
        # For the neutral axis
        elif n_rows % 2 != 0 and n_rows != 1:
            df.iloc[half_the_stack, side_loc] = 'None'             # for odd p
        # Other plies
        '''Replace with p'''
        if n_rows > 1:
            df.iloc[:half_the_stack, side_loc] = 'Tens.'           # applies to latest column 'side'
            df.iloc[-half_the_stack:, side_loc] = 'Comp.'

        df = ut.set_column_sequence(df, cols)
        return df

    @classmethod
    def _make_internals(cls, df_mod, p, column):
        '''Populate internals between a first and last index per group.
        This determines the interval. See df_mod for caution. Steps:

        - Make series comprising intervals for each group
        - Make a temp df joining intervals of d (d_intervals) to replicate values
        - Add the prior d_ row to the correl. interval for internal d_

        Parameters
        ----------
        df_mod : DataFrame
            Passed in modified DataFrame.  CAUTION: Assumes label_ column is
            present.  Also assumes interface and discont. rows are correctly
            populated.
        p : int
            Passed in self.p; number of data points.
        column: str
            Column to assign internals.

        Notes
        -----
        .. math::

            x_i = x_0 + sigma_{i=1}^p (delta * i)
            inv = (x_n - x_0)/(p-1)

        Raises
        ------
        ZeroDivisionError
            If p = 1, internals cannot be made.

        '''
        df = df_mod.copy()

        internal_idx = df[df['label'] == 'internal'].index.tolist()
        #print(internal_idx)

        # Intervals
        first = df.groupby('layer').first()                    # make series of intervals
        last = df.groupby('layer').last()

        # TODO: Unsure if this is accessed; check flow to see if this case is triggered
        if p == 1:
            raise ZeroDivisionError('p-1.  Interval cannot be calculated.')
        else:
            intervals = (last[column] - first[column]) / (p - 1)
            intervals.name = 'intervals'
        #print(intervals)

        # Join Column of firsts and intervals to df
        s_first = first[column]
        s_first.name = 'firsts'
        joined = df.join(s_first, on='layer')                  # x_0; join long df with short s to get equal lengths
        joined = joined.join(intervals, on='layer')            # join long df with short intervals for internal_sums
        #print(joined)

        '''Interval or internal sums?'''
        # Calc. Interval Sums
        trunc = joined[(joined['label'] != 'interface') & (
            joined['label'] != 'discont.')]                    # remove firsts and lasts from cumsum
        ##'''cumsum is not working with groupby in pandas 0.17.1'''
        ##internal_sums = np.cumsum(
        ##    trunc.groupby('layer')['intervals'])               # delta; apply sigma from algo
        internal_sums = trunc.groupby('layer')['intervals'].cumsum()  # 0.17.2 work around; backwards compat.
        #print(clipped)
        #print(internal_sums)

        # Apply Internals to df
        df.loc[internal_idx, column] = joined.loc[
            internal_idx, 'firsts'] + internal_sums            # although shorter, internals added to joined_df by index
        if p % 2 != 0:
            df.loc[df['label'] == 'neut. axis', column] = df[column].mean()

        return df
    ###

    # Attributes --------------------------------------------------------------
    '''Need Laminate info property to display on repr().'''
    @property
    def p(self):
        '''Return number of rows per layer for a given laminate; default LFrame.'''
        df = self.LFrame
        return df.groupby('layer').size().unique()[0]

    @property
    def total(self):
        '''Return the total laminate thickness (in m); default LFrame.'''
        df = self.LFrame
        return df.groupby('layer')['t(um)'].unique().sum()[0] * 1e-6

    @property
    def max_stress(self):
        '''Return Series view of max principal stresses per layer, ~ p = 1.'''
        df = self.LMFrame
        return df.loc[df['label'] == 'interface', 'stress_f (MPa/N)']

    @property
    def min_stress(self):
        '''Return Series view of min principal stresses per layer, ~ p = 1.'''
        df = self.LMFrame
        if df['label'].str.contains('discont.').any():
            return df.loc[df['label'] == 'discont.', 'stress_f (MPa/N)']
        else:
            print('Only maxima detected.')
            return None

    @property
    def extrema(self):
        '''Return DataFrame excluding internals, showing only maxima and minima.'''
        df = self.LMFrame
        maxima = (df['label'] == 'interface')
        minima = (df['label'] == 'discont.')
        return df.loc[maxima | minima, :]

    '''or name recap'''
    @property
    def summary(self):
        '''Print a summary of Laminate properties.

        Parameters
        ----------
        nplies : int
            number of plies
        p : int
            number of points per layer
        ...

        '''
        pass                                               # pragma: no cover

    # Checks ------------------------------------------------------------------
    # Read from DataFrames
    @property
    def is_special(self):
        '''Return True if nplies < 5; Monolith, Bilayer, Trilayer, 4-ply.'''
        return self.nplies < 5

    # TODO: only return pertinent rows
    @property
    def has_discont(self):
        '''Return Series, True at rows where discontinuities are present.

        Notes
        -----
        Generally, disconts are present for laminates with p >= 2 for all nplies.
        Disconts are not present for monoliths with p = 2.

        '''
        return self.LMFrame['label'].str.contains('discont.')

    # TODO: only return True, not series
    @property
    def has_neutaxis(self):
        '''Return Series, True at row where neutral axis row is present; for odd plies.'''
        return self.LMFrame['label'].str.contains('neut. axis')
        # TODO: repalce with below
        #return self.LMFrame['label'].str.contains('neut. axis').any()

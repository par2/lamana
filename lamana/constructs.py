# -----------------------------------------------------------------------------
'''A module that builds core objects, such as stacks and laminates.'''
# Stack() : an dict of the order laminate layers.
# Laminate() : pandas objects including laminate dimensions and calculations

import logging
import itertools as it
import collections as ct

import numpy as np
import pandas as pd

from . import theories
from . import output_
from .lt_exceptions import IndeterminateError
from .lt_exceptions import ModelError
from .utils import tools as ut

# from lamana import theories
# from lamana.utils import tools as ut
# from lamana.lt_exceptions import IndeterminateError, ModelError

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

    FeatureInput is parsed here and attributes are bubbled up through the subclasses.

    Parameters
    ----------
    FeatureInput : dict
        Use `Geometry` key to extract the `GeometryTuple` (converted geometry string)
        Can directly accept a Geometry object.  Changed to accept FI only in 0.4.11.

    Attributes
    ----------
    Geometry : Geometry object
        Converted Geometry string.
    load_params : dict; default None
        A dict of common loading parameters, sample and support radii, etc.
    mat_props : dict; default None
        A dict of materials and properties, i.e. elastic modulus and Poisson's ratio.
    materials : DataFrame
        Converted mat_props to pandas object; used for quick display.
    model : str
        Specified custom, laminate theory model.
    StackTuple : namedtuple
        Contains stack items (see below).
    {stack_order, nplies, name, alias} : list, str, str, str
        StackTuple attributes.

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

    Notes
    -----
    - (0.4.11) object parsing starts here and args bubble up through subclasses

    See Also
    --------
    collections.namedtuple : special tuple in the Python Standard Library.

    '''
    def __init__(self, FeatureInput):
        # Parse FeatureInput
        self.FeatureInput = FeatureInput.copy()                      # for preserving FI in each Case
        self.Geometry = self.FeatureInput['Geometry']
        self.load_params = self.FeatureInput['Parameters']
        self.mat_props = self.FeatureInput['Properties']
        self.materials = self.FeatureInput['Materials']
        self.model = self.FeatureInput['Model']

        # Parse Stack Object
        # TODO: Improve recall
        decoded = self.decode_geometry(self.Geometry)
        self.unfolded = list(decoded)                                # used in tests
        '''Recalled because generator exhausts decoded.  Improve.'''
        decoded = self.decode_geometry(self.Geometry)

        self.StackTuple = self.identify_geometry(decoded)            # namedtuple of (stack, nplies, name, alias)
        self.stack_order = self.StackTuple.order
        self.nplies = self.StackTuple.nplies
        self.name = self.StackTuple.name
        self.alias = self.StackTuple.alias                           # new in 0.4.3c5a

    def decode_geometry(self, Geometry):
        '''Return a generator that decodes the Geometry object.

        Interprets the stacking order and yields a tuple of the lamina type
        (ltype) and thickness.

        A `Geometry` object has a .geometry attribute returning a namedtuple of
        laminae thicknesses labeled:

        - ['outer', 'inner', 'middle', 'symmetric']                  # symmetry convention
        - ['outer', 'inner', 'middle']                               # general conventions

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
        def get_decoded():                                           # procedure
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

        def listify_layer(Geometry):                                 # pure function 1
            '''Return a converted Geometry namedtuple to a list of tuples; pops symmetric entry'''
            layers = list(Geometry.geometry._asdict().items())
            if Geometry.is_symmetric:                                # clean up last element; see namedtuple of symmetric Geometry
                layers.pop()
                '''Add to verbose mode.'''
                #print('Symmetry detected in Geometry object.  Conforming to General Convention...')
            return layers

        def process_layer(ltype, thickness, reverse=False):          # pure function 2
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
        order = ct.defaultdict(list)                                 # subs empty {}

        '''Is there a way to replace this nested counter with something pythonic?'''
        layer_ = 0                                                   # nested counter
        for (ltype, thickness) in decoded:
            #print(ltype, thickness)
            # Exclude Zero layers from the Stack
            if thickness != 0.0:
                layer_ += 1                                          # updates only for non-zero thickness laminae
                order[layer_].append(ltype)                          # adds tuple elements into the defaultdicts list
                order[layer_].append(thickness)                      # ...
        nplies = layer_                                              # updates, but last layer_ is retained in nplies
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
            clean_values.extend(stack[ind])                          # take extant stack
            clean_values.append(material)                            # add new value
            stack[ind] = clean_values

            if ind == nplies:
                '''Add to verbose mode.'''
                #print('Stack materials have been updated.')
                return stack

    @classmethod
    def stack_to_df(cls, stack):
        '''Return a DataFrame of converted stacks with materials (list of dicts).'''
        df = pd.DataFrame(stack).T
        df.reset_index(level=0, inplace=True)                        # reset index; make new column
        df.columns = ['layer', 'type', 't(um)', 'matl']              # rename columns
        recolumned = ['layer', 'matl', 'type', 't(um)']
        df = ut.set_column_sequence(df, recolumned)                  # uses ext. f(x)
        df[['t(um)']] = df[['t(um)']].astype(float)                  # reset numeric dtypes
        return df


# =============================================================================
# LAMINATES -------------------------------------------------------------------
# =============================================================================
# Create Laminate objects


class Laminate(Stack):
    '''Create a `Laminate` object.

    Laminate layers are represented as DataFrame rows.  `Laminate` inherits from
    the `Stack` class.

    Native objects:

    - `Snapshot` : stack of unique layers (1, 2, ..., n), single rows and ID columns.
    - `LFrame` : snapshot with multiple rows including Dimensional Data.

    The listed Parameters are "ID Variables" found in `Snapshot`.  The Other
    Parameters are known as "Dimensional Variables" found in all native objects.
    These are special variables pertaining to columns in DataFrames; they are
    suffixed with trailing underscores.   These parameters are NOT arguements.

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
        Type of point, e.g. interfacial, internal or discontinuity.
    h_ : float
        Lamina thickness for each lamina, except middle layers (half thickness).
    d_ : float
        Distance from the bottom layer; handshakes with calculations in
        `theories.<Model>` and used in testing. Units (m).
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
    summary
    is_special
    has_discont
    has_neutaxis
    frame
    {Snapshot, LFrame} : DataFrame
        Laminate objects.

    Methods
    -------
    to_csv(**kwargs)
        Exports LaminateModel data and FeatureInput dashboard as separate files.
    to_xlsx(offset=3, **kwargs)
        Exports a single file of both LaminateModel data and FeatureInput dashboard.

    Raises
    ------
    IndeterminateError
        If custom attributes could not be set to the `LaminateModel`.
        Handled to rollback and return an LFrame.

    See Also
    --------
    constructs.Stack : base class; initial FeatureInput parser
    constructs.LaminateModel : child class; full LM object
    theories.BaseModel : handles user defined Laminate Theory models
    theories.handshake : gives LFrame data, gets LMFrame back
    models : directory containing package models

    Examples
    --------
    >>> import lamana as la
    >>> FeatureInput['Geometry'] = la.input_.Geometry('400-[200]-800')
    >>> la.constructs.Laminate(FeatureInput)
    <lamana Laminate object (400.0-[200.0]-800.0)>

    '''
    def __init__(self, FeatureInput):
        super(Laminate, self).__init__(FeatureInput)

        self._type_cache = []

        # Laminate Objects
        self.Snapshot = self._build_snapshot()                       # df object; stack
        self._primitive = self._build_primitive()                    # phase 1
        self.LFrame = self._build_LFrame()                           # phase 1; df of IDs; formerly Laminate_
        self._frame = self.LFrame                                    # general accessor


    def __repr__(self):
        return '<lamana {} object ({}), p={}>'.format(
            self.__class__.__name__, self.Geometry.__str__(), self.p
        )

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
            blacklisted.append('_dict_trim')                         # prevent infinite loop
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
        of GeometryTuple with tupled inner instead.

        '''
        return hash((self.Geometry, self.p))

    def _build_snapshot(self):
        '''Build a quick, skeletal view of the stack (Snapshot).

        Assign materials and stress states to self.stack_order.  Optimized by
        concatenation; omits looping.

        '''
        stack_extended = Stack.add_materials(self.stack_order, self.materials)
        Snapshot = Stack.stack_to_df(stack_extended)
        # TODO: Dehardcode Laminate
        return Laminate._set_stresses(Snapshot)

    # PHASE 1
    def _build_primitive(self):
        '''Build a primitive laminate from a stack.

        Build in three steps:

        1. Adopt the Snapshot and add more rows to each layer.
        2. Glue lamina together to make one DataFrame.
        3. Add column of expected stress (`side_`).

        Returns
        -------
        DataFrame
            An extended snapshot; adds p rows per layer.

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
        # TODO: dehardcode Lamainate for self.__class__
        df = Laminate._set_stresses(df)
        #print(df)

        # Build Laminate with Classes
        layers = df.groupby('layer')
        self._type_cache = layers['type'].unique()
        self._type_cache.apply(str)                                  # converts to str class, not str alone

        #self.LFrame = df                                             # retains copy of partial Laminate (IDs & Dimensionals)
        return df

    # PHASE 2
    def _build_LFrame(self):
        '''Update Laminate DataFrame with new dimensional columns.

        This function takes a primitive LFrame (converted Stack) and adds
        columns: `label`, `h(m)`, `d(m)`, `intf`, `k`, `Z(m)`, `z(m)`, `z(m)*`
        A number of pandas-like implementations are performed to achieve this,
        so the coding has a different approach and feel.

        '''
        # For Implementation
        nplies = self.nplies
        p = self.p
        t_total = self.total
        #print('nplies: {}, p: {}, t_total (m): {}'.format(nplies, p, t_total))

        ##df = self.LFrame.copy()
        df = self._primitive

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

        # Z_ ----------------------------------------------------------------------
        # Distance from ith level to the neutral access
        middle = t_total / 2.
        df['Z(m)'] = middle - df['d(m)']
        if (nplies == 1) & (p == 1):                                 # d_ = t_total here, so must amend
            df['Z(m)'] = t_total / 2.

        # z_ ----------------------------------------------------------------------
        # Distance from ith Z-midplane level to the neutral access
        # Two flavors are implemented for linearly and log-distributed z_ (z(m) and z(m)*)
        t_mid = df.loc[df['label'] == 'interface', 'h(m)'] / 2.      # for midplane calc.
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
        ##self.LFrame = ut.set_column_sequence(df, sort_columns)
        return ut.set_column_sequence(df, sort_columns)

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
        stack_types = [row for row in self.Snapshot['type']]         # control
        #print(stack_types)
        abbrev = [letters[0][0].upper()                              # use if type_cache is ndarray
                  for letters in self._type_cache]                   # easier to see
        assert self._type_cache.tolist() == stack_types, \
            'Lamina mismatch with stack types, \
                  \n {} instead of \n {}'.format(self._type_cache, stack_types)
        return abbrev

    '''Find way replace staticmethods with class methods.'''
    @classmethod
    def _set_stresses(cls, df):                                      # == side_()
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
            df.iloc[half_the_stack, side_loc] = 'None'               # for odd p
        # Other plies
        '''Replace with p'''
        if n_rows > 1:
            df.iloc[:half_the_stack, side_loc] = 'Tens.'             # applies to latest column 'side'
            df.iloc[-half_the_stack:, side_loc] = 'Comp.'
        return ut.set_column_sequence(df, cols)

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
        first = df.groupby('layer').first()                          # make series of intervals
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
        joined = df.join(s_first, on='layer')                        # x_0; join long df with short s to get equal lengths
        joined = joined.join(intervals, on='layer')                  # join long df with short intervals for internal_sums
        #print(joined)

        '''Interval or internal sums?'''
        # Calc. Interval Sums
        trunc = joined[(joined['label'] != 'interface') & (
            joined['label'] != 'discont.')]                          # remove firsts and lasts from cumsum
        ##'''cumsum is not working with groupby in pandas 0.17.1'''
        ##internal_sums = np.cumsum(
        ##    trunc.groupby('layer')['intervals'])                   # delta; apply sigma from algo
        internal_sums = trunc.groupby('layer')['intervals'].cumsum() # 0.17.2 work around; backwards compat.
        #print(clipped)
        #print(internal_sums)

        # Apply Internals to df
        df.loc[internal_idx, column] = joined.loc[
            internal_idx, 'firsts'] + internal_sums                  # although shorter, internals added to joined_df by index
        if p % 2 != 0:
            df.loc[df['label'] == 'neut. axis', column] = df[column].mean()

        return df
    ###

    # These methods export data
    def to_csv(self, **kwargs):
        '''Write LaminateModel data FeatureInput dashboard as separate files.

        Returns
        -------
        tuple
            Paths for both .csv files.

        See Also
        --------
        - `output_.export`: for kwargs and docstring.

        '''
        data_fpath, dash_fpath = output_.export(self, suffix='.csv', **kwargs)
        return data_fpath, dash_fpath

    def to_xlsx(self, offset=3, **kwargs):
        '''Write LaminateModel data FeatureInput dashboard as one file.

        Returns
        -------
        tuple
            Path for .xlsx file; maintained For type consistency.

        See Also
        --------
        - `output_.export`: for kwargs and docstring.

        '''
        (workbook_fpath,) = output_.export(self, suffix='.xlsx', offset=offset, **kwargs)
        return (workbook_fpath,)

    # Properties --------------------------------------------------------------
    '''Need Laminate info property to display on repr().'''
    @property
    def p(self):
        '''Return number of rows per layer for a given laminate; default LFrame.'''
        ##df = self.LFrame
        df = self._primitive
        return df.groupby('layer').size().unique()[0]

    @property
    def total(self):
        '''Return the total laminate thickness (in m); default LFrame.'''
        ##df = self.LFrame
        df = self._primitive
        return df.groupby('layer')['t(um)'].unique().sum()[0] * 1e-6

    @property
    def frame(self):
        '''Return the Laminate DataFrame (LFrame).'''
        return self._frame

    # TODO: only return pertinent rows
    @property
    def has_discont(self):
        '''Return Series, True at rows where discontinuities are present.

        Notes
        -----
        Generally, disconts are present for laminates with p >= 2 for all nplies.
        Disconts are not present for monoliths with p = 2.

        '''
        return self._frame['label'].str.contains('discont.')

    # TODO: only return pertinent rows
    @property
    def has_neutaxis(self):
        '''Return Series, True at row where neutral axis row is present; for odd plies.'''
        return self._frame['label'].str.contains('neut. axis')
        # TODO: repalce with below
        ##return self.LMFrame['label'].str.contains('neut. axis').any()

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
        pass                                                         # pragma: no cover

    # Checks ------------------------------------------------------------------
    # Read from DataFrames
    @property
    def is_special(self):
        '''Return True if nplies < 5; Monolith, Bilayer, Trilayer, 4-ply.'''
        return self.nplies < 5


# =============================================================================
# LaminateModel ---------------------------------------------------------------
# =============================================================================
# Create a LaminateModel

#from lamana import theories

class LaminateModel(Laminate):
    '''Create a `LaminateModel` object or raise an exception.

    This class inherits from `Laminate` and `Stack`. A `FeatureInput` is passed
    in from a particular "Feature" module and exchanged between `constructs` and
    `theories` modules.

    Native object:
    - `LMFrame` : an `LFrame` with Dimensional and Data variables via
    `theories.<model>` calculations.  This DataFrame is either updated
    or not.

    Finally this class builds a `LamainateModel` object, merging the Laminate
    data with the Model data defined by an author in a separate `models` module;
    model variables relate to classical laminate theory variables, i.e. `Q11`, `Q12`,
    `D11`, `D12`, ..., `stress`, `strain`, etc.

    Parameters
    ----------
    FeatureInput : dict
        Passed-in, user-defined object from Case.

    Attributes
    ----------
    frame
    extrema
    max_stress
    min_stress
    has_discont
    has_neutaxis
    LMFrame : DataFrame
        Updated DataFrame combined new variables with LFrame variable.
        The completed LaminateModel object.
    {Middle, Inner_i, Outer} : DataFrame
        Isolated layer types
    {compressive, tensile} : DataFrame
        Isolated layer stress sides.

    See Also
    --------
    constructs.Stack : base class; initial FeatureInput parser
    constructs.Laminate : parent class; precursor to LM object
    theories.BaseModel : handles user defined Laminate Theory models
    theories.handshake : gives LFrame data, gets LMFrame back
    models : directory containing package models

    Raises
    ------
    ModelError : for issues applying the updated calculations to LaminateModel

    Examples
    --------
    >>> # From Scratch
    >>> import lamana as la
    >>> FeatureInput = {
            'Geometry': la.input_.Geometry('400.0-[200.0]-800.0'),
            'Materials': ['HA', 'PSu'],
            'Model': 'Wilson_LT',
            'Parameters': {'P_a': 1, 'R': 0.012, 'a': 0.0075, 'p': 5, 'r': 0.0002},
            'Properties': {'Modulus': {'HA': 52000000000.0, 'PSu': 2700000000.0},
            'Poissons': {'HA': 0.25, 'PSu': 0.33}}
        }
    >>> LaminateModel(FeatureInput)
    <lamana LaminateModel object (400.0-[200.0]-800.0)>

    >>> # With Defaults
    >>> import lamana as la
    >>> from lamana.models import Wilson_LT as wlt
    >>> dft = wlt.Defaults()
    >>> LaminateModel(dft.FeatureInput)
    <lamana LaminateModel object (400.0-[200.0]-800.0)>

    '''

    def __init__(self, FeatureInput, **kwargs):
        super(LaminateModel, self).__init__(FeatureInput)
        # Adopts Laminate and Stack attributes also
        ##self.LMFrame = None
        self.LMFrame = self._build_LMFrame(**kwargs)
        self._frame = self.LMFrame                         # accessor

        # LaminateModel Attributes
        self.Middle = self.LMFrame[self.LMFrame['type'] == 'middle']
        self.Inner_i = self.LMFrame[self.LMFrame['type'] == 'inner']
        self.Outer = self.LMFrame[self.LMFrame['type'] == 'outer']
        self.compressive = self.LMFrame[self.LMFrame['side'] == 'Comp.']
        self.tensile = self.LMFrame[self.LMFrame['side'] == 'Tens.']

    # PHASE 3
    def _build_LMFrame(self, **kwargs):
        '''Update `LaminateModel` DataFrame and `FeatureInput`.

        Tries to update `LaminateModel`. If an exception is raised (on the model
        side), no update is made, and the Laminate (without Data columns) is set
        as the default `LFrame`; this is a "rollback."

        - populates stress data calculations from the selected model.
        - may add extra keys to `FeatureInput`, e.g. 'Globals'

        Raises
        ------
        ModelError : If the initial LaminateModel object passed to handshake is not
                     empty, i.e. has LMFrame != None, then updates are unpredictable.

        '''
        try:
            # Pass in the pre-updated LaminateModel object; no LMFrame yet
            LMFrame, self.FeatureInput = theories.handshake(self, **kwargs)
            return LMFrame
        except(IndeterminateError) as e:
            raise ModelError(
                'An error was detected while updating {}.'.format(self.__class__.__name__)
            )

    # Properties --------------------------------------------------------------
    @property
    def frame(self):
        '''Return the Laminate DataFrame (LFrame).'''
        return self._frame

    @property
    def extrema(self):
        '''Return DataFrame excluding internals, showing only maxima and minima.'''
        df = self._frame
        maxima = (df['label'] == 'interface')
        minima = (df['label'] == 'discont.')
        return df.loc[maxima | minima, :]

    @property
    def max_stress(self):
        '''Return Series view of max principal stresses per layer, ~ p = 1.'''
        df = self._frame
        return df.loc[df['label'] == 'interface', 'stress_f (MPa/N)']

    @property
    def min_stress(self):
        '''Return Series view of min principal stresses per layer, ~ p = 1.'''
        df = self._frame
        if df['label'].str.contains('discont.').any():
            return df.loc[df['label'] == 'discont.', 'stress_f (MPa/N)']
        else:
            logging.info('Only maxima detected.')
            return None

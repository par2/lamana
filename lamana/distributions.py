# -----------------------------------------------------------------------------
'''A Feature Module of classes and functions related to stress distributions.'''
# Case() : A collection of LaminateModel objects
# Cases() : A collection of Cases
# flake8 distributions.py --ignore E265,E501,N802,N806

import os
import importlib
import collections as ct
import itertools as it

import pandas as pd
import matplotlib.pyplot as plt

import lamana as la
from lamana.input_ import BaseDefaults
from lamana.utils import tools as ut

bdft = BaseDefaults()

# =============================================================================
# FEATUREINPUT ----------------------------------------------------------------
# =============================================================================
# Builds FeatureInput objects & makes calls for building LaminateModel objects.


class Case(object):
    '''Build a Case object that handles User Input parameters.

    Attributes
    ----------
    materials
    {middle, inner, outer, total}
    total_{middle, inner, inner_i, outer}
    snapshots
    frames
    LMs
    size
    load_params : dict; default None
        A dict of common loading parameters, sample and support radii, etc.
    mat_props : dict; default None
        A dict of materials and properties, i.e. elastic modulus and Poisson's ratio.
    parameters : Series
        Converted load_params to pandas object; used for quick display.
    properties : DataFrame
        Converted mat_props to pandas object; used for quick display.
    Geometries : list of Geometry objects
        A container for multiple Geometry objects.
    model : str
        Specified custom, laminate theory model.
    LaminateModels : list of DataFrames
        Each DataFrame represents a laminate stack containing calculations
        from the applied laminate theory model.
    p : int
        Datapoints per lamina.  Although available in FeatureInput, this
        attribute is mainly is used for quick access in string representations.

    Methods
    -------
    apply(geo_strings=None, model='Wilson_LT', unique=False)
        Return `LaminateModel` and `FeatureInput` objects by iterating geometry
        strings.  Accept user geometries and selected model.
    plot(**kwargs)
        Return matplotlib plots given laminate DataFrames.

    Raises
    ------
    TypeError
        If load_params or mat_props is None; needs a dict and nested dict
        respectively.

    Notes
    -----
    See the "Getting Started" documentation for a sample loading configuration
    diagram.

    '''

    # Automated Parameters
    '''Rename args to load_params and mat_props.'''
    # TODO: remove materials kwarg (?)
    def __init__(self, load_params=None, mat_props=None, materials=None):
        # Default Parameters
        if load_params is not None:
            self.load_params = load_params
        else:
            raise TypeError('Expected a dict of loading parameter values.')

        # Material Properties and Materials Order List
        if mat_props is not None:
            self.mat_props = bdft._convert_material_parameters(mat_props)
        else:
            raise TypeError('Expected a nested dict of material properties.')
        self._materials = bdft.get_materials(self.mat_props)

        # Display pandas Views
        self.parameters = pd.Series(self.load_params)     # parameters Series
        self.properties = self.set_properties()

        ##self.Geometries = []
        self.model = ''
        self.LaminateModels = []
        self.p = []                                   # added 0.4.3d

    def __str__(self):                                # for object calls
        '''Return a string repr of a Geometry object.'''
        ##return'<{}>'.format(self.__class__)
        return'<{} p={}>'.format(self.__class__, self.p)

    def __repr__(self):                               # for object calls
        '''Return a string repr of a Geometry object.'''
        ##return'<{}>'.format(self.__class__)
        return'<{} p={}, size={}>'.format(self.__class__, self.p,
                                          len(self.LaminateModels))

    def __eq__(self, other):
        '''Compare Case objects, designed to handle pandas objects.

        Notes
        -----
        DEV: `__eq__` handles all DataFrame/Series items of `__dict__` separately.
        Attribute names with DataFrame/Series assignments are blacklisted
        and checked separately from other `__dict__` items.

        '''

        if isinstance(other, self.__class__):
            # Auto check attrs if assigned to DataFrames/Series, then add to list
            blacklisted = [attr for attr in self.__dict__ if
                           isinstance(getattr(self, attr), (pd.DataFrame, pd.Series))]

#             DEV: Blacklist attribute names pointing to DataFrames/Series here.
#             blacklisted = ['parameters', 'properties']
            # Check DataFrames and Series
            for attrname in blacklisted:
                ndf_eq = ut.ndframe_equal(getattr(self, attrname),
                                          getattr(other, attrname))
                ##ndf_eq = ndframe_equal(getattr(self, attr), getattr(other, attr))

            # Ignore pandas objects; check rest of __dict__ and build trimmed dicts
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

    def set_properties(self, list_order=None):
        '''Set the material order of the quick view DataFrame for properties.'''
        df_properties = pd.DataFrame(self.mat_props).copy()
        df_properties.index.name = 'materials'
        if list_order is not None:
            df_properties.reindex(list_order)
            df_properties.sort_index(ascending=False, inplace=True)
        else:
            df_properties.reindex(self._materials)    # set index order in view
        return df_properties

    # TODO: accept kwargs
    def apply(self, geo_strings=None, model='Wilson_LT', unique=False):
        '''Apply geometries and laminate theory model to a `LaminateModel`.

        Convert user inputs general convention, then to `Geometry` objects
        and iterate to assign a laminate theory model, make a `FeatureInput`
        object and build DataFrames.

        Three essential objects that are created here are:

        - Geometry : list of mixed types
            Converted user input geometries; uses `input_.Geometry().` Note the
            upper case "G" implies a converted geometry string to Geometry object.
        - FeatureInput : dict
            Container for parameters used in building laminates;
        - LaminateModels : list of DataFrames
            DataFrames representing a laminate stack containing calculations
            using the applied laminate theory model.

        Parameters
        ----------
        geo_strings : list of str; default None
            User input geometry strings.  Note lower case  'geo' implies a
            simple geometry string.
        model : str; default 'Wilson_LT
            Selected model is a custom model found in `models` directory.
        unique : bool; default False
            Apply a set of unique geometry strings.

        Returns
        -------
        None
            Updates certain attributes.

        Raises
        ------
        ValueError
            If no value geometry strings are found.

        See Also
        --------
        lamana.input_.Geometry : convert user input geometries to usable code.
        lamana.constructs.Laminate : build DataFrames containing laminate calculations.
        lamana.constructs.Laminate.build_laminate : uses `FeatureInput`.

        Notes
        -----
        DEV: be careful what you assign to self.  Remember `self.__dict__`
        is used for comparisons via `__eq__`.  If used, consider adding to
        blacklisted list in `__eq__`.

        '''
        '''Consider moving, to all only once.'''
        G = la.input_.Geometry
        self.Geometries = []
        self.model = model

        '''Find way to convert unique geos and add to cache.'''

        # Defaults
        if geo_strings is None:
            # TODO: Add is_valid(geometry) here? Almost like type checking
            raise ValueError("No geometries found.  Please input valid geometry, "
                             "e.g. '400-[200]-800.'")
            ##raise Exception("No geometries found.  Please input valid geometry, e.g. '400-[200-800.'")
            '''Tried to exclude loop, but f(x) needs to iterate and make a list prior to unique.'''
            '''Consider checking a unique appended cache iteratively.'''
#         else:
#             self._geo_strings = geo_strings

        def get_LaminateModels(geometries):
            '''Yield a LaminateModel; build a FeatureInput.

            Set Geometry objects to instance given an iterable of geometry strings.
            Also set p for info (i.e. string representation).

            Notes
            -----
            First checks a cache of unique converted geo_strings before LM; strings are
            more efficient to check than Geometry objects.

            Builds and sets a `LaminateModel`, `FeatureInput` and sets the `p`
            attribute simultaneously.

            Yields
            ------
            LaminateModel
                DataFrame of laminate theory calculations.

            '''
            _geo_cache = set()

            for geometry in geometries:
                conv_geometry = la.input_.Geometry._to_gen_convention(geometry)

                # Check a cache
                if unique and (conv_geometry in _geo_cache):
                    pass
                else:
                    # Make G, FI and LM
                    Geometry = G(conv_geometry)            # convert geometries to Geometry objects (namedtuples)
                    #print(self.materials)
                    FeatureInput = bdft.get_FeatureInput(
                        Geometry,
                        load_params=self.load_params,
                        mat_props=self.mat_props,
                        materials=self._materials,
                        model=self.model,
                        global_vars=None,
                    )
                    '''Add to info?'''
                    _geo_cache.update([conv_geometry])     # make unique set of geo strings to skip if unique
                    self.Geometries.append(Geometry)
                    self.p = FeatureInput['Parameters']['p']
                    #print(conv_geometry)
                    #print(_geo_cache)
                    #print(FeatureInput)
                    '''Is there a way to save a general FI for the Case?'''
                    # TODO: accept kwargs
                    yield la.constructs.Laminate(FeatureInput)

            # DEPRECATED AttributeError exception.
        self.LaminateModels = list(get_LaminateModels(geo_strings))
        print('User input geometries have been converted and set to Case.')

    # TODO: get ipython directives working to plot figures from docstrings.
    # TODO: emulate pandas, return an mpl axes instead of None; change test
    def plot(self, title=None, subtitle=None, x=None, y=None, normalized=None,
             halfplot=None, extrema=True, separate=False, legend_on=True,
             colorblind=False, grayscale=False, annotate=False, inset=False,
             ax=None, subplots_kw=None, suptitle_kw=None, **kwargs):
        '''Plot single and multiple LaminateModels.

        Plots objects found within a list of LMs.  Assumes Laminate objects are
        in the namespace.  Calls `lamana.output_._distribplot()` for
        single/multiple geometries.

        Parameters
        ----------
        title : str; default None
            Suptitle; convenience keyword
        subtitle : str; default None
            Subtitle; convenience keyword.  Used ax.text().
        {x, y} : str; default None
            DataFrame column names.  Users can manually pass in other columns names.
        normalized : bool; default None
            If true, plots y = `k_`; else plots y = `d_` unless specified otherwise.
        halfplot : str; default None
            Trim the DataFrame to read either 'tensile', 'compressive' or `None`.
        extrema : bool; default True
            Plot minima and maxima only; equivalent to p=2.
        separate : bool; default False
            Plot each geometry in separate subplots.
        legend_on : bool; default True
            Turn on/off plot
        colorblind : bool; default False
            Set line and marker colors as colorblind-safe.
        grayscale : bool; default False
            Set everything to grayscale; overrides colorblind.
        annotate : bool; default False
            Annotate names of layer types.
        inset: bool; default None
            Unnormalized plot of single geometry in upper right corner.
        ax : matplotlib axes; default None
            An axes containing the plots.
        subplots_kw : dict; default None
            Default keywords are initialed to set up the distribution plots.
            (`ncols`=1, `figsize`=(12, 8), `dpi`=300)
        suptitle_kw : dict; default None
            Default keywords are initialed to set up the distribution plots.
            (`fontsize`=15, `fontweight`='bold')

        Notes
        -----
        Here are some preferred idioms (not yet implemented):

        >>> case.LM.plot()                                # geometries in case
        Case Plotted. Data Written. Image Saved.
        >>> case.LM[4:-1].plot()                          # handle slicing
        Case Plotted. Data Written. Image Saved.

        See Also
        --------
        lamana.constructs.Laminate : builds the `LaminateModel` object.
        lamana.output_._distribplot : generic handler for stress distribution plots.
        lamana.output_._multiplot : plots multiple cases as subplots (caselets).
        lamana.distributions.Cases.plot : makes call to `_multiplot()`.

        '''
        #print('Accessing plot() method.')
        # FIGURE ------------------------------------------------------------------
        # Set defaults for plots
        title = '' if title is None else title
        subtitle = '' if subtitle is None else subtitle

        subplots_kw = {} if subplots_kw is None else subplots_kw
        subplots_dft = dict(figsize=(12, 9), dpi=300,)
        ##subplots_dft = dict(ncols=1, figsize=(12, 8), dpi=300,)
        subplots_kw.update({k: v for k, v in subplots_dft.items() if k not in subplots_kw})

        suptitle_kw = {} if suptitle_kw is None else suptitle_kw
        ##suptitle_kw = {} if suptitle_kw is None else sup_title_kw
        suptitle_dft = dict(fontsize=15, fontweight='bold')
        suptitle_kw.update({k: v for k, v in suptitle_dft.items() if k not in subplots_kw})

        LMs = self.LMs
        #LMs = cases.LMs                                 # multiple geos
        #LMs = case.LMs                                  # single geo

        ### BETA 0.4.4b2
        # Caselets ----------------------------------------------------------------
        # Plot single geometries separately; a special case of _multiplot
        if separate and len(LMs) > 1:                   # one plot is not multiplot
            caselets = LMs                              # will trigger exception handling

            # Defaults for processing unnormalized single geometries
            normalized = False if normalized is None else normalized
            subplots_kw.update(dict(ncols=2))

            # Returns a full figure (not just an axes).
            # Uses internal code for suptitles.
            # Custom plt.text disallowed due to complexity, e.g. subtitles.
            la.output_._multiplot(
                caselets, halfplot=halfplot, normalized=normalized,
                extrema=extrema, legend_on=legend_on, colorblind=colorblind,
                grayscale=grayscale, annotate=annotate, subplots_kw=subplots_kw,
                suptitle_kw=suptitle_kw, **kwargs
            )

        # Single/Multiple Geometries ----------------------------------------------
        else:
            fig, ax = plt.subplots(**subplots_kw)           # Set fig dimensions and dpi
            normalized = True if normalized is None else normalized
            la.output_._distribplot(
                LMs, x=x, y=y, halfplot=halfplot, normalized=normalized,
                extrema=extrema, legend_on=legend_on, colorblind=colorblind,
                grayscale=grayscale, annotate=annotate, ax=ax, **kwargs
            )

            # Insets --------------------------------------------------------------
            '''Brittle; labels are hard-coded.  Could use abstraction for customization.'''
            # Inset; plots unnormalized by d(m)
            if inset and len(LMs) == 1:
                ##ax2 = fig.gca()
                ax2 = plt.axes([.62, .55, .27, .27])    # upper right corner
                ##ax2 = plt.axes([.22, .22, .27, .27])   # lower left corner
                la.output_._distribplot(
                    LMs, x=x, y=y, normalized=False, extrema=extrema,
                    legend_on=False, colorblind=colorblind, grayscale=grayscale,
                    ax=ax2, xlabel='', ylabel='height (m)'
                )

            # Label Figure    Stress distribution plot with layer annotations:
            '''Find solution for general args in titles'''
            plt.suptitle(title, **suptitle_kw)
            plt.text(0.5, 1.03, subtitle, ha='center', va='center', transform=ax.transAxes)
            plt.rcParams.update({'font.size': 12})

            plt.show()

    @property
    def materials(self):
        '''Override the _materials attribute.

        Raises
        ------
        NameError
            If a trying to set a name not already in the materials list.

        '''
        print('Getting materials...')
        return self._materials

    @materials.setter
    def materials(self, list_order):
        '''Reset materials order with a list. Change properties index.'''
        print('Overriding materials order...')
        if set(list_order).issubset(self.mat_props['Modulus'].keys()):
            self._materials = list_order
            self.properties = self.set_properties(list_order)
        else:
            raise NameError('A listed name was not found in mat_props.')

    @property
    def middle(self):
        '''Return thicknesses of the middle layers.'''
        return [Geo.middle for Geo in self.Geometries]

    @property
    def inner(self):
        '''Return thicknesses of the inner layers.'''
        return [Geo.inner for Geo in self.Geometries]

    @property
    def outer(self):
        '''Return thicknesses of the outer layers.'''
        return [Geo.outer for Geo in self.Geometries]

    # Totals
    @property
    def total(self):
        '''Return total laminate thickness.'''
        return [Geo.total for Geo in self.Geometries]

    @property
    def total_middle(self):
        '''Return total thicknesses of the middle layer.'''
        return [Geo.total_middle for Geo in self.Geometries]

    @property
    def total_inner(self):
        '''Return thicknesses of all inner layers.'''
        return [Geo.total_inner for Geo in self.Geometries]

    @property
    def total_inner_i(self):
        '''Return thicknesses of the separate inner layers.'''
        return [Geo.total_inner_i for Geo in self.Geometries]

    @property
    def total_outer(self):
        '''Return thicknesses of all outer layers.'''
        return [Geo.total_outer for Geo in self.Geometries]

    @property
    def snapshots(self):
        '''Return a list of DataFrames of laminate snapshots without theory
        applied.  Gives a quick view of the stack (as if p = 1).
        '''
        print('Accessing snapshot method.')
        return list(LM.Snapshot for LM in self.LaminateModels)

    @property
    def frames(self):
        '''Return a list of DataFrames of the LaminateModel object from the
        Laminate class.

        Examples
        --------
        >>> case1.frames
        [<LaminateModel object>]
        '''
        print('Accessing frames method.')
        return list(LM.LMFrame for LM in self.LaminateModels)

    @property
    def LMs(self):
        '''Return a list of the raw LaminateModel objects.'''
        return self.LaminateModels

    @property
    def size(self):
        '''Return number of a Laminates.'''
        return len(self.LaminateModels)

# =============================================================================
# UTILITY ---------------------------------------------------------------------
# =============================================================================
# Builds and handles multiple cases simultaneously

class Cases(ct.MutableMapping):
    '''Return a dict of Case objects.

    This is useful for situations requiring laminates with different geometries,
    thicknesses and ps.

    Characteristics:

    - if user-defined, tries to import `Defaults()` to simplify instantiations
    - dict-like storage and access of cases
    - iterable by values
    - sliceable; returns a selection of cases
    - subset selection methods of LaminateModels
    - set operations for subset selections

    Parameters
    ----------
    caselets : list
        Containing geometry strings, lists of geometry strings or cases
        (as of 0.4.4b3).
    load_params : dict; default None
        Passed-in geometric parameters if specified; else default is used.
    mat_props : dict; default None
        Passed-in materials parameters if specidfied; else default is used.
    ps : list of ints
        `p` values to be looped over; `p` sets the number of rows per DataFrame.
    model : str; default None
        Module name from which to auto-import `Defaults()``.
    verbose : bool; default False
        If True, print a list of Geometries.
    unique : bool; default False
        If True and given a series of intersecting `caselets` (specifically
        geometry strings), return unique geometries per `caselet`.
    combine : bool; default False
        Combines `caselets` into a single case. Convenience, complementary
        keyword to Case(separate=True).
    #defaults_path : str
        Custom path from which to import Defaults().

    Raises
    ------
    ImportError
        If default load parameters or materials properties cannot be set.
    TypeError
        If invalid caselet type detected or p is a non-integer.

    Examples
    --------
    Cases of different ps, accepting a list of geometry strings

    >>> from lamana.distributions import Cases
    >>> cases = Cases('dft.geo_inputs['5-ply'], ps=[2,3])
    >>> cases
    {0: <<class 'lamana.distributions.Case'> p=2, size=3>,
     1: <<class 'lamana.distributions.Case'> p=3, size=3>}

    Accepts a dict of listed geometry strings (precursors for caselets)

    >>> dict_caselets = {
        0: ['350-400-500',  '400-200-800', '200-200-1200',
            '200-100-1400', '100-100-1600', '100-200-1400'],
        1: ['400-550-100', '400-500-200', '400-450-300',
            '400-400-400', '400-350-500', '400-300-600'],
        2: ['400-400-400', '350-400-500', '300-400-600',
            '200-400-700', '200-400-800', '150-400-990'],
        3: ['100-700-400', '150-650-400', '200-600-400',
            '250-550-400', '300-400-500', '350-450-400'],
    }
    >>> cases = Cases(dict_caselets)
    >>> cases
    {0: <<class 'lamana.distributions.Case'> p=5, size=6>,
     1: <<class 'lamana.distributions.Case'> p=5, size=6>}
     2: <<class 'lamana.distributions.Case'> p=5, size=6>,}

    Cases instances are iterable by values (default)

    >>> for case in cases:
    ...    print(case.LMs)
    [<lamana LaminateModel object (400.0-[200.0]-800.0), p=2>,
     <lamana LaminateModel object (400.0-[200.0]-800.0), p=2>,
     <lamana LaminateModel object (400.0-[200.0]-400.0S), p=2>]
    [<lamana LaminateModel object (400.0-[200.0]-800.0), p=3>,
     <lamana LaminateModel object (400.0-[200.0]-800.0), p=3>,
     <lamana LaminateModel object (400.0-[200.0]-400.0S), p=3>]

    >>> (LM for case in cases for LM in case.LMs)
    <generator object>

    Notes
    -----
    - LM: `LaminateModel` object.
    - LaminateModel: DataFrames of laminate info; `Snapshot`, `LFrame`, `LMFrame`.
    - case: group of LMs with the same geometric, loading and material parameters.
    - cases: group of cases, particularly with a similar pattern of interest or
      different rows (`p`).
    - caselet: a subset of cases or LMs; geometry string, list or case (See LPEP 003)

    '''
    def __init__(
        self, caselets, load_params=None, mat_props=None, ps=None,
        model=None, verbose=False, unique=False, combine=False,
    ):
        #defaults_path=None
        self.ps = ps
        if model is None:
            self.model = 'Wilson_LT'
        else:
            self.model = model
        #self.defaults_path = defaults_path
        self.verbose = verbose

        # Auto import ; given a model, import defaults from models.<model_name>.Defaults()
        try:
            '''Implement passed in loction of custom models via default_path kw.'''
            modified_name = ''.join(['.', self.model])     # '.Wilson_LT'
            module = importlib.import_module(modified_name, package='lamana.models')
            dft = module.Defaults()                        # triggers handling parameters
        except (ImportError):
            print('User-defined Defaults not found.')

        # Try to set defaults from auto imports, else set whats passed in.
        if load_params is None:
            try:
                self.load_params = dft.load_params
            except (AssertionError):
                raise ImportError('models.Defaults() not found.  Assign load_params.')
        else:
            self.load_params = load_params
        if mat_props is None:
            try:
                self.mat_props = dft.mat_props
            except (AssertionError):
                raise ImportError('models.Defaults() not found.  Assign mat_props.')
        else:
            self.mat_props = mat_props

        # Setup caselets
        # Logic starts here, for defining the hashable class _dict_caselets.
        # Needs latter model, load_params and mat_props defined first
        # Combining caselets here is convenient if a pattern us already setup
        # rather than make a new make separate Case for each manually.
        '''Try to clean up with multiple exceptions rather than isinstance().'''
        if combine:
            '''DEV: deprecate post is_valid update for empty apply'''
            if not caselets:
                raise TypeError('combine=True: Invalid type detected for '
                                'caselets. Make list of geometry strings, '
                                'lists of geometry strings or cases.')
            try:
                # Assuming a list of geometry strings
                case_ = la.distributions.Case(self.load_params, self.mat_props)
                if unique:
                    case_.apply(caselets, unique=True)
                else:
                    case_.apply(caselets)
                self.caselets = [case_]
                # TODO: Brittle; need more robust try-except
            except(AttributeError, TypeError):             # raised from Geometry._to_gen_convention()
                try:
                    # if a list of lists
                    flattened_list = list(it.chain(*caselets))
                    # lists are needed for Cases to recognize separate caselets
                    # automatically makes a unique set
                    #print(caselets)
                    self.caselets = [self._get_unique(flattened_list)]
                    #print(self.caselets)
                except(TypeError):
                    # if a list of cases, extract LMs, else raise
                    flattened_list = [LM.Geometry.string for caselet in caselets
                                      for LM in caselet.LMs]
                    # list is needed for Cases to recognize as one caselet
                    # automatically makes a unique set
                    self.caselets = [self._get_unique(flattened_list)]
                    #print(self.caselets)
        elif unique and not combine:
            self.caselets = [self._get_unique(caselet) for caselet in caselets]
            #print(self.caselets)
        else:
            self.caselets = caselets

        # Build a dict of cases; and a separate case for each p.
        if self.ps is None:                                # ignore ps
            #
            iterable = self._convert_caselets(self.caselets)
            self._dict_caselets = dict((i, case) for i, case in iterable)
        else:                                              # Iterate ps
            list_ = []
            for p in ps:
                if isinstance(p, int):
                    self.load_params['p'] = p
                    iterable = self._convert_caselets(self.caselets)
                    list_cases = [case for i, case in iterable]
                else:
                    raise TypeError('Non-integer detected.  p must be an integer.')
                    '''Test raise exception if p is not int.'''
                list_.extend(list_cases)
            # Reorder dict
            self._dict_caselets = {i: case for i, case in enumerate(list_)}

    # Process caselets
    # Caselets as strings, lists, or cases
    def _convert_caselets(self, caselets_):
        '''Yield key-value pair of converted caselet string or list.

        Supports mixed types of caselets.
        '''
        for i, caselet_ in enumerate(caselets_):
            #print(type(caselet))
            if isinstance(caselet_, str):
                # '400-200-800' --> <case>
                case_ = self._get_case([caselet_])
            elif isinstance(caselet_, list) or isinstance(caselet_, set):
                # ['400-200-800', '400-400-400'] --> <case>
                # {'400-200-800', '400-400-400'} --> <case>
                case_ = self._get_case(caselet_)
            elif isinstance(caselet_, la.distributions.Case) and (self.ps is None):
                # case1 --> <case>
                case_ = caselet_
            elif isinstance(caselet_, la.distributions.Case) and self.ps:
                # case1 --> <case>; redo case
                geo_strings = [LM.Geometry.string for LM in caselet_.LMs]
                case_ = self._get_case(geo_strings)
            else:
                raise TypeError('Invalid type detected for caselets. '
                                'Make list of geometry strings, lists of '
                                'geometry strings or cases.')
            '''Test TypeError.'''
            yield i, case_

    def _get_case(self, caselet_):
        '''Return a case given a caselet.'''
        case_ = la.distributions.Case(self.load_params, self.mat_props)
        case_.apply(caselet_, model=self.model)
        return case_

    def _get_unique(self, caselet_):
        '''Return a set of unique geometry strings given a caselet.

        Notes
        -----
        Here think of `caselet` as geometry strings that make a separate plot.
        There is then only one type of `caselet` needed to make a set - a list
        - since a single geometry string is already unique and a we need the
        strings from a case.  Let's ignore these types then and focus on
        list of geometry strings.

        '''
        if isinstance(caselet_, str):
            print('Single geometry string detected. unique not applied.'
                  'See combine=True keyword.')
            return caselet_
        elif isinstance(caselet_, la.distributions.Case):
            # Extract the list of geometry strings from the case
            caselet_ = [LM.Geometry.string for LM in caselet_.LMs]

        # Given a list of geometry strings, convert them and set unique
        # ['400-200-800', '400-400-400', '400-[200]-800'] -->
        # {'400-[400]-400', '400-[200]-800'}
        converted_caselet_ = [la.input_.Geometry._to_gen_convention(geo_string)
                              for geo_string in caselet_]
        #print(set(converted_caselet_))
        return set(converted_caselet_)

    #TODO: Process dicts of caselets (See LPEP 003)
#     ### BETA
#     def _is_verbose(self, caselet, p):
#         '''Print verbose mode if True.'''
#         # Verbose printing
#         if self.verbose:
#             print('A new case was created. '
#                   '# of LaminateModels: {}, p: {}'.format(len(caselet), p))

        #print(self._dict_caselets)
        #print(self.__dict__)
        #print(self.load_params)
        #print(self.mat_props)

    def __setitem__(self, key, value):
        raise NotImplementedError('Reinstantiate Cases instead.')

    def __getitem__(self, key):
        if isinstance(key, slice):
            #print(key.start, key.stop, key.step)
            if key.step is None:
                step = 1
            slicedkeys = range(key.start, key.stop, step)
            return [self._dict_caselets[k] for k in slicedkeys]
        return self._dict_caselets[key]

    def __getslice__(self, i, j):                          # Python 2
        return self.__getitem__(slice(i, j))

    def __delitem__(self, key):
        del self._dict_caselets[key]

    def __iter__(self):
        return iter(self._dict_caselets.values())

    def __len__(self):
        return len(self._dict_caselets)

    def __eq__(self, other):
        '''Compare Cases.'''
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # The final two methods aren't required, but nice for demo purposes:
    def __str__(self):
        '''Return simple dict representation of the mapping.'''
        return str(self._dict_caselets)

    def __repr__(self):
        '''Echoes class, id, & reproducible representation in the REPL.'''
        return '{}, {}'.format(super(self.__class__, self).__repr__(),
                               self._dict_caselets)

    # API ---------------------------------------------------------------------
    def select(self, nplies=None, ps=None, how='union'):
        '''Return a set (subset) of LaminateModels given keyword conditions.

        Parameters
        ----------
        nplies : list; default None
            List or int of number of plies.
        ps : list; default None
            List or int of number of points/rows.
        how : str; default 'union'
            Use set operations union, difference, intersection, symmetric difference.

        Examples
        --------
        >>> list_ = dft.geos_dissimilar + dft.geos_symmetric
        >>> cases = Cases(geos=list_)
        >>> cases_selected = cases.select(name='7-ply')
        >>> cases_selected
        [Geometry object (400.0-[100.0, 100.0]-400.0S)]

        '''
        '''Add a verbose mode'''

        cases = self

        # Set defaults
        ##selected = []
        if nplies is None:
            nplies = []
        if ps is None:
            ps = []

        # Convert ints to iterables
        if isinstance(nplies, int):
            nplies = [nplies]
        if isinstance(ps, int):
            ps = [ps]

        LMs_by_ps = [LM for case in cases for LM in case.LMs if LM.p in ps]
        LMs_by_nplies = [LM for case in cases for LM in case.LMs if LM.nplies in nplies]
        #print(LMs_by_ps)
        #print(LMs_by_nplies)

        '''Figure how to naturalsort'''
        # Handle comparison logics
        if how.startswith('uni'):
            return set(LMs_by_ps).union(LMs_by_nplies)
        elif how.startswith('int'):
            return set(LMs_by_ps).intersection(LMs_by_nplies)
            '''Order of set is important here'''
        elif how.startswith('dif'):
            return set(LMs_by_ps).difference(LMs_by_nplies)
        elif how.startswith('sym'):
            return set(LMs_by_ps).symmetric_difference(LMs_by_nplies)

    def plot(self, halfplot=None, normalized=True, extrema=True, legend_on=True,
             colorblind=False, grayscale=False, subplots_kw=None,
             suptitle_kw=None, **kwargs):
        '''BETA (0.4.4b3): Plot caselets as subplots.

        Basic multiplotting. Defaults tensile halfplot for more than 2 caselets.
        See Case.plot for docstring.   Subtitles deprecated.

        Has a convenience function for plotting single plots.  Though
        encourages to use Case().

        See Also
        --------
        la.distributions.Case() : single plots

        '''
        caselets = self
        #caselets_ = cases_

        # A convenience option; Cases() should only plot multiple cases
        if len(caselets) == 1:
            #print(caselets)
            '''Add to warning'''
            '''Brittle kw passing if kwargs change; search for general alternative.'''
            print('One caselet detected.  The Cases() class is designed to plot '
                  'more than one case. Consider using the Case() class.')
            case = caselets[0]
            ax = case.plot(
                halfplot=halfplot, normalized=normalized, extrema=extrema,
                legend_on=legend_on, colorblind=colorblind, grayscale=grayscale,
                subplots_kw=subplots_kw, suptitle_kw=suptitle_kw, **kwargs
            )
            return ax

        # Set defaults for halfplots
        if halfplot is None:
            if len(caselets) > 2:
                halfplot = 'tensile'
            else:
                halfplot

        # Returns a full figure (not just an axes).
        # Uses internal code for suptitles.
        # Custom plt.text disallowed due to complexity, e.g. subtitles.
        '''Search for alternate keyword holders.'''
        la.output_._multiplot(caselets, halfplot=halfplot, normalized=normalized,
                              extrema=extrema, legend_on=legend_on,
                              colorblind=colorblind, grayscale=grayscale,
                              subplots_kw=subplots_kw, suptitle_kw=suptitle_kw,
                              **kwargs)

    def to_csv(self, path=None):
        '''Write all DataFrames to a path; output directory (default).'''
        if path is None:
            path = os.getcwd()                             # use for the test in the correct path
            path = path + r'\lamana\output'                # default

        for LM in self.LMs:
            ut.write_csv(LM, path=path, verbose=True)

    @property
    def LMs(self):
        '''Return a unified list of LaminateModels by processing all cases.'''
        cases = self                                       # since self iters values
        return list(LM for case in cases for LM in case.LMs)

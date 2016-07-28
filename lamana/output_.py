# -----------------------------------------------------------------------------
'''Classes and functions for handling visualizations, plots and exporting data. BETA'''
# _distribplot(): independent plots of single and multiple  geometries
# _multiplot(): aggregates severa; distribplots into a grid of subplots
# flake8 output_.py --ignore E265,E501,E701,F841,N802,N803,N806

'''Plot single and multiple LaminateModels.

Plots objects found within a list of LMs.  Assumes Laminate objects are
in the namespace.  Calls `_distribplot()` for single/multiple geometries.

Parameters
----------
title : str; default None
    Suptitle; convenience keyword
subtitle : str; default None
    Subtitle; convenience keyword.  Used ax.text().
x, y : str; default None
    DataFrame column names.  Users can manually pass in other columns names.
normalized : bool; default None
    If true, plots y = k_; else plots y = d_ unless specified otherwise.
halfplot : str; default None
    Trim the DataFrame to read either |'tensile'|'compressive'|None|.
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
{subplots, suptitle}_kw : dict; default None
    Default keywords are initialed to set up the distribution plots.
    - subplots: |ncols=1|figsize=(12,8)|dpi=300|
    - suptitle: |fontsize=15|fontweight='bold'|

Notes
-----
See `_distroplot()` for more kwargs. Here are some preferred idioms:

>>> case.LM.plot()                                # geometries in case
Case Plotted. Data Written. Image Saved.
>>> case.LM[4:-1].plot()                          # handle slicing
Case Plotted. Data Written. Image Saved.

Examples
--------

Plot Single Geometry
--------------------

Unnormalized stress distribution for single geometry (default):

.. plot::
    :context: close-figs

    >>> import lamana as la
    >>> from LamAma.models import Wilson_LT as wlt
    >>> dft = wlt.Defaults()
    >>> case = la.distributions.Case(dft.load_params, dft.mat_props)
    >>> case.apply('400-[200]-800')
    >>> case.plot()

Normalized stress distribution for single geometry:

.. plot::
    :context: close-figs

    >>> case.plot(normalized=True)

Normalized stress distribution (base) with an unnormalized inset:

.. plot::
   :context: close-figs

   >>> case.plot(inset=True)

Stress distribution plot with layer annotations:

.. plot::
    :context: close-figs

    >>> plot(annotate=True)

Custom markerstyles and kwarg passing.

.. plot::
    :context: close-figs

    >>> plot(markerstyles=['D'])

Colorblind-safe color palette.

.. plot::
    :context: close-figs

    >>> plot(colorblind=True)

Grayscale color palette.

.. plot::
    :context: close-figs

    >>> plot(grayscale=True)


Plot Multiple Geometries
------------------------

Normalized stress distributions for multiple geometries (default):

.. plot::
    :context: close-figs

    >>> case.apply('400-200-800', '350-400-500', '200-100-1400')
    >>> case.plot()

Tensile stress distribution:
.. plot::
    :context: close-figs

    >>> case.plot(halfplot='tensile')

Insets are not implemented for multiple geometries:

.. plot::
    :context: close-figs

    >>> case.plot(inset=True)
    NotImplementedError 'Unable to superimpose multiple, unnormalized plots.

See Also
--------
lamana.constructs.Laminate : builds the `LaminateModel` object.
lamana.output_._distribplot : generic handler for stress distribution plots.
lamana.output_._multiplot : plots multiple cases as subplots (caselets).
lamana.distributions.Case.plot : makes call to `_distribplot()`.
lamana.distributions.Cases.plot : makes call to `_multiplot()`.

'''


import os
import math
import tempfile
import logging
import itertools as it

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from . import input_
from .lt_exceptions import InputError
from .lt_exceptions import PlottingError
from .lt_exceptions import ExportError
from .utils import tools as ut
from .utils import config


# =============================================================================
# PLOTS -----------------------------------------------------------------------
# =============================================================================
# Process plotting figures of single and multiple subplots


#def _cycle_depth(iterable, n=None):
#    '''Return a cycler that iterates n items into an iterable.'''
#    if n is None:
#        n = len(iterable)
#    return it.cycle(it.islice(iterable, n))


def _cycle_depth(iterable, depth=None):
    '''Return an itertools.cycle that slices the iterable by a given depth.

    Parameters
    ----------
    iterable : iterable
        A container of infinite length.
    depth : int
        A index value; if None, cycle the entire iterable.

    Examples
    --------
    >>> # Depth:  1    2    3    4    5    6
    >>> iter_ = ['A', 'B', 'C', 'D', 'E', 'F']
    >>> _cycle_depth(iter_, depth=2)
    itertools.cycle                      # ['A', 'B', 'A', 'B', 'A' ...]

    >>> # Depth:  1    2    3    4    5    6
    >>> iter_ = ['A', 'B', 'C', 'D', 'E', 'F']
    >>> _cycle_depth(iter_, depth=3)
    itertools.cycle                      # ['A', 'B', 'C', 'A', 'B', 'C' ...]

    Returns
    -------
    itertools.cycle
        An infinite generator.

    '''
    if depth is None:
        depth = len(iterable)
    return it.cycle(it.islice(iterable, depth))


# TODO: Abstract to Distribplot and PanelPlot classes
def _distribplot(
    LMs, x=None, y=None, normalized=True, halfplot=None, extrema=True,
    legend_on=True, colorblind=False, grayscale=False, annotate=False, ax=None,
    linestyles=None, linecolors=None, markerstyles=None, layercolors=None,
    plot_kw=None, patch_kw=None, annotate_kw=None, legend_kw=None,
    sublabel_kw=None, **kwargs
):
    '''Return an axes plot of stress distributions.

    Some characteristics
        - multiplot: plot multiple geometries
        - halfplot: plots only compressive or tensile side
        - annotate: write layer type names
    Users can override kwargs normal mpl style.

    Parameters
    ----------
    LMs : list of LaminateModel objects
        Container for LaminateModels.
    x, y : str
        DataFrame column names.  Users can pass in other columns names.
    normalized : bool
        If true, plots y = k_; else plots y = d_ unless specified otherwise.
    halfplot : str
        Trim the DataFrame to read either |'tensile'|'compressive'|None|.
    extrema : bool
        Plot minima and maxima only; equivalent to p=2.
    legend_on : bool
        Turn on/off plot. Default: True.
    colorblind : bool
        Set line and marker colors as colorblind-safe.
    grayscale : bool
        Set everything to grayscale.  Overrides colorblind.
    annotate : bool
        Annotate names of layer types.
    ax : matplotlib axes
        An axes containing the plots.

    These keywords control general plotting aesthetics.
    {lines, marker, layer}_styles/colors : dict
        Processes cycled iterables for matplotlib keywords.
        - linestyles: ["-","--","-.",":"]
        - linecolors: LAMANA_PALETTES['bold']
        - markerstyles: mpl.lines.Line2D.filled_markers
        - layercolors: LAMANA_PALETTES['HAPSu']

    {plot, patch, annotate, legend, sublabel}_kw : dict
        Default keywords are initialized to set up the distribution plots.
        - plot: |linewidth=1.8|markersize=8|alpha=1.0|clip_on=False|
        - patch: |linewidth=1.0|alpha=0.15|
        - annotate: write layer types |fontsize=20|alpha=.7|ha='left'|va='center'|
        - legend: |loc=1|fontsize='large'|
        - sublabel: default is lower case alphabet
                   |x=0.12|y=0.94|s=''|fontsize=20|weight='bold'|ha='center'|va='center'|

    Returns
    -------
    matplotlib axes
        A plot of k or d (height) versus stress.

    Raises
    ------
    InputError
        If no stress column is found.
    PlottingError
        If multiple geometries try an unnormalized plot; cannot superimpose.

    Notes
    -----
    Since this function pulls from existing axes with `gca`, it is currently up
    to the coder to manage axes cleanup, particularly when making consecutive plot
    instances.  The following example uses the clear axes f(x) to remedy this issue:

    >>> # Plot consecutive instances
    >>> case = ut.laminator(['400-200-800'])[0]
    >>> LMs = case.LMs
    >>> plot1 = la.output_._distribplot(LMs, normalized=True)
    >>> plot1.cla()                                        # clear last plot, otherwise prevents infinite loop of gca from old plot
    >>> plot2 = la.output_._distribplot(LMs, normalized=False)

    If you want to keep your old axes, consider passing in a new axes.

    >>> fig, new_ax = plt.subplots()
    >>> plot3 = la.output_._distribplot(LMs, normalized=False, ax=new_ax)

    Examples
    --------
    >>> # Plot a single geometry
    >>> import lamana as la
    >>> from lamana.models import Wilson_LT as wlt
    >>> dft = wlt.Defaults()
    >>> case = la.distributions.Case(dft.load_params, dft.mat_props)
    >>> case.apply(['400-200-800'])
    >>> la.output_._distribplot(case.LMs)
    <matplotlib.axes._subplots.AxesSubplot>

    '''
    # -------------------------------------------------------------------------
    '''Make cyclers colorblind and grayscale friendly'''
    if ax is None:
        ax = plt.gca()

    # Default axis labels and DataFrame columns for normalized plots
    if x is None:
        # 'stress_f (MPa/N)' is in Wilson_LT; so the following triggers handling
        ##x = 'stress_f (MPa/N)'
        x = 'stress'

    if normalized:
        y = 'k'
    elif not normalized and y is None:
        y = 'd(m)'
    # NOTE: Will have trouble standardizing the name of the stress column.
    # NOTE: Need to de-hard-code x label since changes with model
    # TODO: Try looking for stress columns, and select last one, else look for strain.

    # see loop on handling stress column

    # Plot Defaults -----------------------------------------------------------
    # Set defaults for plotting keywords with dicts
    # If no kwd found, make an empty dict; only update keys not passed in
    plot_kw = {} if plot_kw is None else plot_kw
    plot_dft = dict(linewidth=1.8, markersize=8, alpha=1.0, clip_on=False,)
    plot_kw.update({k: v for k, v in plot_dft.items() if k not in plot_kw})
    #print('plot_kw (pre-loop): ', plot_kw)

    patch_kw = {} if patch_kw is None else patch_kw
    patch_dft = dict(linewidth=1.0, alpha=0.15,)
    patch_kw.update({k: v for k, v in patch_dft.items() if k not in patch_kw})
    #print('patch_kw: ', patch_kw)

    annotate_kw = {} if annotate_kw is None else annotate_kw
    annotate_dft = dict(fontsize=20, alpha=.7, ha='left', va='center',)
    annotate_kw.update({k: v for k, v in annotate_dft.items() if k not in annotate_kw})
    #print('annotate_kw: ', annotate_kw)

    legend_kw = {} if legend_kw is None else legend_kw
    legend_dft = dict(loc=1, fontsize='large',)
    legend_kw.update({k: v for k, v in legend_dft.items()
                      if k not in legend_kw and legend_on})
    #print('legend_kw: ', legend_kw)

    sublabel_kw = {} if sublabel_kw is None else sublabel_kw
    sublabel_dft = dict(
        x=0.12, y=0.94, s='', fontsize=20, weight='bold', ha='center',
        va='center', transform=ax.transAxes
    )
    sublabel_kw.update({k: v for k, v in sublabel_dft.items()
                        if k not in sublabel_kw})
    #print('sublabel_kw: ', sublabel_kw)

    # Style Cyclers -----------------------------------------------------------
    # Set defaults for the line/marker styles, colors and layer patch colors
    if linestyles is None:
        linestyles = it.cycle(["-", "--", "-.", ":"])
    if linecolors is None:
        linecolors = config.LAMANA_PALETTES['bold']
    if markerstyles is None:
        markerstyles = [mrk for mrk in mpl.lines.Line2D.filled_markers
                        if mrk not in ('None', None)]
    if layercolors is None:
        layercolors = config.LAMANA_PALETTES['HAPSu']
        ##layercolors = ['#E7940E', '#F5A9A9', '#FCEB00', '#0B4EA5']

    if colorblind:
        linecolors = config.LAMANA_PALETTES['colorblind']
        '''Add special color blind to layers'''
    if grayscale:
        linecolors = ['#000000']
        layercolors = reversed(config.LAMANA_PALETTES['grayscale'][:-1])     # exclude black
        patch_kw.update(dict(alpha=0.5))
        if colorblind:
            print('Grayscale has overriden the colorblind option.')

    marker_cycle = it.cycle(markerstyles)
    ##marker_cycle = it.cycle(reversed(markerstyles))
    line_cycle = it.cycle(linestyles)
    color_cycle = it.cycle(linecolors)

    # Plotting ----------------------------------------------------------------
    minX, maxX = (0, 0)
    for i, LM in enumerate(LMs):
        if extrema:
            df = LM.extrema                                        # plots p=2
        else:
            df = LM.LMFrame
        #nplies = LM.nplies                                         # unused
        materials = LM.materials
        lbl = LM.Geometry.string
        stack_order = LM.stack_order

        # Handle arbitrary name of x column by
        # selecting last 'stress' column; assumes 'stress_f (MPa)' for Wilson_LT
        # if none found, exception is raised. user should input x value
        #logging.debug('x: {}'.format(x))
        x_col = x
        y_col = y
        try:
            df[x_col]
        except KeyError:
            try:
                # Try to discern if input wants a stress column.
                stress_names = df.columns.str.startswith('stress')
                stress_cols = df.loc[:, stress_names]
                ##stress_cols = df.loc[stress_names]
                x_series = stress_cols.iloc[:, -1]
                x_col = x_series.name
                logging.info(
                    "Stress column '{}' not found."
                    " Using '{}' column.".format(x, x_col)
                )
            # TODO: unable to test without configuring model.  Make mock model for test.
            except KeyError:
                raise InputError(
                    "Stress column '{}' not found."
                    ' Specify `y` column in plot() method.'.format(x_col)
                )

        x_series, y_series = df[x_col], df[y_col]
        xs, ys = x_series.tolist(), y_series.tolist()

        # Update plot boundaries
        if min(xs) < minX:
            minX = float(min(xs))
        if max(xs) > maxX:
            maxX = float(max(xs))
        #print(minX, maxX)

        # Keyword Updates;
        # Use the cycler if plot_kw is empty, otherwise let the user manually change plot_kw
        plot_kw.update({
            'label': lbl,
            #'marker': 'o',
            #'color': 'b',
            'marker': next(marker_cycle),
            'color': next(color_cycle),
            'linestyle': next(line_cycle)
        })

        '''Put following into info.'''
        #print(LM.Geometry, LM.Geometry.string, LM.name, LM.nplies, LM.p)
        # Label caselets with sublabels, e.g. a,b,c, i,ii,iii...
        ax.tick_params(axis='x', pad=10)
        ax.tick_params(axis='y', pad=10)
        ax.plot(xs, ys, **plot_kw)

    width = maxX - minX                                            # sets rectangle width
    minY = y_series.min()
    maxY = y_series.max()

    # Smart-cycle layer colors list; slice iterable the length of materials
    # Draw layers only for # y = {k_ and d_(if nplies=1)}
    layer_cycle = _cycle_depth(layercolors, depth=len(materials))  # assumes all Cases materials equiv.

    # -------------------------------------------------------------------------
    # Annotations anchored to layers instead of plot; iterates layers
    incrementer = 0
    for layer_, (type_, t_, matl_) in stack_order.items():
        if normalized:
            ypos, thick = layer_, 1                                # thick is a unit thick (k-k_1)
        elif (not normalized and len(LMs) == 1):
            thick = t_ / 1e6
            ypos = incrementer
        else:
            raise PlottingError(
                'Unnormalized plots (i.e. y=d(m)) are visually cumbersome for'
                ' geometries > 1. Consider using the `normalized=True` keyword'
                ' for displaying simultaneous multi-geometry data.'
            )
            # NOTE: Replaced with raise in 0.4.11.dev0
            #'''Add this to warning.'''
            #print('CAUTION: Unnormalized plots (y=d(m)) are cumbersome for '
            #      'geometries > 1. Consider normalized=True for multi-geometry '
            #      'plots.')
            #return None

        patch_kw.update({'facecolor': next(layer_cycle)})          # adv. cyclers
        rect = mpl.patches.Rectangle((minX, ypos), width, thick, **patch_kw)
        ax.add_artist(rect)
        '''add these to a kw dict somehow..  preferably to annotate_kw'''
        xpad = 0.02
        ypad_layer = 0.15
        ypad_plot = 0.03

        if normalized:
            ypad = (rect.get_height() * ypad_layer)                # relative to layers
        elif not normalized:
            #print(ax.get_ylim()[1])
            ypad = ax.get_ylim()[1] * ypad_plot                    # relative to plot
            #print(ypad)
        rx, ry = rect.get_xy()
        cx = rx + (rect.get_width() * xpad)
        cy = ry + ypad

        if annotate:
            ax.annotate(type_, (cx, cy), **annotate_kw)
        incrementer += thick

    # -------------------------------------------------------------------------
    # Set plot limits
    #ax.axis([minX, maxX, minY, maxY])
    if halfplot is None:
        ax.axis([minX, maxX, minY, maxY])
    elif halfplot is not None:
        if halfplot.lower().startswith('comp'):
            ax.set_xlim([minX, 0.0])
            ax.set_ylim([minY, maxY])
            ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(5))
        else:                                                      # default tensile
            ax.set_xlim([0.0, maxX])
            ax.set_ylim([minY, maxY])
            ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(5))
#             '''Fix overlapping; no way to do automatically'''
#             major_ticks = np.arange(0.0, maxX, 0.1)
#             ax.set_xticks(major_ticks)

    # Set legend parameters and axes labels
    if legend_kw is not None and legend_on:
        ax.legend(**legend_kw)
    ax.text(**sublabel_kw)                                         # figure sublabel

    # TODO: Refactor for less limited parameter-setting of axes labels.
    axtitle = kwargs.get('label', '')
    xlabel = kwargs.get('xlabel', x)
    ylabel = kwargs.get('ylabel', y)

    ax.set_title(axtitle)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ##ax.xaxis.labelpad = 20
    ##ax.yaxis.labelpad = 20

    return ax


# TODO: Needs to return an axes or figure plot
# TODO: caselets are defined as containers of str, lists of str or cases, in LPEP 003.
# Here caseslets are an LM, LMs or cases; list of cases(?) or cases object.
def _multiplot(
    caselets, x=None, y=None, title=None, normalized=True, extrema=False,
    halfplot='tensile', colorblind=False, grayscale=False, annotate=False,
    labels_off=False, suptitle_kw=None, subplots_kw=None, patch_kw=None,
    plot_kw=None, legend_kw=None, labels_kw=None, **kwargs
):
    '''Return figure of axes containing several plots.

    Characteristics:

    - multiple plots
    - kwarg/arg passing
    - global labels and titles
    - delete remaining subplots if less than remaining axes.

    Parameters
    ----------
    caselets : LM, LMs or cases
        Should be a container of str, lists of str or cases; however, accepting
        LM, LMs or cases.  Refactoring required.
    x, y : str
        DataFrame column names.  Users can pass in other columns names.
    title : str
        Figure title.
    normalized : bool
        If true, plots y = k_; else plots y = d_ unless specified otherwise.
    extrema : bool, default: False
        Plot minima and maxima only; equivalent to p=2.
        Forced off for clarity in separate plots.
    halfplot : str
        Trim the DataFrame to read either |'tensile'|'compressive'|None|.
    colorblind : bool
        Set line and marker colors as colorblind-safe.
    grayscale : bool
        Set everything to grayscale.  Overrides colorblind.
    annotate : bool
        Annotate names of layer types.
    labels_off : bool
        Toggle labels.
    labels_kw : dict
        One stop for custom labels and annotated text passed in from user.
        axestitle, sublabels, legendtitles are lists of labels for each caselet.


    These keywords control general plotting aesthetics.
    {subplot, patch, plot, legend, suptitle}_kw : dict
        Default keywords are initialized to set up the distribution plots.
        - subplots: |ncols=4|
        - patch: None
        - plot: |clip_on=True|
        - legend: |loc=1|fontsize='small'|
        - suptitle: |t=''|fontsize=22|fontweight='bold'|

    Returns
    -------
    matplotlib figure
        A figure of subplots.

    Examples
    --------
    >>> # Plot a set of caselets (subplots)
    >>> import lamana as la
    >>> from lamana.models import Wilson_LT as wlt
    >>> dft = wlt.Defaults()
    >>> const_total = ['350-400-500', '400-200-800']
    >>> cases = la.distributions.Cases(
    ...     const_total, load_params=dft.load_params, mat_props=dft.mat_props,
    ...     model='Wilson_LT', ps=[2, 3]
    ... )
    >>> la.output_._multiplot(cases)

    '''
    # DEFAULTS ----------------------------------------------------------------
    title = '' if title is None else title

    if labels_off:
        kwargs['xlabel'], kwargs['ylabel'] = ('', '')              # turn off axes labels

    subplots_kw = {} if subplots_kw is None else subplots_kw
    subplots_dft = dict(ncols=4)
    subplots_kw.update({k: v for k, v in subplots_dft.items() if k not in subplots_kw})
    #print('subplots_kw: ', subplots_kw)

    patch_kw = {} if patch_kw is None else patch_kw
    #print('patch_kw: ', patch_kw)

    plot_kw = {} if plot_kw is None else plot_kw
    plot_dft = dict(clip_on=True)                                  # needed in halfplots; else BUG
    plot_kw.update({k: v for k, v in plot_dft.items() if k not in plot_kw})
    #print('plot_kw: ', plot_kw)

    legend_kw = {} if legend_kw is None else legend_kw
    legend_dft = dict(loc=1, fontsize='small')
    legend_kw.update({k: v for k, v in legend_dft.items() if k not in legend_kw})
    #print('legend_kw: ', legend_kw)

    suptitle_kw = {} if suptitle_kw is None else suptitle_kw
    suptitle_dft = dict(t='', fontsize=22, fontweight='bold')
    if title:
        suptitle_dft.update(dict(t=title))
    suptitle_kw.update({k: v for k, v in suptitle_dft.items() if k not in suptitle_kw})
    #print('suptitle_kw: ', suptitle_kw)

    # Main dict to handle all text
    # sublabels defaults to no labels after letter 'z'.
    # Will auto label subplots from a to z.  Afterwhich, the user must supply labels.
    labels_kw = {} if labels_kw is None else labels_kw
    alphabet = map(chr, range(97, 123))                            # to label subplots; REF 037
    labels_dft = dict(suptitle=None, sublabels=list(alphabet),
                      axes_titles=None, legend_titles=None,)
    if title:
        labels_dft.update(suptitle=title)                    # compliment convenience kw arg
    labels_kw.update({k: v for k, v in labels_dft.items() if k not in labels_kw})
    if labels_kw['suptitle']:
        suptitle_kw.update(t=labels_kw['suptitle'])
#    if labels_kw['subtitle']: subtitle=labels_kw['subtitle']
#     if labels_kw['xlabel']: kwargs['xlabel'] = ''                # remove axlabels; use text()
#     if labels_kw['ylabel']: kwargs['ylabel'] = ''                # remove axlabels; use text()
    #print('labels_kw: ', labels_kw)

    '''Consider cycling linecolors for each single geo, multiplot.'''

    # FIGURE ------------------------------------------------------------------
    # Reset figure dimensions
    ncaselets = len(caselets)
    ncols_dft = subplots_kw['ncols']
    nrows = int(math.ceil(ncaselets / ncols_dft))          # Fix "can't mult. seq. by non-int..." error; nrows should always be int
    ##nrows = math.ceil(ncaselets / ncols_dft)
    subplots_kw['figsize'] = (24, 8 * nrows)
    if ncaselets < ncols_dft:
        ncols_dft = ncaselets
        subplots_kw['ncols'] = ncaselets

    # Set defaults for lists of titles/labels
    for key in ['axes_titles', 'legend_titles', 'sublabels']:
        if labels_kw[key] is None:
            labels_kw[key] = [''] * ncaselets
    if ncaselets > len(labels_kw['sublabels']):
        labels_kw['sublabels'] = [' '] * ncaselets
        print('There are more cases than sublabels.  Bypassing default... '
              "Consider adding custom labels to 'axestext_kw'.")

    fig, axes = plt.subplots(nrows=nrows, **subplots_kw)
    #print('args: {}'.format(args))
    #print('kwargs:{} '.format(kwargs))
    #print('nrows: {}, ncols: {}'.format(nrows, ncols_dft))

    # NOTE: does not return ax.  Fix?
    def plot_caselets(i, ax):
        '''Iterate axes of the subplots; apply a small plot ("caselet").

        Caselets could contain cases (iterable) or LaminateModels (not iterable).

        '''
        try:
            caselet, axtitle, ltitle, sublabel = (
                caselets[i],
                labels_kw['axes_titles'][i],
                labels_kw['legend_titles'][i],
                labels_kw['sublabels'][i]
            )
            # Plot LMs on each axes per case (and legend notes if there)
            #print(ltitle, axsub)
            kwargs.update(label=axtitle)
            legend_kw.update(title=ltitle)
            sublabel_kw = dict(s=sublabel)


            # TODO: Refactor
            # Caselet could be a case or LM, but distribplot needs a list of LMs
            try:
                # Case
                LMs = caselet.LMs
            except (AttributeError):
                # Single LaminateModel
                LMs = [caselet]
                #print('Exception was caught; not a case')
                # NOTE: what about LMs?

            _distribplot(
                LMs, x=x, y=y, halfplot=halfplot, extrema=extrema, annotate=annotate,
                normalized=normalized, ax=ax, colorblind=colorblind,
                grayscale=grayscale, plot_kw=plot_kw, patch_kw=patch_kw,
                legend_kw=legend_kw, sublabel_kw=sublabel_kw, **kwargs
            )
        except(IndexError, KeyError):
            # Cleanup; remove the remaining plots
            fig.delaxes(ax)

    def iter_vector():
        '''Return axes for nrow=1; uses single loop.'''
        for i, ax in enumerate(axes):
            plot_caselets(i, ax)

    def iter_matrix():
        '''Return axes for nrow>1; uses nested loop.'''
        i = 0
        for ax_row in axes:
            for ax in ax_row:
                plot_caselets(i, ax)
                i += 1

    if nrows == 1:
        iter_vector()
    else:
        iter_matrix()

    # Common Figure Labels
    fig.suptitle(**suptitle_kw)
    plt.rcParams.update({'font.size': 18})

    # NOTE: Add a figure return and show deprecation in 0.4.11.dev0
    return fig
    #plt.show()


# -----------------------------------------------------------------------------
# AXES-LEVEL ------------------------------------------------------------------
# -----------------------------------------------------------------------------
class AxesPlot():
    '''Return a matplotblib axes.

    See Also
    --------
    - _distribplot()
    - singleplot()
    - halfplot()
    - quarterplot()
    - predictplot()

    '''
    pass


# -----------------------------------------------------------------------------
# FIGURE-LEVEL ----------------------------------------------------------------
# -----------------------------------------------------------------------------
class FigurePlot():
    '''Return a matplotlib figure.

    This class sets up a figure to accept data for multiple plots.


    Attributes
    -----------
    nrows, ncols = int, int
        Figure rows and columns.

    Notes
    -----
    Each subplot is a separate axes.

    See Also
    --------
    - _multiplot()
    - ratioplot()

    '''
    #figsize = (ncols * size * aspect, nrows * size)
    pass

# NOTE: Transferred from tools.utils in 0.4.13-dev
def export(L_, overwrite=False, prefix=None, suffix=None, order=None,
           offset=3, dirpath=None, temp=False, keepname=True, delete=False):
    '''Write LaminateModels and FeatureInput to files; return a tuple of paths.

    Supported formats:
    - .csv: two files; separate data and dashboard files
    - .xlsx: one file; data and dashboard sheets

    Parameters
    ----------
    L_ : Laminate-like object
        Laminate or subclass containing attributes and calculations.
    overwrite : bool; default False
        Save over files with the same name.  Prevents file incrementation
        and excess files after cyclic calls.
    prefix : str; default None
        Prepend a prefix to the filename.  Conventions are:
        - '' : legacy or new
        - 'w': written by the package
        - 't': temporary file; used when tempfile is renamed
        - 'r': redone; altered from legacy
        - 'dash': dashboard
    suffix : |'.csv'|'.xlsx'|
        Determines the file format by appending to filename; default '.xlsx'.
    order: list
        Keys of the FeatureInput.
    offset : int
        Blank columns between data in the dashboard.
    dirpath : str, optional; default "/export" directory
        Directory path to store resulting csv files; custom path NotImplemented.
    temp : bool, default False
        Make temporary files in the OS Temp directory instead.
    keepname : bool, True
        Toggle renaming temporary files; temp must be True.
    delete : bool, default False
        Force file removal after created; mainly used for temporary files.

    Returns
    -------
    tuple
        Full file paths (str) of the created files LM and dashboard data.

    See Also
    --------
    - get_path(): deals with munging paths and validations
    - convert_featureinput(): convert dict values to DataFrames
    - reorder_featureinput(): make and ordered list for the dashboard
    - make_tempfile(): review how Python 'mkstemp' makes temp; NotImplemented
    - rename_tempfile(): rename the file post closing file.

    Notes
    -----
    Contents are written into an "/export" directory. FeatureInput data a.k.a "dashboard".
    We use mkstemp (low-level), which leaves it open for to_excel to write.
    Here are technical characteristics:
    - OK  Outputs different file formats.
    - OK  Writes regular or temporary files (get auto-deleted by the OS; for tests)
    - OK  Calls helper functions to clean paths and datastructures.
    - OK  Allows prefixing for file indentification.
    - OK  Outputs data and dashboards.
    - OK  Works even when files exist in the directory.
    - OK  Auto creates "\export" directory if none exists.
    - OK  Renames temporary files by default.
    - OK  Support Laminate and LaminateModel objects
    - X   Supports custom directory paths.

    Examples
    --------
    >>> import lamana as la
    >>> case = la.distributions.laminator('400.0-[200.0]-800.0')[0]
    >>> LM = case.LMs[0]
    >>> export(LM)
    '~/lamana/export/laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.xlsx'

    >>> # Overwrite Protection
    >>> export(LM, overwrite=False)
    '~/lamana/export/laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0(1).xlsx'

    >>> # Optional .csv Format
    >>> export(LM, suffix='.csv')
    '~/lamana/export/dash_laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'
    '~/lamana/export/laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'

    >>> # Optional Temporary Files
    >>> export(LM, suffix='.csv', temp=True)
    'temp/t_dash_laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'
    'temp/t_laminatemodel_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'

    >>> # Supports Laminate objects too
    >>> from lamana.models import Wilson_LT as wlt
    >>> dft = wlt.Defaults()
    >>> L = la.constructs.Laminate(dft.FeatureInput)
    >>> export(L)
    '~/lamana/export/dash_laminate_5ply_p5_t2.0_400.0-[200.0]-800.0.xlsx'

    '''
    # Parse for Filename ------------------------------------------------------
    nplies = L_.nplies
    p = L_.p
    # TODO: Fix units
    t_total = L_.total * 1e3                               # (in mm)
    geo_string = L_.Geometry.string
    FI = L_.FeatureInput

    # Path Munge --------------------------------------------------------------
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = config.EXTENSIONS[1]                      # .xlsx

    if dirpath is None:
        ###
        # Prepend files with 'w' for "written" by the package
        # NOTE: removed default w_ prefix; check the control and other uses to maintain coding
        # TODO: rename legacy files with "l_"
        ###
        if hasattr(L_, 'LMFrame'):
            kind = 'laminatemodel'
        else:
            kind = 'laminate'
        filename = r'{}{}_{}ply_p{}_t{:.1f}_{}'.format(
            prefix, kind, nplies, p, t_total, geo_string)

        # Force-create export directory or path (REF 047)
        # Send file to export directory
        defaultpath = ut.get_path()
        if not os.path.exists(defaultpath):
            # TODO: Make sure this log prints out
            logging.info(
                'No default export directory found.  Making directory {} ...'.format(defaultpath)
            )
            os.makedirs(defaultpath)
    else:
        raise NotImplementedError('Custom directory paths are not yet implemented.')

    # Prepare FeatureInput ----------------------------------------------------
    if order is None:
        order = ['Geometry', 'Model', 'Materials',
                 'Parameters', 'Globals', 'Properties']    # default
    converted_FI = input_.convert_featureinput(FI)
    reordered_FI = ut.reorder_featureinput(converted_FI, order)  # elevates strings
    dash_df = pd.concat(converted_FI)                       # combines all dfs into one
    data_df = L_._frame

    # Assemble ----------------------------------------------------------------
    # Build csv data and dashboard (as optional temporary file)
    if not suffix.endswith('xlsx'):
        try:
            # Tempfiles are used to obviate writing to package folders
            if temp:
                data_des, data_filepath = tempfile.mkstemp(suffix=suffix)
                dash_des, dash_filepath = tempfile.mkstemp(suffix=suffix)
            else:
                data_filepath = ut.get_path(
                    filename, suffix=suffix, overwrite=overwrite
                )                                          # pragma: no cover
                dash_filepath = ut.get_path(
                    filename, suffix=suffix, overwrite=overwrite, dashboard=True
                )                                          # pragma: no cover

            # Write File
            data_df.to_csv(data_filepath)
            dash_df.to_csv(dash_filepath)

            # Tempfile Options
            if temp:
                os.close(data_des)
                os.close(dash_des)

            if temp and keepname:
                data_filepath = ut.rename_tempfile(
                    data_filepath, ''.join(['t_', filename, suffix]))
                dash_filepath = ut.rename_tempfile(
                    dash_filepath, ''.join(['t_', 'dash_', filename, suffix]))

            logging.info('DataFrame written as {} file in: {}'.format(suffix, data_filepath))
            logging.info('Dashboard written as {} file in: {}'.format(suffix, dash_filepath))
        except (NameError) as e:
            raise ExportError('Export failed.  {}'.format(e))
        finally:
            if delete:
                os.remove(data_filepath)
                os.remove(dash_filepath)
                logging.info('File has been deleted: {}'.format(data_filepath))
                logging.info('File has been deleted: {}'.format(dash_filepath))
            pass
        return (data_filepath, dash_filepath)

    # For Excel Files Only
    elif suffix.endswith('xlsx'):
        try:
            # Tempfiles are used to obviate writing to package folders
            if temp:
                data_des, workbook_filepath = tempfile.mkstemp(suffix=suffix)
            else:
                workbook_filepath = ut.get_path(
                    filename, suffix=suffix, overwrite=overwrite
                )                                          # pragma: no cover

            # Excel worksheet code block --------------------------------------
            writer = pd.ExcelWriter(workbook_filepath)

            # Data sheet
            sheetname = geo_string.replace('[', '|').replace(']', '|')
            data_sheetname = ' '.join(['Data', sheetname])
            data_df.to_excel(writer, data_sheetname)

            # Dashboard sheet
            dash_sheetname = ' '.join(['Dash', sheetname])

            for i, dict_df in enumerate(reordered_FI.values()):
                if dict_df.size == 1:                      # assumes string strs are ordered first
                    dict_df.to_excel(writer, dash_sheetname, startrow=4**i)
                else:
                    dict_df.to_excel(writer, dash_sheetname, startcol=(i-1)*offset)

            writer.save()

            if temp:
                os.close(data_des)

            if temp and keepname:
                workbook_filepath = ut.rename_tempfile(
                    workbook_filepath, ''.join(['t_', filename, suffix]))

            logging.info('Data and dashboard written as {} file in: {}'.format(suffix, workbook_filepath))
            print(workbook_filepath, "second time")
        except (NameError) as e:
            raise ExportError('Export failed.  {}'.format(e))
        finally:
            if delete:
                os.remove(workbook_filepath)
                logging.info('File has been deleted: {}'.format(workbook_filepath))
            pass

        return (workbook_filepath,)

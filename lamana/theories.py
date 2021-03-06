# -----------------------------------------------------------------------------
'''A interface between constructs and models modules.'''
# BaseModel(): A super class for user-customized models.
# flake8 constructs.py --ignore=E265,E501,N802,H806

import abc
import importlib
import logging

import six

# TODO: Replace with interactive way to import models
from lamana.models import *
##import lamana.models
from lamana.utils import tools as ut


@six.add_metaclass(abc.ABCMeta)
class BaseModel(object):
    '''Provide attributes for sub-classing custom models.

    Sub-class from here to make a model that interfaces with LamAna.

    Notes
    -----
    This class helps centralize common attributes associated with a custom
    model.  A model is selected in by the `Case.apply()` method and is applied in
    Phase 3 of `constructs.Laminate()`.  It is idiomatic to subclass `BaseModel`
    when making custom models.

    Uses an abstractmethod to enforce implementation of a hook method.  It also
    suggests that BaseModel can only be sub-classed, not instantiated.

    See Also
    --------
    distributions.Case.apply(): model selection
    constructs.Laminate(): creates LMFrame by merging LT data with LFrame
    theories.handshake(): get updated DataFrame and FeatureInput

    '''
    def __init__(self):
        super(BaseModel, self).__init__()
        self.model_name = None
        self.LaminateModel = None
        self.FeatureInput = None

    def __repr__(self):
        return '<{} Model object>'.format(self.__class__.__name__)

    # TODO: Find `_use_model_` more dynamically than forcing to search `Model._use_model`.
    @abc.abstractmethod
    def _use_model_():
        '''Hook method.

        Same name as config.HOOKNAME. This method must be implemented and
        return the following.

        Returns
        -------
        tuple
            Updated (DataFrame, FeatureInput).

        '''
        pass                                               # pragma: no cover


def handshake(precursor, adjusted_z=False):
    '''Return an updated LaminateModel and FeatureInput objects.

    This key method interfaces between Laminate class and a custom model module.
    Model names are related to the laminate theory, e.g. Classical_LT, Wilson_LT.
    This name is applied by the user upon calling `Case.apply(model='model_name')`
    and is found in the FeatureInput dict.

    Parameters
    ----------
    precursor : LaminateModel object
        A pre-updated `LaminateModel` object is passed in, giving access
        to the parent `Laminate` class.  The `Laminate.LFrame` only has ID and
        Dimensional columns, so no laminate theory calculations or columns are
        populated yet.  This DataFrame is updated and applied to the current
        `LaminateModel` object.
    adjusted_z : bool, optional; default False
        This option forces the use of the z(m)* column values.  A different
        algorithm was used it calculate the internal values for this variable.

    Notes
    -----
    This function searches for a special hook method named `_use_model_` in the
    specified model module.  The hook may be written as method within a class
    or written as an independent function offering a choice for users to write
    models in either class-style (recommended) or function-style.  This hook
    method simply returns an updated LaminateModel and FeatureInput.

    `handshake()` determines either class- or function-style models by duck typing
    a module name according to the model name provided in the `Case.apply()`` method.
    These modules are located in the `models` directory - a repository for all
    package models.  Assuming a function first, the hook method is sought by
    calling `_use_model_()`; if none is found, the exception is caught and a hook
    method named `<class>._use_model_` is sought next (as of 0.4.5b1).  As of
    0.4.11, hardcoded class names here removed; any pythonic name can be used
    for the <class> parameter.

    Here is the workflow of a model selected by the user and its call in `Laminate`.
    This assumes the model is developed and located in the standard .\models directory.

    1. User selects a model in `lamana.distributions.Case.apply(model='model_name')`;
       Model name is stored in the FeatureInput object then passed into
       `lamana.constructs.LaminateModel`.
    2. `LaminateModel` inherits from `Laminate` and `Stack` that build
       DataFrames with dimensional data.  The LMFrame attr is initially None.
    3. `theories.handshake()` is called and searches for the model name in models dir.
    4. Inside the selected model, the hook method `models._use_model_` is called
       (if function-style) or `models.<model_name>._use_model_` (if class-style)
    5. The a `LaminateModel.LMFrame` object is either updated or raises an error.

    '''
    HOOKNAME = '_use_model_'                               # looks for this in custom models

    # Find and Import the Model
    model_name = precursor.FeatureInput['Model']
    modified_name = ''.join(['.', model_name])             # e.g '.Wilson_LT'
    module = importlib.import_module(modified_name, package='lamana.models')

    # TODO: add assertion for presursor.LMFrame == Laminate(FI).LMFrame prior to update
    try:
        # Look for a hook function
        hook = ut.get_hook_function(module, hookname=HOOKNAME)
        logging.debug('Found a hook function: {}'.format(hook))
    except(AttributeError):
        # This code block obviates hardcoding a specific model class name.
        # Look for a class containing the hook method
        class_obj = ut.get_hook_class(module, hookname=HOOKNAME)
        class_name = getattr(module, class_obj.__name__)
        my_instance = class_name()                         # instantiate the class; important
        hook = getattr(my_instance, HOOKNAME)              # hook method
        logging.debug('Found a hook method {} in {}'.format(hook, class_name))

    # TODO: Try adding ModelError back in here
    # TODO: Add following with args
    #LaminateModel, FeatureInput = hook(Laminate, *args, adjusted_z=False, **kwargs)
    # eqiv. LM, FI = module._use_model_()
    LaminateModel, FeatureInput = hook(precursor, adjusted_z=False)

    # Make sure the passed FeatureInput has Equal attributes
    ##assert FeatureInput['Parameters']['p'] == Laminate.p

    return(LaminateModel, FeatureInput)

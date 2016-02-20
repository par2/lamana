# -----------------------------------------------------------------------------
'''A interface between constructs and models modules.'''
# BaseModel(): A super class for user-customized models.
# flake8 constructs.py --ignore=E265,E501,N802,H806

import importlib

# TODO: Replace with interactive way to import models
from lamana.models import *


class BaseModel(object):
    '''Provide attributes for sub-classing custom models.

    Notes
    -----
    This class helps centralize common attributes associated with a custom
    model.  A model is selected in `distributions.apply()` and returned in
    Phase 3 of `constructs.Laminate()`.  It is idiomatic to subclass `BaseModel`
    when making custom models.

    See Also
    --------
    distributions.apply(): model selection
    constructs.Laminate(): creates LMFrame by merging LT data with LFrame
    theories.handshake(): get updated DataFrame and FeatureInput

    '''
    def __init__(self):
        super(BaseModel, self).__init__()
        '''Change model_name to name.'''
        self.model_name = None
        self.LaminateModel = None
        self.FeatureInput = None

    def __repr__(self):
        return '<{} object>'.format(self.__class__.__name__)


# TODO: Find `_use_model_` more dynamically than forcing to search `Model._use_model`.
#Try to add as a class attribute that comes by subclassing BaseModel.


def handshake(Laminate, adjusted_z=False):
    '''Return updated LaminateModel and FeatureInput objects.

    This key method interfaces between Laminate class and a custom model module.
    Model names are related to the laminate theory, e.g. Classical_LT, Wilson_LT.
    This name is applied by the user upon calling `Case.apply(model='model_name')`
    and is found in the FeatureInput dict.

    Parameters
    ----------
    Laminate : Laminate object
        The entire `Laminate` object is passed in, giving access to its methods.
        `Laminate.LFrame` only has ID and Dimensional columns, so no laminate
        theory calculations or columns are populated yet.
    adjusted_z : bool, optional; default False
        This option forces the use of the z(m)* column values.  A different
        algorithm was used it calculate the internal values for this variable.

    Notes
    -----
    This method searches for a special hook method named `_use_model_` in the
    specified model module.  This hook may be written as method within a class
    or written as an independent function offering a choice for users to write
    models in either class-style (recommended) or function style.  This method
    simply returns an updated LaminateModel and FeatureInput.

    `handshake()` determines which style by duck typing the module with the provided
    name located in the `models` directory - a repository for all standard models.
    Assuming a function first, the hook is sought by invoking `_use_model_()`;
    if none is found, the exception is caught and a hook named `Model._use_model_`
    is sought next (as of 0.4.5b1).

    Here is the workflow of a model selected by the user and its call in `Laminate`.
    This assumes the model is developed and located in the standard models directory.

    1. User selects a model in `lamana.distributions.Case.apply(model='model_name')`;
       Model name is stored in the FeatureInput object, passed into `Laminate`.
    2. Inside `lamana.constructs.Laminate`,  _update_columns._update_calculations(FI)`
       is called, which initiates LT calculations for the given model.
    3. `theories.handshake(L)` is called and searches for the model name in models dir.
    4. Inside the selected model, the hook method `models._use_model_` is called
       (if function-style) or `models.<model_name>._use_model_` (if class-style)

    '''
    # Find and Import the Model
    model_name = Laminate.FeatureInput['Model']
    modified_name = ''.join(['.', model_name])                      # '.Wilson_LT'
    module = importlib.import_module(modified_name, package='lamana.models')

    try:
        # Look for the function
        '''Set up to accept *args'''
        '''Just need to update LM and FI.  '''
        LaminateModel, FeatureInput = module._use_model_(Laminate, adjusted_z=False)
        #print('Found a function')
    except(AttributeError):
        # Catch exceptions, if no function found, find class
        '''Make smarter to find whatever class has the _use_model hook.'''
        class_name = getattr(module, 'Model')
        my_instance = class_name()
        LaminateModel, FeatureInput = my_instance._use_model_(Laminate, adjusted_z=False)
        #print('Found a class')

    # Make sure the passed FeatureInput has Equal attributes
    assert FeatureInput['Parameters']['p'] == Laminate.p

    return(LaminateModel, FeatureInput)

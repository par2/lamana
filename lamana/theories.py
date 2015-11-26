# -----------------------------------------------------------------------------
# An interface between constructs and models modules
# BaseModel() : A super class for user-customized models.
# flake8 constructs.py --ignore=E265,E501,N802,H806

import importlib

'''Replace with interactive way to import models'''
from lamana.models import *


class BaseModel(object):
    '''Provide attributes for subclassing custom models.

    This class helps centralize common attributes associated with a selected
    model.  Intermeadiate users are encourages to sub-class from here to unify
    the API idioms.  Model is selected in distributions.apply() and returned in
    Phase 3 of constructs.Laminate().

    See Also
    ========
    - distributions.apply(): model selection
    - constructs.Laminate(): creates LMFrame by merging LT data with LFrame
    - theories.handshake(): get updated DataFrame and FeatureInput

    '''
    def __init__(self):
        super(BaseModel, self).__init__()
        '''Change model_name to name.'''
        self.model_name = None
        self.LaminateModel = None
        self.FeatureInput = None

    def __repr__(self):
        return '<{} object>'.format(self.__class__.__name__)

'''Need to find _use_model_ more dynamically than forcing to search Model._use_model.
Try to add as a class attribute that comes by subclassing BaseModel.
'''


def handshake(Laminate, adjusted_z=False):
    '''Return updated LaminateModel and FeatureInput objects.

    This key method interfaces between Laminate ::class:: and custom models ::module::.
    Modules are named by the type of laminate theory, e.g. Classical_LT, Wilson_LT.
    This name is applied by the user upon calling Case.apply() and is found in
    the FeatureInput dict.

    This method searches for a special hook method named `_use_model_` in the
    specified model module.  This hook may be written as method within a class
    or written as an independent function offering a choice for users to write
    models in either class-style (recommended) or function style.

    handshake() determine which style by duck typing the module with the provided
    name located in the `models` directory - a repository for all models.
    Assuming a function first, the hook is sought by invoking _use_model_();
    if none is found, the exception is caught and a hook named Model._use_model_
    is sought next (as of 0.4.5b1).

    Variables
    =========
    Laminate : the psudeo LaminateModels object (not yet updated)
        The entire Laminate ::object:: is passed in for access to all methods.
        Laminate.LFrame only has ID and Dimensional columns, so no Laminate
        Theory calculations or columns are present yet.

    Workflow
    ========

    `.constructs.Laminate._update_columns._update_calculations()` -->
     --> `.theories.Model.handshake()` -->  `.models.<model_name>`
     --> `_use_model` (if function) or Model._use_function (if class)

    '''
    # Find and Import the Model
    model_name = Laminate.FeatureInput['Model']
    modified_name = ''.join(['.', model_name])                      # '.Wilson_LT'
    module = importlib.import_module(modified_name, package='lamana.models')

    try:
        # Look for the function
        '''Set up to accept *args'''
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

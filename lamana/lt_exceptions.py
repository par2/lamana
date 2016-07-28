# -----------------------------------------------------------------------------
'''General classes for a custom exceptions.'''


class Error(Exception):
    pass


class FormatError(Error):
    '''Associated with geo_string formatting.'''
    pass


#class ValidationError(Error):
#    '''Associate with invalid, impossible geo_strings.'''
#    pass


#class KeyError(Error):
#    pass


class InputError(Error):
    '''Associated with invalid user inputs.'''
    pass


class NotImplementedError(Error):
    pass


class IndeterminateError(Error):
    '''Associated with INDET exceptions.

    See Also
    --------
    - "More on IndeterminateError" in the documentation.

    '''
    pass


class PlottingError(Error):
    '''Associated with plotting errors.'''
    pass


class ExportError(Error):
    '''Associated with export errors.'''
    pass


class ModelError(Error):
    '''Associated with model exceptions.'''
    # TODO: Consider replacing Attribute Error in hook tools and theories.handshake
    pass

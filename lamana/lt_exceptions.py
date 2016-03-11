# -----------------------------------------------------------------------------
'''General classes for a custom exceptions.'''


class Error(Exception):
    pass


class FormatError(Error):
    '''Associate with geo_string formatting.'''
    pass


class InvalidError(Error):
    '''Associate with invalid, impossible geo_strings.'''
    pass


class KeyError(Error):
    pass


class NotImplementedError(Error):
    pass


class IndeterminateError(Error):
    '''Associate with INDET exceptions.

    See Also
    --------
    - "More on IndeterminateError" in the documentation.

    '''
    pass

# -----------------------------------------------------------------------------
'''General classes for a custom exceptions.'''


class Error(Exception):
    pass


class FormatError(Error):
    '''Associate with geo_string formatting.'''
    pass


class KeyError(Error):
    pass


class NotImplementedError(Error):
    pass


class IndeterminateError(Error):
    '''Associate with INDET exceptions.'''
    pass

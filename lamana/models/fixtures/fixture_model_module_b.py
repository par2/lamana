#------------------------------------------------------------------------------
'''Module

This fixture is used to test the importing of models, handled by the
`theories.handshake()` module.  These are mostly dummy classes used to provoke errors.

No more than one hook method is allowed per module.

'''
from ...theories import BaseModel
# from lamana.theories import BaseModel

class OneMethod(BaseModel):
	def _use_model_():
		pass
	pass


class ManyMethods(BaseModel):
	def _use_model_():
		pass

	def method2():
		pass
	pass

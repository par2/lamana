#------------------------------------------------------------------------------
'''Module

This fixture is used to test the importing of models, handled by the
`theories.handshake()` module.  These are mostly dummy classes used to provoke errors.

'''
class OneMethod():
	'''No hook method.'''
	def method1():
		pass
	pass

class ManyMethods():
	'''No hook method.'''
	def method1():
		pass
	
	def method2():
		pass
	pass

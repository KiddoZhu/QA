import time

class Timer(object) :	
	def __init__(self, continuous = False) :
		self.start_time = time.time()
		self.continuous = continuous
	
	def __float__(self) :
		result = time.time() - self.start_time
		if not self.continuous :
			self.start_time = time.time()
		return result

def function_timer(func) :
	
	def _function(*args, **kargs) :
		time = Timer()
		result = func(*args, **kargs)
		print "%s(): %.2f s" % (func.__name__, time)
		return result

	return _function

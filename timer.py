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

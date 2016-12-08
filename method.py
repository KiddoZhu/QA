try :
	import cPickle as pickle
except :
	import pickle

class Method(object) :

	def __init__(self, database = None) :
		if database :
			self.database = database
	
	def load_data(self, filename) :
		self.database = Database(filename)
	
	def save(self, filename) :
		if hasattr(self, "database") :
			print "'%s' is not invoked, ignore save()." % self.__class__.__name__
			return
		pickle.dump(self, open(filename, "w"))
	
	@staticmethod
	def load(filename) :
		return pickle.load(open(filename))

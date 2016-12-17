import jieba
import pickle
import numpy as np
from gensim.models import Word2Vec as _Word2Vec, LdaModel as _LDA
from sklearn.metrics.pairwise import cosine_similarity

from method import Method
from timer import function_timer

class Word2Vec(Method) :

	def __init__(self, *args, **kargs) :
		super(Word2Vec, self).__init__(*args, **kargs)
		self.config = {"min_count": 1, "size": 100, "window": 10, "iter": 20};

	@function_timer
	def train(self, **kargs) :
		self.config.update(kargs)
		self.model = _Word2Vec(list(self.database.sentences), **self.config)
		delattr(self, "database")
	
	def __getitem__(self, item) :
		if isinstance(item, unicode) or isinstance(item, str) :
			return self.word(item)
		elif hasattr(item, "__iter__") :
			return self.sentence(item)
		else :
			raise ValueError("Item must be either word in unicode/str or sentence in list.")
	
	def word(self, word) :
		return self.model[word]
	
	def sentence(self, sentence) :
		vector = 0
		count = 0
		for word in sentence :
			if word in self.model :
				vector += self.model[word]
				count += 1
		return vector / count

	@staticmethod
	def similarity(v1, v2) :
		return cosine_similarity(v1, v2)

class LDA(Method) :
	def __init__(self, *args, **kargs) :
		super(LDA, self).__init__(*args, **kargs)
		self.config = {"num_topics": 100}
	
	@function_timer
	def train(self, **kargs) :
		self.config.update(kargs)
		self.model = _LDA(self.database.corpus, id2word = self.database.dictionary, **self.config)
		delattr(self, "database")
	
	def __getitem__(self, item) :
		if isinstance(item, unicode) or isinstance(item, str) :
			return self.word(item)
		elif hasattr(item, "__iter__") :
			return self.sentence(item)
		else :
			raise ValueError("Item must be either word in unicode/str or sentence in list.")
	
	def word(self, word) :
		assert(word in self.model.id2word.values())
		return self.sentence([word])
	
	def sentence(self, sentence) :
		result = np.zeros(self.model.num_topics)
		pairs = self.model[self.model.id2word.doc2bow(sentence)]
		for idx, val in pairs :
			result[idx] = val
		return result
	
	@staticmethod
	def similarity(v1, v2) :
		return cosine_similarity(v1, v2)
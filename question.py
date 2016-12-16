import jieba
from nltk.parse.stanford import StanfordDependencyParser

JAR_PATH = "stanford-parser/stanford-parser.jar"
MODELS_PATH = "stanford-parser/stanford-parser-3.6.0-models.jar"

class Question(object) :
	# Zhu: here you can add more attribute
	__slots__ = ["type", "keyword"]
	
	def __init__(self, **kargs) :
		for k, v in kargs.items() :
			setattr(self, k, v)

class QuestionExtractor(object) :

	parser = StanfordDependencyParser()	
	
	def __call__(self, question) :
		assert(isinstance(question, str))
		words = jieba.cut(question)
		dependency = parser.parse(words).next()
		
		# Zhu: here insert your rules
		
		# e.g.
		if True :
			return Question(type = "what", keyword = words[0])
		else :
			return Question(type = "when", keyword = words[0])

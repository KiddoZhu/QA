#coding=utf-8

import jieba
import jieba.posseg as pseg
import jieba.analyse 
from nltk.parse.stanford import StanfordDependencyParser

# JAR_PATH = "stanford-parser/stanford-parser.jar"
# MODELS_PATH = "stanford-parser/stanford-parser-3.6.0-models.jar"

'''
# Three ways to determine answers:
	1. get question type and then we could know answer type
	2. get question regularize equation and match words at the target sentence
	3. use key word marching, suppose key words in the target sentence
'''

class Question(object) :
	# Zhu: here you can add more attribute
	# __slots__ = ["type", "keyword"]
	pass
	def __init__(self, **kargs) :
		for k, v in kargs.items() :
			setattr(self, k, v)
		self.answerWordsList = []



def getQuestionType(wordsToken):
	numberToken = [u'第几', u'多少', u'几大']
	whatToken = [u'什么', u'哪个', u'哪一', u'哪所', u'哪种']
	whoToken = [u'谁' ]
	whereToken = [u'哪里']

	for word in wordsToken:
		# print word
		if word in whatToken:
			print 'What Question'
			return 'What',['n']
		if word in numberToken:
			print 'Number Question'
			return 'Number', ['m']
		if word in whoToken:
			print 'Who Question'
			return 'Who', ['nr']
		if word in whereToken:
			print 'where question'
			return 'Where', ['ns']
	return 'Unknown', []

def getAnswerRe(pos, sentence):
	print 'getAnswerRe.....'






class QuestionExtractor(object) :

	# parser = StanfordDependencyParser()	
	
	def __call__(self, question) :
		# print(question.questionSentence)
		qSentence = question.questionSentence
		assert(isinstance(qSentence, str))

		question.wordsToken = jieba.cut(qSentence)
		question.posToken = pseg.cut(qSentence)
		question.keyWordToken = jieba.analyse.extract_tags(qSentence, topK=5)
		print ' '.join(question.keyWordToken)
		# dependency = parser.parse(words).next()
		print '/'.join(question.wordsToken)
		for word, flag in question.posToken:
			print('%s %s'%(word, flag))

		question.questionTypem question.answerType = getQuestionType(question.wordsToken)
		# question.answerType = getAnswerType(question.questionType)
		question.answerRe = getAnswerRe(question.posToken, question.questionSentence)




def matchAnswerWords(q, s):
	print 'matchining'

def main():
	s = '《华英字典》的作者是？'
	question = Question(questionSentence=s)
	# setattr(question, 'questionSentence', '马尔代夫的第一大支柱产业是什么？')
	extractor = QuestionExtractor()
	extractor(question)
	targetSentence = '《华英字典》的作者是马礼逊'
	matchAnswerWords(question, targetSentence)

main()
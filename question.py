#coding=utf-8

import jieba
import jieba.posseg as pseg
import jieba.analyse 
from nltk.parse.stanford import StanfordDependencyParser
import codecs
import re
import sys
from help_func import *
# import debugger
# reload(sys)
# sys.setdefaultencoding('unicode')
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
	
	def setSentence(self, s):
		assert(isinstance(s, unicode))
		splitS = re.split(u'？|\t', s)
		if len(splitS) == 1:
			print 'no ? char'
		s = splitS[0]
		self.questionSentence = s

	#Replace answer keyword
	def addReKeyword(self, keyWord):
		if self.questionSentence.find(keyWord) == -1:
			return False
		if keyWord not in list(self.wordsToken):
			return False
		pattern = [w.replace(keyWord, u'<any>') for w in self.wordsToken]
		self.addTemp(pattern)
		pattern = []
		for w in self.wordsToken:
			if w == keyWord:
				break
			pattern.append(w)
		pattern.append(u'<any>')
		self.addTemp(pattern)
		return True

	def addTemp(self, r):
		if not hasattr(self, 'answerTemp'):
			setattr(self, 'answerTemp', [])
		self.answerTemp.append(r)

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



def getAnswerTemp(q):
	sentence = q.questionSentence
	# find keyword matching
	keyWordMatching = [u'多少', u'几', u'谁', u'什么', 
						u'哪个', u'哪一', u'哪所', u'哪种',
						u'哪里', u'第几']
	isWords = [u'是', u'成为', u'变成', u'由']
	whereWords = [u'哪里', u'在哪', u'哪一']
	for word in keyWordMatching:
		q.addReKeyword(word)
	
	# some representative words we want to march
	for w in isWords:
		if w in q.wordsToken:
			for w_is in isWords:
				i = q.wordsToken.index(w)
				before = q.wordsToken[:i]
				pattern = [u'<any>', w_is]
				pattern.extend(before)
				q.addTemp(pattern)
				pattern = [u'<any']
				pattern.extend(before)
				q.addTemp(pattern)
				before.extend([w_is, u'<any>'])
				q.addTemp(before)
				# ignore sentence before ','
				if sentence.find(u'，') != -1:
					i_comma = sentence.rfind(u'，')
					before_comma = sentence[:i_comma]
					before_is = sentence[i_comma+1: sentence.rfind(w_is)]
					before_comma = list(jieba.cut(before_comma))
					before_is = list(jieba.cut(before_is))
					before_comma.extend(before_is).extend([w_is, u'<any>'])
					q.addTemp(before_comma)
					
					before_comma = sentence[:i_comma]
					before_comma = list(jieba.cut(before_comma))
					before_comma.extend([u'<any>', w_is]).extend(before_is)
					q.addTemp(before_comma)
	
	if u'哪里' in q.wordsToken:
		i = q.wordsToken.index(u'哪里')
		before = q.wordsToken[:i]
		after = q.wordsToken[i+1:]
		if len(after) == 0:
			pattern = [u'在', '<any>']
			pattern.extend(before)
			q.addTemp(pattern)
			pattern = [u'位于', '<any>']
			pattern.extend(before)
			q.addTemp(pattern)
			





class QuestionExtractor(object) :

	# parser = StanfordDependencyParser()	
	
	def __call__(self, question) :
		# print(question.questionSentence)
		qSentence = question.questionSentence
		# assert(isinstance(qSentence, str))

		question.wordsToken = list(jieba.cut(qSentence))
		question.posToken = list(pseg.cut(qSentence))
		question.keyWordToken = list(jieba.analyse.extract_tags(qSentence, topK=5))
		print ' '.join(question.keyWordToken)
		# dependency = parser.parse(words).next()
		print '/'.join(question.wordsToken)
		# for word, flag in question.posToken:
		# 	print('%s %s'%(word, flag))

		question.questionType, question.answerType = getQuestionType(question.wordsToken)
		getAnswerTemp(question)
		my_print(question.answerTemp)
		# print question.answerRe




def matchAnswerWords(q, s):
	# print 'matchining'
	oriSent = q.questionSentence
	tarSent = s
	# print oriSent
	# print tarSent


def doall(s):
	# s = u'马尔代夫的第一大支柱产业是什么？	旅游业'
	question = Question()
	question.setSentence(s)
	# setattr(question, 'questionSentence', '马尔代夫的第一大支柱产业是什么？')
	extractor = QuestionExtractor()
	extractor(question)
	print 'ALL the Templete'
	my_print(question.answerTemp)
	#targetSentence = u'《华英字典》的作者是马礼逊'
	#matchAnswerWords(question, targetSentence)

def posText():
	textName = 'test.txt'
	f = codecs.open(textName, 'r', 'utf-8')
	#while True:
	#	line = f.readline()
	#	if not line:
	#		break
		# print line
	sampleQuestions = [u'甲午战争后，清政府签订了哪个不平等条约',
		u'马尔代夫的第一大支柱产业是什么？',
		u'《华英字典》的作者是？',
		u'甲午战争爆发的标志是？',
		]
	for q in sampleQuestions:
		doall(q)



posText()
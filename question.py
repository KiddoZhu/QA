#coding=utf-8

import jieba
import jieba.posseg as pseg
import jieba.analyse 
from nltk.parse.stanford import StanfordDependencyParser
import codecs
import re
import sys
import logging
from help_func import *
import debugger
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
		patternPos = []
		patternW = []
		for i in range(len(self.wordsToken)):
			if self.wordsToken[i] == keyWord:
				patternPos.append(self.answerType)
			patternPos.append(self.posToken[i])
			if self.wordsToken[i] in self.keyWordToken:
				patternW.append(5)
			else:
				patternW.append(1)

		self.addTemp(pattern, patternPos, patternW)

		pattern = []
		patternPos = []
		patternW = []
		for i in range(len(self.wordsToken)):
			if self.wordsToken[i] == keyWord:
				break
			pattern.append(self.wordsToken[i])
			patternPos.append(self.posToken[i])
			if self.wordsToken[i] in self.keyWordToken:
				patternW.append(5)
			else:
				patternW.append(1)
		pattern.append(u'<any>')
		patternPos.append(self.answerType)
		patternW.append(1)
		self.addTemp(pattern, patternPos, patternW)
		return True

	def addTemp(self, r, r_pos, r_w):
		if not hasattr(self, 'answerTemp'):
			setattr(self, 'answerTemp', [])
		if not hasattr(self, 'answerTempPos'):
			setattr(self, 'answerTempPos', [])
		if not hasattr(self, 'answerTempW'):
			setattr(self, 'answerTempW', [])
		assert(len(r) == len(r_pos), 'Not equal length of pattern and patten pos')
		assert(len(r_pos) == len(r_w), 'Not equal length of patternPos and pattern weight')

		self.answerTemp.append(r)
		self.answerTempPos.append(r_pos)
		self.answerTempW.append(r_w)
	def getAnswerTemp(self):
		sentence = self.questionSentence
		# find keyword matching
		keyWordMatching = [u'多少', u'几', u'谁', u'什么', 
							u'哪个', u'哪一', u'哪所', u'哪种',
							u'哪里', u'第几', u'哪']
		isWords = [u'是', u'成为', u'变成', u'由']
		whereWords = [u'哪里', u'在哪']
		for word in keyWordMatching:
			self.addReKeyword(word)
		
		# some representative words we want to match
		for w in isWords:
			if w in self.wordsToken:
				i = self.wordsToken.index(w)
				before = self.wordsToken[:i]
				beforePos = self.posToken[:i]
				beforeW = []
				for j in range(i):
					if self.wordsToken[j] in self.keyWordToken:
						beforeW.append(5)
					else:
						beforeW.append(1)
				# <any> is what?
				pattern = [u'<any>', w] + before
				patternPos = [self.answerType, 'v'] + beforePos
				patternW = [1,1] + beforeW
				self.addTemp(pattern, patternPos, patternW)
				# <any> what?
				pattern = [u'<any>'] + before
				patternPos = [self.answerType] + beforePos
				patternW = [1] + beforeW
				self.addTemp(pattern, patternPos, patternW)
				# what is <any>?
				pattern = before + [w, '<any>']
				patternP = beforePos + ['v', self.answerType]
				patternW = beforeW + [1,1]
				self.addTemp(pattern, patternPos, patternW)			
				# ignore sentence before ','
				if sentence.find(u'，') != -1:
					i_comma = sentence.rfind(u'，')
					before_comma_s = sentence[:i_comma]
					print before_comma_s
					before_is_s = sentence[i_comma+1: sentence.rfind(w)]
					before_comma, before_comma_pos = getPosToken(before_comma_s)
					before_is, before_is_pos = getPosToken(before_is_s)
					before_comma_w = []
					before_is_w = []
					for i in range(len(before_comma)):
						if before_comma[i] in self.keyWordToken:
							before_comma_w.append(5)
						else:
							before_comma_w.append(1)
					for i in range(len(before_is)):
						if before_is[i] in self.keyWordToken:
							before_is_w.append(5)
						else:
							before_is_w.append(1)				
					
					pattern = before_comma + before_is + [w, u'<any>']
					patternPos = before_comma_pos + before_is_pos + ['v', self.answerType]
					patternW = before_comma_w + before_is_w + [1,1]
					self.addTemp(pattern, patternPos, patternW)
					
					pattern = before_comma + [u'<any>', w]  + before_is
					patternPos = before_comma_pos + [self.answerType, 'v'] + before_is_pos
					patternW = before_comma_w + [1,1] + before_is_w
					self.addTemp(pattern, patternPos, patternW)				
		
		for w in whereWords:
			if w in self.wordsToken:
				i = self.wordsToken.index(w)
				before = self.wordsToken[:i]
				after = self.wordsToken[i+1:]
				beforePos = self.posToken[:i]
				afterPos = self.posToken[i+1:]
				beforeW = []
				afterW = []
				for j in range(len(before)):
					if before[j] in self.keyWordToken:
						beforeW.append(5)
					else:
						beforeW.append(1)
				for j in range(len(after)):
					if after[j] in self.keyWordToken:
						afterW.append(5)
					else:
						afterW.append(1)
				if len(after) == 0:
					pattern = [u'在', '<any>'] + before
					patternPos = ['v', self.answerType] + beforePos
					patternW = [1,1] + beforeW
					self.addTemp(pattern, patternPos, patternW)
					pattern = [u'位于', '<any>'] + before
					patternPos = ['v', self.answerType] + beforePos
					patternW = [1,1] + beforeW
					self.addTemp(pattern, patternPos, patternW)

def getQuestionType(wordsToken):
	numberToken = [u'第几', u'多少', u'几大']
	whatToken = [u'什么', u'哪个', u'哪一', u'哪所', u'哪种']
	whoToken = [u'谁' ]
	whereToken = [u'哪里']
	for word in wordsToken:
		# print word
		if word in whatToken:
			print 'What Question'
			return 'What','n'
		if word in numberToken:
			print 'Number Question'
			return 'Number', 'm'
		if word in whoToken:
			print 'Who Question'
			return 'Who', 'nr'
		if word in whereToken:
			print 'where question'
			return 'Where', 'ns'
	return 'Unknown', 'n'


def getPosToken(s):
	wordPos = pseg.cut(s)
	pos = []
	words = []
	for word, f in wordPos:
		pos.append(f)
		words.append(word)
	# print pos
	return words, pos


class QuestionExtractor(object) :

	# parser = StanfordDependencyParser()	
	
	def __call__(self, question) :
		# print(question.questionSentence)
		qSentence = question.questionSentence
		# assert(isinstance(qSentence, str))

		# question.wordsToken = list(jieba.cut(qSentence))
		question.wordsToken, question.posToken = getPosToken(qSentence)

		# print question.posToken
		# # my_print(question.posToken)
		# print 'Length words Token = %d'%(len(question.wordsToken))
		# print 'Length pos token = %d'%(len(question.posToken))
		question.keyWordToken = list(jieba.analyse.extract_tags(qSentence, topK=5))
		# print ' '.join(question.keyWordToken)
		# dependency = parser.parse(words).next()
		# print '/'.join(question.wordsToken)
		# for word, flag in question.posToken:
		# 	print('%s %s'%(word, flag))

		question.questionType, question.answerType = getQuestionType(question.wordsToken)
		question.getAnswerTemp()
		# my_print(question.answerTemp)
		# print question.answerRe


def parseQuestion(s):
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
	return question

def posText():
	# textName = 'test.txt'
	# f = codecs.open(textName, 'r', 'utf-8')
	#while True:
	#	line = f.readline()
	#	if not line:
	#		break
		# print line
	sampleQuestions = [u'甲午战争后，清政府签订了哪个不平等条约',
		u'马尔代夫的第一大支柱产业是什么？',
		u'《华英字典》的作者是？',
		u'甲午战争爆发的标志是？',
		u'甲午战争后，清政府签订不平等条约是什么',
		u'元谋人化石发现于中国的哪一省份？',
		u'人类合成的第一种抗菌药是？',
		u'1916年至1927年，北京大学的校长是？',
		]
	for q in sampleQuestions:
		parseQuestion(q)

if __name__ == '__main__':
	posText()
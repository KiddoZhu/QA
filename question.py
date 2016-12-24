#coding=utf-8

import jieba
import jieba.posseg as pseg
import jieba.analyse
# from nltk.parse.stanford import StanfordDependencyParser

#ＴＯＤＯ地点的问题
import codecs
import re
import sys
import logging
# from help_func import *
import debugger

W_KEYWORD = 5
W_NORMAL = 1
W_ANY = 50
W_NUMBER = 15
W_DETAILNOUN = 10

'''
# Three ways to determine answers:
	1. get question type and then we could know answer type
	2. get question regularize equation and match words at the target sentence
	3. use key word marching, suppose key words in the target sentence
'''
def getPattern(sentence, sentenceKeyWord):
	pattern, patternPos = getPosToken(sentence)
	patternW = []
	for w in pattern:
		if w in sentenceKeyWord:
			patternW.append(W_KEYWORD)
		else:
			patternW.append(W_NORMAL)
	return pattern, patternPos, patternW

def replaceAnswerWord(sentence, keyWord, answerType, sentenceKeyWord):
	if sentence.find(keyWord) == -1:
		return False, [], [], []
	patternW = []
	i = sentence.find(keyWord)
	beforeKeyWord = sentence[:i]
	afterKeyWord = sentence[i+len(keyWord):]
	before, beforePos = getPosToken(beforeKeyWord)
	after, afterPos = getPosToken(afterKeyWord)
	for w in before:
		if w in sentenceKeyWord:
			patternW.append(W_KEYWORD)
		else:
			patternW.append(W_NORMAL)
	patternW.append(W_ANY)
	for w in after:
		if w in sentenceKeyWord:
			patternW.append(W_KEYWORD)
		else:
			patternW.append(W_NORMAL)
	return True, before + [u'<any>'] + after, beforePos + [answerType] + afterPos, patternW

class Question(object) :
	pass
	def __init__(self, **kargs) :
		for k, v in kargs.items() :
			setattr(self, k, v)
		self.answerWordsList = []
	def setSentence(self, s):
		assert(isinstance(s, unicode))
		s = s.strip('\r\n')
		splitS = re.split(u'？|\t', s)
		# if len(splitS) == 1:
		# 	print 'no ? char'
		# my_print(splitS)
		s = splitS[0]
		self.questionSentence = s
	#Replace answer keyword
	def addReKeyword(self, keyWord):
		findWords, pattern, patternPos, patternW = replaceAnswerWord(self.questionSentence,
		 						keyWord, self.answerType, self.keyWordToken)
		if not findWords:
			return False
		self.addTemp(pattern, patternPos, patternW)
		return True

	def addTemp(self, r, r_pos, r_w):
		#my_print(r)
		#my_print(r_pos)
		#my_print(r_w)
		if not hasattr(self, 'answerTemp'):
			setattr(self, 'answerTemp', [])
		if not hasattr(self, 'answerTempPos'):
			setattr(self, 'answerTempPos', [])
		if not hasattr(self, 'answerTempW'):
			setattr(self, 'answerTempW', [])
		assert(len(r) == len(r_pos))
		assert(len(r_pos) == len(r))
		for i in range(len(r)):
			if r_pos[i] == 'm' and r[i] != u'<any>':
				# print "Number pos"
				r_w[i] = W_NUMBER
			if r_pos[i].startswith('n') and len(r_pos[i]) > 1 and r[i] != u'<any>':
				# print 'DETAILED Noun'
				r_w[i] = W_DETAILNOUN
		self.answerTemp.append(r)
		self.answerTempPos.append(r_pos)
		self.answerTempW.append(r_w)

	def getAnswerTemp(self):
		sentence = self.questionSentence
		# find keyword matching
		keyWordMatching = [u'多少', u'几', u'谁', u'什么',
							u'哪个', u'哪一', u'哪所', u'哪种',
							u'哪里', u'哪一年', u'哪位',
							u'什么样', u'哪条', u'哪年', u'哪天',
							u'哪块大陆', u'哪些', u'哪位',
							u'怎么', u'哪部', u'哪篇',
							u'何时', u'何处', u'多重', u'多大', u'多长时间', u'何时', u'多长',
							u'多远', u'多快', u'如何', u'何年', u'多高', u'多宽']
		isWords = [u'是', u'成为', u'变成', u'由']
		whereWords = [u'哪里', u'在哪', u'地点是']
		locationWords = [u'在', u'位于', u'地点是']
		self.findKeyWord = False
		self.matchWord = ''
		for word in keyWordMatching:
			if self.addReKeyword(word):
				self.findKeyWord = True
				self.matchWord = word

		# if not keyWordFind:
		# 	print 'Not Find Keyword'
		# 	my_print(self.questionSentence)
		# some representative words we want to match

		for w in isWords:
			if w in self.wordsToken:
				i = self.wordsToken.index(w)
				before = self.wordsToken[:i]
				beforePos = self.posToken[:i]
				beforeW = []
				for j in range(i):
					if self.wordsToken[j] in self.keyWordToken:
						beforeW.append(W_KEYWORD)
					else:
						beforeW.append(W_NORMAL)
				# <any> is what?

				pattern = [u'<any>', w] + before
				patternPos = [self.answerType, 'v'] + beforePos
				patternW = [W_ANY, W_NORMAL] + beforeW
				# #my_print(pattern)
				# #my_print(patternPos)
				self.addTemp(pattern, patternPos, patternW)
				# <any> what?
				pattern = [u'<any>'] + before
				patternPos = [self.answerType] + beforePos
				patternW = [W_ANY] + beforeW
				self.addTemp(pattern, patternPos, patternW)
				pattern = before + [u'<any>']
				patternPos = beforePos + [self.answerType]
				patternW = beforeW + [W_ANY]
				self.addTemp(pattern, patternPos, patternW)
				# what is <any>?
				pattern = before + [w, '<any>']
				# #my_print(beforePos)
				patternPos = beforePos + ['v', self.answerType]
				# #my_print(patternP)
				patternW = beforeW + [W_NORMAL, W_ANY]
				self.addTemp(pattern, patternPos, patternW)
				# ignore sentence before ','
				if sentence.find(u'，') != -1:
					i_comma = sentence.rfind(u'，')
					before_comma_s = sentence[:i_comma]
					# print before_comma_s
					before_is_s = sentence[i_comma+1: sentence.rfind(w)]
					before_comma, before_comma_pos = getPosToken(before_comma_s)
					before_is, before_is_pos = getPosToken(before_is_s)
					before_comma_w = []
					before_is_w = []
					for i in range(len(before_comma)):
						if before_comma[i] in self.keyWordToken:
							before_comma_w.append(W_KEYWORD)
						else:
							before_comma_w.append(W_NORMAL)
					for i in range(len(before_is)):
						if before_is[i] in self.keyWordToken:
							before_is_w.append(W_KEYWORD)
						else:
							before_is_w.append(W_NORMAL)

					pattern = before_comma + before_is + [w, u'<any>']
					patternPos = before_comma_pos + before_is_pos + ['v', self.answerType]
					patternW = before_comma_w + before_is_w + [W_NORMAL, W_ANY]
					self.addTemp(pattern, patternPos, patternW)

					pattern = before_comma + [u'<any>', w]  + before_is
					patternPos = before_comma_pos + [self.answerType, 'v'] + before_is_pos
					patternW = before_comma_w + [W_ANY, W_NORMAL] + before_is_w
					self.addTemp(pattern, patternPos, patternW)

		for w in whereWords:
			if self.questionSentence.find(w) != -1:
				i = self.questionSentence.find(w)
				before = self.questionSentence[:i]
				after = self.questionSentence[i+len(w):]
				before, beforePos, beforeW = getPattern(before, self.keyWordToken)
				after, afterPos, afterW = getPattern(after, self.keyWordToken)
				for w_l in locationWords:
					pattern = [w_l, '<any>'] + before
					patternPos = ['v', self.answerType] + beforePos
					patternW = [W_NORMAL, W_ANY] + beforeW
					self.addTemp(pattern, patternPos, patternW)
					pattern = before + [w_l, '<any>']
					patternPos = beforePos +  ['v', self.answerType]
					patternW = beforeW +  [W_NORMAL, W_ANY]
					self.addTemp(pattern, patternPos, patternW)
					if len(after) != 0:
						pattern = [w_l, '<any>'] + before + after
						patternPos = ['v', self.answerType] + beforePos + afterPos
						patternW = [W_NORMAL, W_ANY] + beforeW + afterW
						self.addTemp(pattern, patternPos, patternW)
						pattern = before + after + [w_l, '<any>']
						patternPos = beforePos + afterPos + ['v', self.answerType]
						patternW = beforeW + afterW + [W_NORMAL, W_ANY]
						self.addTemp(pattern, patternPos, patternW)

		# if we did not find any words
		# if not hasattr(self, 'answerTempW'):
			# print "Donnot find asnwer templater"
			# my_print(self.questionSentence)
			# my_print(self.wordsToken)
		# In case we have direct answers
		pattern = self.wordsToken + [u'<any>']
		patternPos = self.posToken + [self.answerType]
		patternW = []
		for word in self.wordsToken:
			if word in self.keyWordToken:
				patternW.append(W_KEYWORD)
			else:
				patternW.append(W_NORMAL)
		patternW.append(W_ANY)
		self.addTemp(pattern, patternPos, patternW)

def getQuestionType(sentence):
	keyWordMatching = [	u'下一句', ]

	numberToken = [u'第几', u'多少', u'几', u'多远', u'多快', u'多高', u'多宽', u'哪一年',
	 			u'哪年', u'哪天', u'多大', u'多长时间', u'何年',  u'多重', u'何时',u'多长', ]
	whatToken = [u'什么', u'哪个', u'哪部', u'哪篇', u'哪一', u'哪条', u'哪种']
	whoToken = [u'谁', u'哪位', ]
	whereToken = [u'哪里', u'哪所', u'何处', u'哪块大陆',]

	for word in numberToken:
		if sentence.find(word) != -1:
			return 'Number', 'm'
	for word in whatToken:
		if sentence.find(word) != -1:
			return 'What', 'n'
	for word in whoToken:
		if sentence.find(word) != -1:
			return 'Who', 'nr'
	for word in whereToken:
		if sentence.find(word) != -1:
			return 'Where', 'ns'
	if sentence.endswith(u'年份是'):
		# print 'End With '
		# my_print(sentence)
		return 'Number', 'm'
	if sentence.endswith(u'年是'):
		return 'Number', 'm'
	if sentence.endswith(u'地点是'):
		return 'Where', 'ns'
	# print 'Not find keyword token'
	# my_print(sentence)
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

	def __call__(self, question) :
		# print(question.questionSentence)
		qSentence = question.questionSentence
		# question.wordsToken = list(jieba.cut(qSentence))
		question.wordsToken, question.posToken = getPosToken(qSentence)
		assert len(question.wordsToken) == len(question.posToken)
		# print 'Length words Token = %d'%(len(question.wordsToken))
		# print 'Length pos token = %d'%(len(question.posToken))
		question.keyWordToken = list(jieba.analyse.extract_tags(qSentence, topK=5))
		# print ' '.join(question.keyWordToken)
		# dependency = parser.parse(words).next()
		# print '/'.join(question.wordsToken)
		# for word, flag in question.posToken:
		# 	print('%s %s'%(word, flag))
		question.questionType, question.answerType = getQuestionType(question.questionSentence)
		question.getAnswerTemp()
		# my_print(question.answerTemp)
		# print question.answerRe

def parseQuestion(s):
	question = Question()
	question.setSentence(s)

	extractor = QuestionExtractor()
	extractor(question)
	# print 'ALL the Templete'
	#my_print(question.questionSentence)
	#my_print(question.wordsToken)
	# my_print(question.questionSentence)
	# my_print(question.answerTemp)
	# my_print(question.answerTempPos)
	# my_print(question.answerTempW)
	return question

def posText():
	# textName = 'questions.txt'
	# f = codecs.open(textName, 'r', 'utf-8')
	# while True:
	# 	line = f.readline()
	# 	if not line:
	# 		break
	# 	parseQuestion(line)
		# print line
	sampleQuestions = [
		u'甲午战争后，清政府签订了哪个不平等条约',
		u'马尔代夫的第一大支柱产业是什么？',
		u'《华英字典》的作者是？',
		u'甲午战争爆发的标志是？',
		u'甲午战争后，清政府签订不平等条约是什么',
		u'元谋人化石发现于中国的哪一省份？',
		u'人类合成的第一种抗菌药是？',
		u'1916年至1927年，北京大学的校长是？',
		u'《资治通鉴》的撰写一共耗时多少年？',
		u'《苏德互不侵犯条约》的签订地点是？',
		u'第一位获得菲尔兹奖的女性是？',
		u'目前市面上流通的主要人民币是第几套？',
		u'1858年，与清政府签订《天津条约》的国家是英法俄和那个国家',
		u'白果是哪种植物的果实',
		u'北宋“三苏”中，苏洵与苏轼的亲戚关系是什么'
		]
	for q in sampleQuestions:
		parseQuestion(q)

def getJiebaPos():
	s = '史上第一位获得菲尔兹奖的女性数学家MaryamMirzakhani'
	# my_print(zip(*pseg.cut(s)))
	s = '2004年夏季奥运会是在那个城市举办'
	# my_print(zip(*pseg.cut(s)))

if __name__ == '__main__':
	posText()
	# getJiebaPos()

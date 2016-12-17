#coding=utf-8

import re
import json
import jieba
import numpy as np

from method import Method

import debugger

INF = 100000000
STOPWORDS = u"。？！"

def EditDistance(tl1, tl2, w1 = None, w2 = None) :
	assert(isinstance(tl1, list))
	assert(isinstance(tl2, list))
	if w1 == None :
		w1 = np.ones(len(tl1), dtype = int)
	if w2 == None :
		w2 = np.ones(len(tl2), dtype = int)
	
	dist = np.ones((len(tl1)+1, len(tl2)+1), dtype = int) * INF
	dist[0][0] = 0
	for i in range(len(tl1)+1) :
		for j in range(len(tl2)+1) :
			if i > 0 :
				dist[i][j] = min(dist[i][j], dist[i-1][j] + w1[i-1])
			if j > 0 :
				dist[i][j] = min(dist[i][j], dist[i][j-1] + w2[j-1])
			if i > 0 and j > 0 :
				if tl1[i-1] == tl2[j-1] :
					dist[i][j] = min(dist[i][j], dist[i-1][j-1])
				else :
					dist[i][j] = min(dist[i][j], dist[i-1][j-1] + max(w1[i-1], w2[j-1]))
	
	return dist[-1][-1]

class Search(Method) :

	re_split = re.compile("|".join(STOPWORDS))

	@property
	def title2text(self) :
		if not hasattr(self, "_title2text") :
			self._title2text = dict((attrib["title"], text) for text, attrib in self.database)
		return self._title2text
	
	def extract(self, tokenlist) :
		assert(isinstance(tokenlist, list))
		n = len(tokenlist)
		result = []
		for i in range(n) :
			for j in range(i, n) :
				substr = "".join(tokenlist[i:j+1])
				if substr in self.title2text.keys() :
					result.append(substr)
		return result

	def answer(self, question) :
		tokenlist = list(jieba.cut(question))
		entries = self.extract(tokenlist)
		print "entries:", json.dumps(entries, ensure_ascii = False)
		for entry in entries :
			text = self.title2text[entry]
			sentences = self.re_split.split(text)
			scores = map(lambda s: EditDistance(tokenlist, list(jieba.cut(s))), sentences)
			rank = sorted(range(len(scores)), key = lambda r: scores[r])
			for idx in rank[:20] :
				if scores[idx] == INF :
					break
				print scores[idx], sentences[idx]

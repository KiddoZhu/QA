#coding=utf-8
import re
import json
import jieba
import numpy as np

from method import Method
from question import parseQuestion
from timer import function_timer

import debugger

INF = 100000000
STOPWORDS = u"。？！"
RANK = 20
IGNORE = set([u"的"])

def EditDistance(tl1, tl2, w1 = None, w2 = None) :
	assert(isinstance(tl1, list))
	assert(isinstance(tl2, list))
	if not set(tl1).intersection(tl2) :
		return [INF, u""]
	if w1 == None :
		w1 = np.ones(len(tl1), dtype = int)
	if w2 == None :
		w2 = np.ones(len(tl2), dtype = int)
	
	dist = np.ones((len(tl1)+1, len(tl2)+1), dtype = int) * INF
	ans = np.ones((len(tl1)+1, len(tl2)+1), dtype = int) * -1
	dist[0][0] = 0
	for i in range(len(tl1)+1) :
		for j in range(len(tl2)+1) :
			if i > 0 and tl1[i-1] == u"<any>" :
				if j > 0 and dist[i-1][j-1] < dist[i][j] :
					dist[i][j] = dist[i-1][j-1]
					ans[i][j] = j-1
			else : # a normal token
				if i > 0 and dist[i-1][j] + w1[i-1] < dist[i][j] :
					dist[i][j] = dist[i-1][j] + w1[i-1]
					ans[i][j] = ans[i-1][j]
				if j > 0 and dist[i][j-1] + w2[j-1] < dist[i][j]:
					dist[i][j] = dist[i][j-1] + w2[j-1]
					ans[i][j] = ans[i][j-1]
				if i > 0 and j > 0 :
					if tl1[i-1] == tl2[j-1] and dist[i-1][j-1] < dist[i][j] :
						dist[i][j] = dist[i-1][j-1]
						ans[i][j] = ans[i-1][j-1]
					elif dist[i-1][j-1] + max(w1[i-1], w2[j-1]) < dist[i][j] :
						dist[i][j] = dist[i-1][j-1] + max(w1[i-1], w2[j-1])
						ans[i][j] = ans[i-1][j-1]
	
	return [dist[-1][-1], tl2[ans[-1][-1]]]

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
				if substr in self.title2text.keys() and substr not in IGNORE :
					result.append(substr)
		return result
	
	@function_timer
	def answer(self, question_str) :
		question = parseQuestion(question_str)
		if not hasattr(question, "answerTemp") : # TODO
			return []
		entries = self.extract(list(jieba.cut(question_str)))
		print "entries:", json.dumps(entries, ensure_ascii = False)
		results = []
		for entry in entries :
			text = self.title2text[entry]
			sentences = self.re_split.split(text)
			entry_results = []
			for sentence in sentences :
				tmp_results = []
				for tokenlist in question.answerTemp :
					wtl = np.ones(len(tokenlist), dtype = int) * 5
					tmp_results.append(EditDistance(tokenlist, list(jieba.cut(sentence)), w1 = wtl))
				tmp_results.sort()
				if tmp_results[0][0] < INF :
					entry_results.append(tmp_results[0] + [sentence])
			entry_results.sort()
			results += entry_results[:RANK]
		results.sort()
		return results

if __name__ == "__main__" :
	import json
	q_str = u"甲午战争爆发的标志是？"
	a_str = u"丰岛海战是战争爆发的标志"
	tokenlists = parseQuestion(q_str)
	for tokenlist in tokenlists.answerTemp :
		print json.dumps(tokenlist, ensure_ascii = False)
		print json.dumps(EditDistance(tokenlist, list(jieba.cut(a_str))), ensure_ascii = False)

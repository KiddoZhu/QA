#coding=utf-8
import re
import json
import jieba
import numpy as np
from multiprocessing import Pool

from method import Method
from question import parseQuestion
from web import search
from timer import function_timer

import debugger

INF = 100000000
STOPWORDS = [u":", u",", u"\\.", u"，", u"。", u"？", u"！", u"\n"]
RANK = 50
IGNORE = set([u"的"])

def EditDistance(tl1, tl2, pos1 = None, pos2 = None, w1 = None, w2 = None) :
	assert(hasattr(tl1, "__getitem__"))
	assert(hasattr(tl2, "__getitem__"))
	assert(bool(pos1) == bool(pos2))
	if not set(tl1).intersection(tl2) :
		return [INF, u""]
	if w1 == None :
		w1 = np.ones(len(tl1), dtype = int)
	if w2 == None :
		w2 = np.ones(len(tl2), dtype = int)	
	if pos1 == None :
		pos1 = np.zeros(len(tl1))
		pos2 = np.zeros(len(tl2))
	dist = np.ones((len(tl1)+1, len(tl2)+1), dtype = int) * INF
	ans = np.ones((len(tl1)+1, len(tl2)+1), dtype = int) * -1
	dist[0][0] = 0
	for i in range(len(tl1)+1) :
		for j in range(len(tl2)+1) :
			if i > 0 and tl1[i-1] == u"<any>" :
				tmp = dist[i-1][j-1]
				if not pos2[j-1].startswith(pos1[i-1]) :
					if pos1[i-1][0] == pos2[j-1][0] :
						tmp += max(w1[i-1], w2[j-1]) / 2
					else :
						tmp += max(w1[i-1], w2[j-1])
				if j > 0 and tmp < dist[i][j] :
					dist[i][j] = tmp
					ans[i][j] = j-1
			else : # a normal token
				if i > 0 and dist[i-1][j] + w1[i-1] < dist[i][j] :
					dist[i][j] = dist[i-1][j] + w1[i-1] * 2
					ans[i][j] = ans[i-1][j]
				if j > 0 and dist[i][j-1] + w2[j-1] < dist[i][j]:
					dist[i][j] = dist[i][j-1] + w2[j-1] * 2
					ans[i][j] = ans[i][j-1]
				if i > 0 and j > 0 :
					tmp = dist[i-1][j-1]
					if tl1[i-1] != tl2[j-1] :
						tmp += max(w1[i-1], w2[j-1])
					if pos1[i-1] != pos2[j-1] :
						tmp += max(w1[i-1], w2[j-1])
					if tmp < dist[i][j] :
						dist[i][j] = tmp
						ans[i][j] = ans[i-1][j-1]
	
	return [dist[-1][-1], -len(tl2[ans[-1][-1]]), tl2[ans[-1][-1]]]

def entry_answer(question, sentences, length) :
	entry_results = set() # keep unique
	for i in range(len(sentences) - length + 1) :
		sentence = "".join(sentences[i : i + length])
		if not sentence : # empty sentence
			continue
		tmp_results = []
		for pattern, w1, pos1 in zip(question.answerTemp, question.answerTempW, question.answerTempPos) :
			tokenlist, pos2 = zip(*jieba.posseg.cut(sentence))
			tmp_results.append(EditDistance(pattern, tokenlist, pos1 = pos1, pos2 = pos2, w1 = w1))
		tmp_results.sort()
		if tmp_results[0][0] < INF :
			entry_results.add(tuple(tmp_results[0] + [sentence]))
	entry_results = list(entry_results)
	entry_results.sort()
	return entry_results[:RANK]
	
class Search(Method) :

	re_split = re.compile("|".join(STOPWORDS))
	re_empty = re.compile(r"[ \n]+")

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
	def answer(self, question_str, length = 1, open = False) :
		if question_str.endswith(u"？") or question_str.endswith(u"?") :
			question_str = question_str[:-1]
		question = parseQuestion(question_str)
		entries = self.extract(list(jieba.cut(question_str)))
		print "entries:", json.dumps(entries, ensure_ascii = False)
		processes = []
		pool = Pool(processes = 4)
		for entry in entries :
			text = self.title2text[entry]
			text = self.re_empty.sub("", text)
			sentences = self.re_split.split(text)
			for l in range(1, length + 1) :
				processes.append(pool.apply_async(entry_answer, (question, sentences, l)))
		if open :
			text = search(question_str)
			text = self.re_empty.sub("", text)
			sentences = self.re_split.split(text)
			f = lambda s : s.find(question_str) == -1 and s[-1] != u"？" and s[-1] != u"?"
			sentences = filter(f, sentences)
			for l in range(1, length + 1) :
				processes.append(pool.apply_async(entry_answer, (question, sentences, l)))
		pool.close()
		pool.join()
		results = set()
		for process in processes :
			results.update(process.get())
		results = list(results)
		results.sort()
		return results[:RANK]

if __name__ == "__main__" :
	'''
	import pickle
	db = pickle.load(open("dump/database-simplified.dump"))
	s = Search(db)
	results = s.answer(u"《资治通鉴》的撰写一共耗时多少年？", length = 2, open = True)
	for score, _, answer, sentence in results :
		# result = (score, sentence, answer)
		fout.write("%d\t%s\t%s\n" % (score, answer, sentence))
	'''
	q_str = u"《资治通鉴》的撰写一共耗时多少年？"
	question = parseQuestion(q_str)
	sentence = u"《资治通鉴》是编年体以时间为"
	for pattern, w1, pos1 in zip(question.answerTemp, question.answerTempW, question.answerTempPos) :
		tokenlist, pos2 = zip(*jieba.posseg.cut(sentence))
		print json.dumps(zip(pattern, pos1, w1), ensure_ascii=False)
		print json.dumps(zip(tokenlist, pos2), ensure_ascii=False)
		print json.dumps(EditDistance(pattern, tokenlist, pos1 = pos1, pos2 = pos2, w1 = w1), ensure_ascii=False)
#coding=utf-8

import codecs
import pickle
from data import Database
from search import Search
from embedding import Word2Vec

INPUT_FILE = "test.txt"
OPEN_MODE = True
USE_KNN = False

if __name__ == "__main__" :
	db = pickle.load(open("dump/database-simplified.dump"))
	
	fin = codecs.open(INPUT_FILE, "r", "utf-8")
	lines = map(lambda l: l.strip(), fin.readlines())
	fin.close()
	ids = []
	queries = []
	for line in lines :
		parts = line.strip().split()
		ids.append(parts[0])
		if INPUT_FILE.startswith("test") :
			queries.append(parts[1])
		else :
			queries.append(parts[0])
	
	if USE_KNN :
		search = Search(database = db)
		search.embedding = Word2Vec.load("dump/w2v-model-simplified.dump")
	else :
		search = Search(database = db)
		
	fout = codecs.open(INPUT_FILE + "-output.txt", "w", "utf-8")
	for id, query in zip(ids, queries) :
		results = search.answer(query, length = 2, open = OPEN_MODE)
		if results :
			score, _, answer, sentence = results[0]
			# result = (score, sentence, answer)
			fout.write("%s\t%s\n" % (id, answer))
		else :
			fout.write("%s\t%s\n" % (id, "none"))
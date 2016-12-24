#coding=utf-8

import codecs
from data import Database
from search import Search
from question import parseQuestion

if __name__ == "__main__" :
	#db = Database("data/zhwiki-extracted/", conditions = [
	#	Database.cond_length(50),
	#	Database.cond_title(lambda t: not t.startswith("Wikipedia:")),
	#	Database.cond_title(lambda t: not t.startswith("File:")),
	#	Database.cond_title(lambda t: not t.startswith("Draft:"))
	#])
	import pickle
	db = pickle.load(open("dump/database-simplified.dump"))
	
	fin = codecs.open("样例数据.txt", "r", "utf-8")
	lines = map(lambda l: l.strip(), fin.readlines())
	fin.close()
	queries = map(lambda l: l.split()[0], lines)
	
	fout = codecs.open("output.txt", "w", "utf-8")
	search = Search(db)
	for query in queries :
		fout.write("%s\n" % query);
		results = search.answer(query, length = 2, open = True)
		for score, _, answer, sentence in results :
			# result = (score, sentence, answer)
			fout.write("%d\t%s\t%s\n" % (score, answer, sentence))
		fout.write("---------------------------------\n")
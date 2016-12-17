#coding=utf-8

import codecs
from data import Database
from search import Search

if __name__ == "__main__" :
	db = Database("data/zhwiki-extracted/", conditions = [
		Database.cond_length(50),
		Database.cond_title(lambda t: not t.startswith("Wikipedia:")),
		Database.cond_title(lambda t: not t.startswith("File:")),
		Database.cond_title(lambda t: not t.startswith("Draft:"))
	])
	import pickle
	pickle.dump(db, open("dump/database-simplified.dump", "w"))
	
	fin = codecs.open("样例数据.txt", "r", "utf-8")
	lines = map(lambda l: l.strip(), fin.readlines())
	fin.close()
	queries = map(lambda l: l.split()[0], lines)
	
	import sys
	sys.stdout = open("output.txt")
	search = Search(db)
	for query in queries :
		print query
		search.answer(query)
		print "---------------------------------"

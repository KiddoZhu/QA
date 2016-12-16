#coding=utf-8
import jieba
import codecs
import pickle
import warnings

from data import Database
from graph import Graph
from method import Method
from embedding import Word2Vec, LDA
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_distances

from timer import function_timer
import debugger

def old_main() :
	pass
	#graph = Graph(db)
	#graph.undirected_graph
	#graph.save("dump/graph-zhwiki.dump")
	#for k in range(10, 501, 10) :
	#	cores = graph.k_core(k = k)
	#	print "k = %d, len(cores) = %d" % (k, len(cores))
	
	#w2v = Word2Vec(db)
	#w2v.train(workers = 64)
	#w2v.save("dump/w2v-zhwiki.dump")
	
	#lda = LDA(db)
	#lda.train()
	#lda.save("dump/lda2-zhwiki.dump")

@function_timer
def t2wv(db) :
	return dict((attrib["title"], model[jieba.cut(text)]) for text, attrib in db)
	
if __name__ == "__main__" :
	db = Database("data/zhwiki-extracted/", conditions = [
		Database.cond_length(50), 
		Database.cond_title(lambda t: not t.startswith("Wikipedia:")),
		Database.cond_title(lambda t: not t.startswith("File:")),
		Database.cond_title(lambda t: not t.startswith("Draft:"))
	])
	# 767125 loaded, 451657 filtered, 31997 fails

	
	model = Method.load("dump/lda-model.dump")
	title2topic = t2wv(db)
	pickle.dump(title2topic, open("dump/title2topic.dump", "w"))
	#title2wv = pickle.load(open("dump/title2wv.dump"))
	vectors = []
	id2title = {}
	for i, (t, v) in enumerate(title2topic.items()) :
		vectors.append(v)
		id2title[i] = t
	
	fin = codecs.open("样例数据.txt", "r", "utf-8")
	lines = map(lambda l: l.strip(), fin.readlines())
	fin.close()
	queries = map(lambda l: l[:l.find(u"？")], lines)
	
	import sys
	saved = sys.stdout
	sys.stdout = open("output.txt", "w")
	
	#knn = NearestNeighbors(n_neighbors = 10, metric = cosine_distances, n_jobs = 64)
	with warnings.catch_warnings() :
		warnings.filterwarnings("ignore", category = DeprecationWarning)
		#knn.fit(vectors)
		#pickle.dump(knn, open("dump/knn.dump", "w"))
		knn = pickle.load(open("dump/knn.dump"))
		q_distances, q_ids = knn.kneighbors([model[jieba.cut(query)] for query in queries])
	for query, distances, ids in zip(queries, q_distances, q_ids) :
		print query
		for title in map(lambda id: id2title[id], ids) :
			print title
		print "------------------------------"
	sys.stdout = saved
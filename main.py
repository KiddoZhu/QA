from data import Database
from graph import Graph
from embedding import Word2Vec, LDA
from sklearn.neighbors import NearestNeighbors

import debugger

if __name__ == "__main__" :
	db = Database("data/zhwiki-extracted/", conditions = [
			Database.cond_length(50), 
			Database.cond_title(lambda t: not t.startswith("Wikipedia:")),
			Database.cond_title(lambda t: not t.startswith("File:")),
			Database.cond_title(lambda t: not t.startswith("Draft:"))
		])
	# 767125 loaded, 451657 filtered, 31997 fails
	
	#graph = Graph(db)
	#graph.undirected_graph
	#graph.save("dump/graph-zhwiki.dump")

	#for k in range(10, 501, 10) :
	#	cores = graph.k_core(k = k)
	#	print "k = %d, len(cores) = %d" % (k, len(cores))
	
	
	
	#w2v = Word2Vec(db)
	#w2v.train(workers = 64)
	#w2v.save("dump/w2v-zhwiki.dump")
	
	lda = LDA(db)
	lda.train(workers = 64)
	lda.save("dump/lda-zhwiki.dump")
	
	embeddings = [lda[sentence] for sentence in db.sentences]
	knn = NearestNeighbors(n_neighbors = 10)
	knn.fit(embeddings)
	#print knn.k_neighbors(query, n_jobs = 64)
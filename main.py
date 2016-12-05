import json

from data import Database
from graph import Graph

import debugger

if __name__ == "__main__" :
	db = Database("data/zhwiki-extracted/", conditions = [
			Database.cond_length(50), 
			Database.cond_title(lambda t: not t.startswith("Wikipedia:")),
			Database.cond_title(lambda t: not t.startswith("File:")),
			Database.cond_title(lambda t: not t.startswith("Draft:"))
		])
	# 767125 loaded, 451657 filtered, 31997 fails
	graph = Graph(db)
	graph.undirected_graph
	graph.save("dump/graph-zhwiki.dump")

	for k in range(10, 501, 10) :
		cores = graph.k_core(k = k)
		print "k = %d, len(cores) = %d" % (k, len(cores))

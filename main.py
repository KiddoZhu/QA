import json

from data import Database
from graph import Graph

import debugger

if __name__ == "__main__" :
	db = Database("data/zhwiki-extracted/", conditions = [
			Database.cond_length(50), 
			Database.cond_title(lambda t: not t.startswith("Wikipedia:")),
			Database.cond_title(lambda t: not t.startswith("File:"))
		])
	# 767125 loaded, 451657 filtered, 31997 fails
	graph = Graph(db)
	#DG = graph.directed_graph
	UG = graph.undirected_graph
	#graph.save("dump/graph-zhwiki.dump")

	for k in range(10, 50, 10) :
		cores = graph.k_core(k = k)
		print json.dumps(cores, ensure_ascii = False)
	#db.save("dump/database-zhwiki.dump")

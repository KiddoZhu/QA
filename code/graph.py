from copy import deepcopy
from collections import defaultdict
from itertools import chain
from acora import AcoraBuilder

from data import Database
from method import Method
from timer import function_timer

def _dd_int() :
	return defaultdict(int)

def longest_match(matches) :
	from itertools import groupby
	from operator import itemgetter
	
	for pos, match_set in groupby(matches, itemgetter(1)) :
		yield max(match_set)

class Graph(Method) :

	@property
	@function_timer
	def directed_graph(self) :
		if not hasattr(self, "_directed_graph") :
			print "getting directed graph ..."
			
			graph = defaultdict(_dd_int)
			# Zhu: in my VM, build speed is about 1.4w entity / s
			ac = AcoraBuilder(*self.database.entities).build()
			
			# match consumes no time, compared to build
			for text, attrib in self.database :
				entities = zip(*longest_match(ac.finditer(text)))[0]
				for entity in set(entities) :
					if entity == attrib["title"] :
						continue
					graph[attrib["title"]][entity] += 1
			
			delattr(self, "database")
			self._directed_graph = graph
			
		return self._directed_graph
	
	@property
	def undirected_graph(self) :
		if not hasattr(self, "_undirected_graph") :
			directed = self.directed_graph
			graph = defaultdict(_dd_int)
			
			for u in directed :
				for v in directed[u] :
					graph[u][v] += directed[u][v]
					graph[v][u] += directed[u][v]
			self._undirected_graph = graph
			
		return self._undirected_graph
	
	def k_core(self, k) :
		graph = deepcopy(self.undirected_graph)
		new_cores = graph.keys()
		cores = None
		
		while cores != new_cores :
			cores = new_cores
			new_cores = []
			for core in cores :
				if len(graph[core]) < k :
					for neigh in graph[core] :
						graph[neigh].pop(core)
					graph.pop(core)
				else :
					new_cores.append(core)
		
		return cores

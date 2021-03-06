import sys
import os
import re
import pickle
import jieba
from langconv import Converter
from gensim.corpora import Dictionary
from xml.etree import ElementTree as et

class Database(list) :

	_re_split = re.compile("(?<=</doc>).*?(?=<doc)", flags = re.DOTALL)
	_re_ignore = re.compile("<br>")
	_xml_escape = [(" & ", " &amp; ")]
	_converter = Converter("zh-hans")
	
	@staticmethod
	def cond_length(length) :
		return lambda x: len(x[0]) > length
	
	@staticmethod
	def cond_title(condition) :
		return lambda x: condition(x[1]["title"])
	
	def __init__(self, database = None, conditions = []) :
		if isinstance(database, list) :
			super(Database, self).__init__(database)
		
		elif isinstance(database, str) :
			self.load_data(database, conditions = conditions)
		
	
	def load_data(self, path, conditions = []) :
		walk = os.walk(path)
		total = reduce(int.__add__, map(lambda t: len(t[2]), walk))
		count = 0
		success = 0
		filtered = 0
		fail = 0
		print "loading data from %s" % path
		
		self.entities = set()
		for dirpath, dirnames, filenames in os.walk(path) :
			for filename in filenames :
				fullname = os.path.join(dirpath, filename)
				xml_raw = open(fullname, "r").read()
				for xml in self._re_split.split(xml_raw) :
					xml = self._re_ignore.sub("", xml)
					for old, new in self._xml_escape :
						xml = xml.replace(old, new)
					
					try :
						e = et.fromstring(xml)
						if not isinstance(e.text, unicode) :
							e.text = e.text.decode()
						if not isinstance(e.attrib["title"], unicode) :
							e.attrib["title"] = e.attrib["title"].decode()
						e.text = self._converter.convert(e.text)
						for key in e.attrib :
							e.attrib[key] = self._converter.convert(e.attrib[key])
						data = (e.text, e.attrib)
						for condition in conditions :
							if not condition(data) :
								filtered += 1
								break
						else :
							success += 1
							self.append(data)
							self.entities.add(e.attrib["title"])
					except et.ParseError :
						fail += 1
					
				count += 1
				#if count >= 10 :
				#	break
				print "\rfiles: %d / %d" % (count, total),
				sys.stdout.flush()
		
		print "... %d loaded, %d filtered, %d fails" % (success, filtered, fail)
	
	@property
	def sentences(self) :
		# return tokenized sentences
		for text, attrib in self :
			yield list(jieba.cut(text))
	
	@property
	def dictionary(self) :
		# return gensim Dictionary
		if not hasattr(self, "_dictionary") :
			self._dictionary = Dictionary(self.sentences, prune_at = None)
		return self._dictionary
	
	@property
	def corpus(self) :
		# return sparse vectors for gensim models
		if not hasattr(self, "_corpus") :
			self._corpus = [self.dictionary.doc2bow(sentence) for sentence in self.sentences]
		return self._corpus
	
	def save(self, filename) :
		pickle.dump(self, open(filename, "w"))
	
	@staticmethod
	def load(filename) :
		return pickle.load(open(filename))

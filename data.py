import sys
import os
import re
import pickle
import jieba
import xml.etree.ElementTree as et


class Database(list) :

	_re_split = re.compile("(?<=</doc>).*?(?=<doc)", flags = re.DOTALL)
	_re_ignore = re.compile("<br>")
	_xml_escape = [(" & ", " &amp; ")]
	
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
				print "\rfiles: %d / %d" % (count, total),
				sys.stdout.flush()
		
		print "... %d loaded, %d filtered, %d fails" % (success, filtered, fail)
	
	def save(self, filename) :
		pickle.dump(self, open(filename, "w"))
	
	@staticmethod
	def load(filename) :
		return pickle.load(open(filename))

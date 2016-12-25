import codecs
from argparse import ArgumentParser

def ParseArgument() :
	parser = ArgumentParser(description = "file comparison")
	parser.add_argument("file1")
	parser.add_argument("file2")
	return parser.parse_args()

if __name__ == "__main__" :
	args = ParseArgument()
	lines1 = codecs.open(args.file1, "r", "utf-8").readlines()
	lines2 = codecs.open(args.file2, "r", "utf-8").readlines()
	assert(len(lines1) == len(lines2))
	count = 0
	for x, y in zip(lines1, lines2) :
		if x == y :
			count += 1
	print "%d / %d correct." % (count, len(lines1))
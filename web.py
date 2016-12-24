#coding=utf-8
import re
import codecs
from urllib2 import urlopen

url = {
	"Google" : "http://www.google.com.hk/search?lr=lang_zh-CN&q=%s",
	"Baidu" : "http://www.baidu.com/s?rn=50&wd=%s"
	}

#re_content = re.compile(r"<(?:a|p)(?: [^>]*?)?>(.*?)</\1>", re.DOTALL)
re_content = re.compile(r'<div class="c-abstract">(.*?)</div>', re.DOTALL)
re_span = re.compile(r'<span class=" newTimeFactor_before_abs m">.*?</span>', re.DOTALL)
re_pair_tag = re.compile(r"<(\w*)(?: [^>]*?)?>([^<]*)</\1>")
re_simple_tag = re.compile(r"<[^>]*?/>|<img src=[^>]*?>")

escaped = {"&nbsp;": " ", "&gt;": ">", "&amp;": "&", "&quot;": '"', "<br>": "\n"}

def search(question_str, engine = "Baidu") :
	if isinstance(question_str, unicode) :
		question_str = question_str.encode("utf-8")
	page = urlopen(url[engine] % question_str).read()
	content = [group for group in re_content.findall(page)]
	result = []
	for text in content :
		replaced = re_simple_tag.sub("", text)
		replaced = re_span.sub("", text)
		for k, v in escaped.items() :
			replaced = replaced.replace(k, v)
		text = None
		while replaced != text :
			text = replaced
			replaced = re_pair_tag.sub(r"\2", text)
		result.append(text.decode("utf-8"))
	return "\n".join(result)
	
if __name__ == "__main__" :
	search("“中华民族”一词最早由谁提出？")
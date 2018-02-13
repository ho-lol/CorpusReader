from corpusReaderk import *
import re
from nltk.corpus.util import LazyCorpusLoader
sejong = LazyCorpusLoader(
    'sejong', 
    SejongCorpusReader, 
    r'sj[a-z]+\d\d.txt',
    cat_file='cats.txt',
    encoding="utf8")
##f=open('abc.txt','r',encoding='utf8').read()
##sent=re.compile('(.+?)\n\n',re.DOTALL)
##remove_sentnum=[re.compile('# \d+ / \d+\n').sub('',i) for i in sent.findall(f)]
##print(remove_sentnum)
##for i in sent.findall(f):
##    remove_sentnum=re.compile('# \d+ / \d+\n').sub('',i)
##    print(remove_sentnum)

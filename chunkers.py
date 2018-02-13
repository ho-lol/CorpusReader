import nltk.tag
from nltk.chunk import ChunkParserI
from nltk.chunk.util import tree2conlltags, conlltags2tree
from nltk.tag import UnigramTagger, BigramTagger, ClassifierBasedTagger
from nltk.corpus import names, ieer, gazetteers


def chunk_trees2train_chunks(chunk_sents):
	tag_sents = [tree2conlltags(sent) for sent in chunk_sents]
	return [[((w,t),c) for (w,t,c) in sent] for sent in tag_sents]

def prev_next_pos_iob(tokens, index, history):
	word, pos = tokens[index]
	
	if index == 0:
		prevword, prevpos, previob = ('<START>',)*3
	else:
		prevword, prevpos = tokens[index-1]
		previob = history[index-1]
	
	if index == len(tokens) - 1:
		nextword, nextpos = ('<END>',)*2
	else:
		nextword, nextpos = tokens[index+1]
	
	feats = {
		'word': word,
		'pos': pos,
		'nextword': nextword,
		'nextpos': nextpos,
		'prevword': prevword,
		'prevpos': prevpos,
		'previob': previob
	}
	
	return feats

class ClassifierChunker(ChunkParserI):
	def __init__(self, train_sents, feature_detector=prev_next_pos_iob, **kwargs):
		if not feature_detector:
			feature_detector = self.feature_detector
		
		train_chunks = chunk_trees2train_chunks(train_sents)
		self.tagger = ClassifierBasedTagger(train=train_chunks,
			feature_detector=feature_detector, **kwargs)
	
	def parse(self, tagged_sent):
		if not tagged_sent: return None
		chunks = self.tagger.tag(tagged_sent)
		return conlltags2tree([(w,t,c) for ((w,t),c) in chunks])



if __name__ == '__main__':
            
            from nltk.corpus import treebank_chunk,conll2000
            from nltk import tokenize
            conll_train = conll2000.chunked_sents('train.txt')
            train_chunks = treebank_chunk.chunked_sents()
            a=ClassifierChunker(conll_train)
            sentense = "I am a boy."
            tokens = nltk.word_tokenize(sentense)
            tagged = nltk.pos_tag(tokens)
            print(tagged)
            print(a.parse(tagged))

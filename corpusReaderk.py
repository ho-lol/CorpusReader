from nltk.corpus.reader.tagged import *
from nltk.tokenize import *
class CategorizedTaggedCorpusReaderK(CategorizedCorpusReader,
                                     TaggedCorpusReader):
    def __init__(self, *args, **kwargs):
        """
        Initialize the corpus reader.  Categorization arguments
        (``cat_pattern``, ``cat_map``, and ``cat_file``) are passed to
        the ``CategorizedCorpusReader`` constructor.  The remaining arguments
        are passed to the ``TaggedCorpusReader``.
        """
        CategorizedCorpusReader.__init__(self, kwargs)
        TaggedCorpusReader.__init__(self, *args, **kwargs)
        self._raw_fileids=[fileid for fileid in self.fileids() if 'sjr' in fileid]
        self._tagm_fileids=[fileid for fileid in self.fileids() if 'sjtm' in fileid]
        self._morph_fileids=[fileid for fileid in self.fileids() if 'sjm' in fileid]
        self._word_tokenizer=RegexpTokenizer('[\n\r]+|@SP@',gaps=True)
        self._tag_tokenizer=RegexpTokenizer('[\n\r]+|\++|@SP@',gaps=True)

    def _resolve(self, fileids, categories):
        if fileids is not None and categories is not None:
            raise ValueError('Specify fileids or categories, not both')
        if categories is not None:
            return self.fileids(categories)
        else:
            return fileids
        
    def raw(self, fileids=None, categories=None):
        return TaggedCorpusReader.raw(
            self, self._resolve(self._raw_fileids, categories))
    def morphs(self, fileids=None, categories=None):
        self._sep=''
        self._word_tokenizer=self._word_tokenizer
        return TaggedCorpusReader.words(
            self, self._resolve(self._morph_fileids, categories))
    def words(self, fileids=None, categories=None):
        self._sep=''
        self._word_tokenizer=self._word_tokenizer
        return TaggedCorpusReader.words(
            self, self._resolve(self._raw_fileids, categories))
    def sents(self, fileids=None, categories=None):
        return TaggedCorpusReader.sents(
            self, self._resolve(self._raw_fileids, categories))
    def paras(self, fileids=None, categories=None):
        return TaggedCorpusReader.paras(
            self, self._resolve(self._raw_fileids, categories))
    
    def tagged_morphs(self, fileids=None, categories=None):
        self._sep='/'
        self._word_tokenizer=self._tag_tokenizer
        return TaggedCorpusReader.tagged_words(
            self, self._resolve(self._tagm_fileids, categories))
    def tagged_words(self, fileids=None, categories=None, tagset=None):
        self._word_tokenizer=self._word_tokenizer
        self._sep=''
        return TaggedCorpusReader.tagged_words(
            self, self._resolve(self._tagm_fileids, categories))
    def tagged_sents(self, fileids=None, categories=None, tagset=None):
        self._sep='/'
        self._word_tokenizer=self._tag_tokenizer
        return TaggedCorpusReader.tagged_sents(
            self, self._resolve(self._tagm_fileids, categories), tagset)
    def tagged_paras(self, fileids=None, categories=None, tagset=None):
        self._word_tokenizer=self._tag_tokenizer
        return TaggedCorpusReader.tagged_paras(
            self, self._resolve(self._tagm_fileids, categories), tagset)

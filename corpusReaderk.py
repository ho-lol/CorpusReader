from nltk.corpus.reader.tagged import *
from nltk.tokenize import *


class SejongCorpusReader(CategorizedCorpusReader, TaggedCorpusReader):
    SPACE = " "

    def __init__(self, *args, **kwargs):
        """
        Initialize the corpus reader.  Categorization arguments
        (``cat_pattern``, ``cat_map``, and ``cat_file``) are passed to
        the ``CategorizedCorpusReader`` constructor.  The remaining arguments
        are passed to the ``TaggedCorpusReader``.
        """
        CategorizedCorpusReader.__init__(self, kwargs)
        TaggedCorpusReader.__init__(self, *args, **kwargs)
        self._raw_fileids = [fileid for fileid in self.fileids() if 'sjr' in fileid]
        self._tagm_fileids = [fileid for fileid in self.fileids() if 'sjt' in fileid]
        self._morph_fileids = [fileid for fileid in self.fileids() if 'sja' in fileid]
        self._word_tokenizer = RegexpTokenizer('[\n\r]+|' + self.SPACE, gaps=True)
        self._tag_tokenizer = RegexpTokenizer('[\n\r]+|\++|' + self.SPACE, gaps=True)

        ## 위에 파일아이디들도 스마트하게 바꿀수 있는 방
        ## 워드 토크나이저 태그 토크나이저 다 따로 재생성 하고 sep도 각 함수마다 다 따로 줫는데 이것을 좀더 스마트하게 바꾸는방법

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
        self._word_tokenizer = self._tag_tokenizer
        return TaggedCorpusReader.words(
            self, self._resolve(self._morph_fileids, categories))

    def words(self, fileids=None, categories=None):
        self._sep = ''
        return TaggedCorpusReader.words(
            self, self._resolve(self._raw_fileids, categories))

    def sents(self, fileids=None, categories=None):
        return TaggedCorpusReader.sents(
            self, self._resolve(self._raw_fileids, categories))

    def paras(self, fileids=None, categories=None):
        return TaggedCorpusReader.paras(
            self, self._resolve(self._raw_fileids, categories))

    def tagged_morphs(self, fileids=None, categories=None):
        self._sep = '/'
        self._word_tokenizer = self._tag_tokenizer
        return TaggedCorpusReader.tagged_words(
            self, self._resolve(self._tagm_fileids, categories))

    def tagged_words(self, fileids=None, categories=None, tagset=None):
        self._word_tokenizer = self._word_tokenizer
        self._sep = ''
        return TaggedCorpusReader.tagged_words(
            self, self._resolve(self._tagm_fileids, categories))

    def tagged_sents(self, fileids=None, categories=None, tagset=None):
        self._sep = '/'
        self._word_tokenizer = self._tag_tokenizer
        return TaggedCorpusReader.tagged_sents(
            self, self._resolve(self._tagm_fileids, categories), tagset)

    def tagged_paras(self, fileids=None, categories=None, tagset=None):
        self._word_tokenizer = self._tag_tokenizer
        return TaggedCorpusReader.tagged_paras(
            self, self._resolve(self._tagm_fileids, categories), tagset)

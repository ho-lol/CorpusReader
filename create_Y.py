import itertools
from pathlib import Path
import nltk
import os
import re
from difflib import SequenceMatcher


def create_maping(file):
    table = []
    with open(file, 'r') as fp:
        for line in fp.readlines():
            table.append(line.strip())
    return table



def pairwise(iterable: object) -> object:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    assert isinstance(b, object)
    return zip(a, b)


# def make_arrays(fnr, fnt):
#     _raw_array = []
#     _tagged_array = []
#     for line in open(fnr, 'r', encoding="utf8").readlines():
#         if line and not line.strip():
#             continue
#         _raw_array.append(line.split())
#     for line in open(fnt, 'r', encoding="utf8").readlines():
#         if line and not line.strip():
#             continue
#         _tagged_array.append(line.split())
#     return _raw_array, _tagged_array
#
#
# def split_word(morph_list, table):
#     return True


# def make_corpus(raw_array, tagged_array, table, file):
#     f = open(file,'w')
#     for raw_sent, tagged_sent in zip(raw_array, tagged_array):
#         if not len(raw_sent) == len(tagged_sent):
#             print(raw_sent,tagged_sent)
#             continue
#         result = []
#         for raw_word, tag_word in zip(raw_sent, tagged_sent):
#             tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", tag_word)
#             if not split_word(tag_morph, table):
#                 print(raw_word, file=f)
#             tagged = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])
#
#             if raw_word == tagged:
#                 for cur, nxt in pairwise(tag_morph):
#
#             else:
#                 SM = SequenceMatcher(None, raw_word, tagged)
#         print('\n',file=f)


def remove_num(data):
    return re.compile(r'__[0-9]+').sub('', data)


def split_fraction(path,  table, fpatten = 'sj[0-9][0-9]', encoding='utf8'):
    """

    :type fpatten: File pattern of Corpus
    """
    files = path.glob(fpatten)  ##glob 패턴이 이상함 sj\d+이 안된당

    for file in files:

        text = file.open(encoding=encoding).read()

        raw, tag_morphed, tag_all = [], [], []

        sent_rule = re.compile('(.+?)\n\n', re.DOTALL)
        del_sent_num_rule = re.compile('# \d+ / \d+\n')
        #word_morph_rule = re.compile(r'(?P<raw>.+)[ \t]+(?P<tag>.+)[\n]*')

        for sent in sent_rule.findall(text):
            del_sent_num = del_sent_num_rule.sub('', sent)
            tagged = re.split(r'\s+', del_sent_num)
            raw_temp = []
            tag_temp = []
            for i in range(0, len(tagged), 2):
                raw_word = tagged[i]
                tag_word = remove_num(tagged[i+1])
                tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", tag_word)
                # for cur, nxt in pairwise(tag_morph):
                #
                #         tagged_word = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])
                #         if raw_word == tagged:
                #
                #             pass
                #         else:
                #             SM = SequenceMatcher(None, raw_word, tagged)
                split_idx=[0]
                for i in range(0,len(tag_morph)-1):
                    cur = tag_morph[i]
                    nxt = tag_morph[i+1]
                    if cur[cur.rfind('/') + 1:] + ' ' + nxt[nxt.rfind('/') + 1:] in table:
                        split_idx.append(i+1)
                if len(split_idx) == 1:
                    raw_temp.append(raw_word)
                    tag_temp.append(tag_word)
                    continue

                tagged_word = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])
                if raw_word == tagged_word:
                    raw_idx=0
                    raw_len=0
                    for cur,nxt in pairwise(split_idx):
                        a = tag_morph[cur:nxt]
                        tag_temp.append("+".join(a))
                        for i in a:
                            raw_len = i.rfind('/')
                        raw_temp.append(raw_word[raw_idx:raw_len])
                        raw_idx = raw_len
                        raw_len = 0

                else:
                    split_morph=[]
                    morph_idx = 0
                    for cur,nxt in pairwise(split_idx):
                        for i in tag_morph[cur:nxt]:
                            morph_idx+=len(i[:i.rfind('/')])
                        split_morph.append(morph_idx)

                    SM = SequenceMatcher(None, raw_word, tagged_word)
                    split_raw=[]
                    for tag, i1, i2, j1, j2 in SM.get_opcodes():
                        if tag == "equal":
                            for i in split_morph:
                                if j1 <= i and j2 >= i:
                                    split_raw.append(i1+(i-j1))
                    split_morph.insert(0, 0)
                    split_raw.insert(0,0)
                    if len(split_morph) != len(split_raw):
                        print(split_morph,split_raw)
                        print(raw_word,tag_word)
                        raw_temp.append(raw_word)
                        tag_temp.append(tag_word)
                        continue
                    for cur,nxt in pairwise(split_raw):
                        raw_temp.append(raw_word[cur:nxt])
                    for cur,nxt in pairwise(split_idx):
                        a = tag_morph[cur:nxt]
                        tag_temp.append("+".join(a))





                    #
                    # for cur,nxt in pairwise(split_idx):
                    #     a = tag_morph[cur:nxt]
                    #     print("+".join(a))
                    #     tag_temp.append("+".join(a))
                    #     raw_sum = ''
                    #     for i in a:
                    #         raw_sum += i[:i.rfind('/')]
                    #     print(raw_sum)
                    #     raw_temp.append(raw_sum)

            raw.append(raw_temp)

            tag_morph.append(tag_temp)
            # raw.append([tagged[i] for i in range(0, len(tagged), 2)])
            #
            # tag_morphed.append([remove_num(tagged[i]) for i in range(1, len(tagged), 2)])
            #
            # tag_all.append([tagged[i] for i in range(1, len(tagged), 2)])


if __name__ == "__main__":
    table = create_maping("SP_TABLE.txt")
    curr_path = os.path.dirname(os.path.abspath(__file__))
    path = nltk.data.find('corpora\\sejong').path
    p = Path(path)
    assert isinstance(path, object)
    os.chdir(path)
    split_fraction(p, table)
    # files_raw = []
    # files_tagged = []
    #
    # for fn in os.listdir(path):
    #     assert isinstance(fn, object)
    #     if "sjr" in fn:
    #         files_raw.append(fn)
    #     elif "sjt" in fn:
    #         files_tagged.append(fn)
    #
    # # 테스트용 나중에 삭제바람
    # # files_raw = [files_raw[7]]
    # # files_tagged = [files_tagged[7]]
    # dic = {}
    # big = {}
    # raw_array = []
    # tagged_array = []
    # for i in range(len(files_raw)):
    #     temp_raw_array, temp_tagged_array = make_arrays(fnr=files_raw[i], fnt=files_tagged[i])
    #     raw_array = temp_raw_array
    #     tagged_array = temp_tagged_array
    #     print(str(i) + "리스트만들기 완료")
    #     make_corpus(raw_array, tagged_array, table)
    #     print(str(i) + "사전만들기완료")
    os.chdir(curr_path)
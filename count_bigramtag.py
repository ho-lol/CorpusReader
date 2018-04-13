import re
from typing import List, Any

import sejong
import itertools


def pairwise(iterable: object) -> object:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    assert isinstance(b, object)
    return zip(a, b)


def count_dict(dic, key):
    """

    :rtype: object
    """
    if dic.get(key):
        dic[key] += 1
    else:
        dic[key] = 1


def make_df_txt(dic, fn):
    with open(fn, 'w', encoding="utf8") as f:
        for k, v in dic.items():
            print(k, v, file=f)

def make_df(dic, fn="count_bigram.bin"):
    import pickle
    with open(fn, 'wb') as f:
        pickle.dump(dic, f)


def make_pair(sents):
    dic = {}
    for sent in sents:
        for phrase in sent:
            split_phrase = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", phrase)
            if len(split_phrase) == 1:
                temp: str = "".join(split_phrase)
                count_dict(dic,"@@SP@@ "+temp[temp.rfind('/'):])
            else:
                for cur, nxt in pairwise(split_phrase):
                    count_dict(dic,cur[cur.rfind('/'):]+" "+nxt[nxt.rfind('/'):])
    return dic


if __name__ == "__main__":
    result = {}
    sents: List[List[Any]] = []
    for i in sejong.sejong.tagged_phrase_sents():  # 만약에 tagged_phrase_sents가 잘바뀌면 이것도 필요없을듯
        sents.append([j[0] for j in i])
    result = make_pair(sents)
    # for cur, nxt in pairwise(sejong.sejong.tagged_morphs()):
    #     count_dict(result, cur[1] + " " + nxt[1])
    make_df(result)
    # make_df_txt(result, "count_bigramtag.txt")

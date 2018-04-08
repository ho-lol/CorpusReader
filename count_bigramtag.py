import sejong
import itertools


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def count_dict(dic, key):
    if dic.get(key):
        dic[key] += 1
    else:
        dic[key] = 1


def make_df(dic, fn):
    with open(fn, 'w', encoding="utf8") as f:
        for k, v in dic.items():
            print(k, v, file=f)


if __name__ == "__main__":
    result = {}
    for cur, nxt in pairwise(sejong.sejong.tagged_morphs()):
        count_dict(result, cur[1] + " " + nxt[1])
    make_df(result, "count_bigramtag.txt")

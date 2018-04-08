import re
import os
import glob
from pathlib import Path
from nltk.data import find
from os.path import basename


def remove_num(data):
    return re.compile(r'__[0-9]+').sub('', data)


def make_file(wfn, data, encoding='utf8'):
    with open(wfn, 'w', encoding=encoding) as f:
        print("\n\n" + "\n\n\n".join(" ".join(e) for e in data) + "\n\n\n", file=f)


def split_fraction(path, fpatten='sj[0-9][0-9]', encoding='utf8'):
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

            raw.append([tagged[i] for i in range(0, len(tagged), 2)])

            tag_morphed.append([remove_num(tagged[i]) for i in range(1, len(tagged), 2)])

            tag_all.append([tagged[i] for i in range(1, len(tagged), 2)])

        fr = re.sub('\D+', 'sjr', basename(os.path.join(str(file)))) + ".txt"
        ft = re.sub('\D+', 'sjt', basename(os.path.join(str(file)))) + ".txt"
        fa = re.sub('\D+', 'sja', basename(os.path.join(str(file)))) + ".txt"

        make_file(fr, raw)
        make_file(ft, tag_morphed)
        make_file(fa, tag_all)


if __name__ == "__main__":
    path_f = find("corpora\\sejong").path

    p = Path(path_f)

    os.chdir(os.path.join(path_f))
    # os.chdir(p) 3.6일때
    split_fraction(p)
